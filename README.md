# anki-audio-speed

Anki add-on: change the playback speed of card audio while reviewing, without changing its pitch.

- A slider next to the Edit button in the reviewer's bottom bar, 0.5×–1.5× in steps of 0.05.
- `8` slower, `9` faster, `0` back to 1.0×.
- Takes effect immediately, also on audio that is already playing; `r` replays at the set speed.
- Each new card starts at 1.0×. The answer side keeps the speed set on the question side.
  Leaving the reviewer resets to 1.0×.

It sets mpv's `speed` property, so it covers every `[sound:]` tag on every note type. While the
speed is off 1.0 it adds mpv's `scaletempo2` filter with a 40 ms window and search interval
(mpv's own default insertion uses 20 / 30 ms), which time-stretches without a pitch shift and
sounds cleaner on slowed TTS speech. At 1.0 the filter is removed and playback is untouched.
`<audio>` elements written into a card template are played by the card's web view, not mpv,
and are not covered.

Desktop only: AnkiMobile and AnkiDroid do not run add-ons. Needs mpv as the audio player
(Anki's default on all desktop platforms).

## Install

```bash
uv run python scripts/install.py
```

This builds `dist/anki_audio_speed.ankiaddon` and opens it with Anki. Confirm the install and
restart Anki. `uv run python scripts/build.py` only builds the file. Configure under Tools → Add-ons → Audio Speed → Config; see
[`config.md`](src/anki_audio_speed/config.md).

## Layout

- `speed.py` — rounding and clamping. No Anki imports.
- `__init__.py` — the hooks: mpv speed, reset per card, keys, the bottom-bar bridge.
- `web/` — the slider, injected into the reviewer's bottom bar.

## Development

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
```
