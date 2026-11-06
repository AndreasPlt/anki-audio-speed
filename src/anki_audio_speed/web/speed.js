/* Audio speed slider, placed after the Edit button of the reviewer's bottom bar. */
const audioSpeed = (() => {
  let input, label;
  const format = (value) => `${Number(value).toFixed(2)}×`;

  return {
    init({ min, max, step, value }) {
      input = Object.assign(document.createElement("input"), { type: "range", min, max, step, value });
      label = Object.assign(document.createElement("span"), { textContent: format(value) });
      input.addEventListener("input", () => {
        label.textContent = format(input.value);
        pycmd(`audiospeed:${input.value}`);
      });
      input.addEventListener("change", () => pycmd("audiospeed:done"));

      const box = Object.assign(document.createElement("span"), { id: "audio-speed", title: "Audio speed" });
      box.append(input, label);
      document.querySelector("#innertable td.stat").append(box);
    },

    show(value) {
      input.value = value;
      label.textContent = format(value);
    },
  };
})();
