"""Anki add-on: change the playback speed of card audio while reviewing.

A slider next to the reviewer's Edit button, and keys for slower / faster / normal, set the
speed of mpv, Anki's audio player. That covers every `[sound:]` on every note type. The pitch
is kept by a tuned scaletempo2 filter. Each new card starts at normal speed; its answer side
keeps the speed.

* :mod:`anki_audio_speed.speed` - rounding and clamping; no Anki imports.
"""

from __future__ import annotations

import json

from . import speed

try:  # pragma: no cover - only available inside Anki
    from aqt import gui_hooks, mw, sound
    from aqt.reviewer import ReviewerBottomBar
    from aqt.utils import tooltip
except ImportError:  # imported outside Anki (tests)
    gui_hooks = mw = sound = ReviewerBottomBar = tooltip = None

_PREFIX = "audiospeed:"
_current = speed.NORMAL

# Stands in for the scaletempo2 that mpv inserts by itself off 1.0: a 40 ms window and search
# interval (defaults 20 / 30) sounded cleaner on slowed TTS speech. In the chain only while the
# speed is off 1.0, so normal playback stays untouched.
_FILTER_LABEL = "audiospeed"
_FILTER = f"@{_FILTER_LABEL}:scaletempo2=window-size=40:search-interval=40"


def _config() -> dict:
    return mw.addonManager.getConfig(__name__) or {}


def _bounds() -> tuple[float, float, float]:
    config = _config()
    return (
        float(config.get("min", 0.5)),
        float(config.get("max", 1.5)),
        float(config.get("step", 0.05)),
    )


def _set(value: float) -> None:
    global _current
    _current = speed.snap(value, *_bounds())
    player = sound.mpvManager
    if player is None:
        if _current != speed.NORMAL:
            tooltip("Audio speed needs mpv, Anki's default audio player")
        return
    _apply(player, _current)
    if mw.state == "review":
        mw.bottomWeb.eval(f"audioSpeed.show({_current})")


def _apply(player, value: float) -> None:
    """Set mpv's speed (also for audio already playing) with our filter in place.

    The filter goes in before the speed leaves 1.0 and comes out after it is back, so mpv
    never inserts its own default one in between.
    """
    present = any(f.get("label") == _FILTER_LABEL for f in player.get_property("af"))
    if value == speed.NORMAL:
        player.set_property("speed", value)
        if present:
            player.command("af", "remove", f"@{_FILTER_LABEL}")
    else:
        if not present:  # checked each time: a restarted mpv comes back without it
            player.command("af", "add", _FILTER)
        player.set_property("speed", value)


def _on_bottom_bar(web_content, context) -> None:
    if not isinstance(context, ReviewerBottomBar):
        return
    base = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
    web_content.css.append(f"{base}/speed.css")
    web_content.js.append(f"{base}/speed.js")
    low, high, step = _bounds()
    options = json.dumps({"min": low, "max": high, "step": step, "value": _current})
    web_content.body += f"<script>audioSpeed.init({options});</script>"


def _on_message(handled: tuple, message: str, context) -> tuple:
    if not message.startswith(_PREFIX):
        return handled
    value = message[len(_PREFIX) :]
    if value == "done":
        mw.web.setFocus()  # back to the reviewer's keys
    else:
        _set(float(value))
    return True, None


def _on_shortcuts(state: str, shortcuts: list) -> None:
    if state != "review":
        return
    config = _config()
    step = _bounds()[2]
    shortcuts += [
        (config.get("slower_key", "8"), lambda: _set(_current - step)),
        (config.get("faster_key", "9"), lambda: _set(_current + step)),
        (config.get("normal_key", "0"), lambda: _set(speed.NORMAL)),
    ]


def _on_question(card, tags) -> None:
    _set(speed.NORMAL)  # runs before the question's audio starts


def _on_state(new_state: str, old_state: str) -> None:
    if old_state == "review":
        _set(speed.NORMAL)  # the browser's preview and the editor play at normal speed


if gui_hooks is not None:  # pragma: no cover - only inside Anki
    mw.addonManager.setWebExports(__name__, r"web/.*\.(css|js)")
    gui_hooks.webview_will_set_content.append(_on_bottom_bar)
    gui_hooks.webview_did_receive_js_message.append(_on_message)
    gui_hooks.state_shortcuts_will_change.append(_on_shortcuts)
    gui_hooks.reviewer_will_play_question_sounds.append(_on_question)
    gui_hooks.state_did_change.append(_on_state)
