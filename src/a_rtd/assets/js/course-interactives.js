(function () {
  "use strict";

  const CDN = {
    plotly: "https://cdn.plot.ly/plotly-3.3.1.min.js",
    pyodideIndex: "https://cdn.jsdelivr.net/pyodide/v0.29.4/full/",
    p5: "https://cdnjs.cloudflare.com/ajax/libs/p5.js/2.0.5/p5.min.js",
    jsxgraphCss: "https://cdn.jsdelivr.net/npm/jsxgraph@1.6.2/distrib/jsxgraph.css",
    jsxgraphJs: "https://cdn.jsdelivr.net/npm/jsxgraph@1.6.2/distrib/jsxgraphcore.js",
  };

  const loadedScripts = new Map();
  const examples = new Map();
  let controlIdCounter = 0;
  let pyodidePromise = null;
  let staticBaseUrl = null;

  function staticAssetUrl(path) {
    if (!staticBaseUrl) {
      const staticScript =
        document.currentScript ||
        [...document.scripts].find((script) => script.src.includes("/_static/"));

      if (staticScript && staticScript.src.includes("/_static/")) {
        staticBaseUrl = staticScript.src.slice(
          0,
          staticScript.src.indexOf("/_static/") + "/_static/".length
        );
      } else {
        staticBaseUrl = new URL("_static/", document.baseURI).href;
      }
    }

    return new URL(path.replace(/^\/+/, ""), staticBaseUrl).href;
  }

  function loadScript(src) {
    if (loadedScripts.has(src)) {
      return loadedScripts.get(src);
    }

    const promise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Could not load ${src}`));
      document.head.appendChild(script);
    });

    loadedScripts.set(src, promise);
    return promise;
  }

  function loadCss(href) {
    if ([...document.styleSheets].some((sheet) => sheet.href === href)) {
      return;
    }

    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  async function loadPlotly() {
    if (!window.Plotly) {
      await loadScript(CDN.plotly);
    }
    return window.Plotly;
  }

  async function loadPyodideRuntime() {
    if (!pyodidePromise) {
      pyodidePromise = loadScript(`${CDN.pyodideIndex}pyodide.js`).then(() =>
        window.loadPyodide({ indexURL: CDN.pyodideIndex })
      );
    }
    return pyodidePromise;
  }

  async function loadP5() {
    if (!window.p5) {
      await loadScript(CDN.p5);
    }
    return window.p5;
  }

  async function loadJsxGraph() {
    loadCss(CDN.jsxgraphCss);
    if (!window.JXG) {
      await loadScript(CDN.jsxgraphJs);
    }
    return window.JXG;
  }

  function numberFromDataset(element, key, fallback) {
    const value = Number(element.dataset[key]);
    return Number.isFinite(value) ? value : fallback;
  }

  function resizePlotlyPlot(plot, plotly) {
    if (!plot.isConnected || !plotly.Plots || !plotly.Plots.resize) {
      return;
    }

    window.requestAnimationFrame(() => plotly.Plots.resize(plot));
  }

  function renderPlotly(plotly, plot, data, layout, config = {}) {
    return plotly
      .react(
        plot,
        data,
        {
          autosize: true,
          ...layout,
        },
        {
          responsive: true,
          displayModeBar: false,
          ...config,
        }
      )
      .then(() => resizePlotlyPlot(plot, plotly));
  }

  function makeRangeControl({ label, min, max, step, value, onInput }) {
    const wrapper = document.createElement("div");
    wrapper.className = "course-interactive__control";

    const labelElement = document.createElement("label");
    const output = document.createElement("output");
    const input = document.createElement("input");

    input.type = "range";
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = String(value);
    input.id = `course-interactive-control-${controlIdCounter += 1}`;

    labelElement.htmlFor = input.id;
    function sync() {
      output.value = input.value;
      onInput(Number(input.value));
    }

    labelElement.append(label, " ", output);
    wrapper.append(labelElement, input);
    input.addEventListener("input", sync);
    sync();

    return wrapper;
  }

  function makeNumberInputControl({ label, min, max, step, value, onInput }) {
    const wrapper = document.createElement("div");
    wrapper.className = "course-interactive__control";

    const labelElement = document.createElement("label");
    const input = document.createElement("input");
    const message = document.createElement("div");

    input.type = "number";
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = String(value);
    input.inputMode = "decimal";
    input.id = `course-interactive-control-${controlIdCounter += 1}`;

    message.className = "course-interactive__message";
    labelElement.textContent = label;
    labelElement.htmlFor = input.id;

    function sync() {
      const nextValue = Number(input.value);
      const isValid =
        input.value.trim() !== "" &&
        Number.isFinite(nextValue) &&
        nextValue >= min &&
        nextValue <= max;

      if (!isValid) {
        input.setAttribute("aria-invalid", "true");
        message.textContent = `Enter a number from ${min} to ${max}.`;
        return;
      }

      input.removeAttribute("aria-invalid");
      message.textContent = "";
      onInput(nextValue);
    }

    wrapper.append(labelElement, input, message);
    input.addEventListener("input", sync);
    sync();

    return wrapper;
  }

  function makeSelectControl({ label, options, value, onInput }) {
    const wrapper = document.createElement("div");
    wrapper.className = "course-interactive__control";

    const labelElement = document.createElement("label");
    const select = document.createElement("select");

    labelElement.textContent = label;
    select.id = `course-interactive-control-${controlIdCounter += 1}`;
    labelElement.htmlFor = select.id;

    options.forEach((option) => {
      const optionElement = document.createElement("option");
      optionElement.value = String(option.value);
      optionElement.textContent = option.label;
      if (String(option.value) === String(value)) {
        optionElement.selected = true;
      }
      select.append(optionElement);
    });

    function sync() {
      onInput(select.value);
    }

    wrapper.append(labelElement, select);
    select.addEventListener("change", sync);
    sync();

    return wrapper;
  }

  function makeCheckboxControl({ label, checked, onInput }) {
    const wrapper = document.createElement("div");
    wrapper.className = "course-interactive__control";

    const labelElement = document.createElement("label");
    const input = document.createElement("input");
    const text = document.createElement("span");

    labelElement.className = "course-interactive__checkbox-label";
    input.type = "checkbox";
    input.checked = checked;
    input.id = `course-interactive-control-${controlIdCounter += 1}`;
    labelElement.htmlFor = input.id;
    text.textContent = label;

    function sync() {
      onInput(input.checked);
    }

    labelElement.append(input, text);
    wrapper.append(labelElement);
    input.addEventListener("input", sync);
    sync();

    return wrapper;
  }

  function registerExample(name, initializer) {
    examples.set(name, { initializer });
  }

  function findExample(element) {
    if (element.dataset.example && examples.has(element.dataset.example)) {
      return examples.get(element.dataset.example);
    }

    return null;
  }

  async function initInteractive(element) {
    const example = findExample(element);

    try {
      if (example) {
        await example.initializer(element);
        return;
      }

      element.textContent = `Unknown interactive example: ${element.dataset.example || "none"}`;
    } catch (error) {
      const message =
        error && error.userMessage
          ? error.userMessage
          : "This interactive example could not be loaded.";
      element.textContent = message;
      console.error(error);
    }
  }

  window.CourseInteractives = {
    loadJsxGraph,
    loadP5,
    loadPlotly,
    loadPyodideRuntime,
    makeCheckboxControl,
    makeNumberInputControl,
    makeRangeControl,
    makeSelectControl,
    numberFromDataset,
    registerExample,
    renderPlotly,
    resizePlotlyPlot,
    staticAssetUrl,
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".course-interactive").forEach(initInteractive);
  });
})();
