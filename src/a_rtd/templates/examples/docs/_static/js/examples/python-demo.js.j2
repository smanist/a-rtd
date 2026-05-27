(function () {
  "use strict";

  const {
    loadPlotly,
    loadPyodideRuntime,
    makeRangeControl,
    numberFromDataset,
    registerExample,
    renderPlotly,
    staticAssetUrl,
  } = window.CourseInteractives;

  let dampedSignalPromise = null;
  const dampedSignalSource = String.raw`import numpy as np


def damped_signal(frequency=2.0, damping=0.15, time_max=8.0, steps=320):
    """Return a small NumPy-backed signal for the template Pyodide demo."""
    t = np.linspace(0.0, float(time_max), int(steps) + 1)
    y = np.exp(-float(damping) * t) * np.cos(float(frequency) * t)
    envelope = np.exp(-float(damping) * t)

    return {
        "time": t.tolist(),
        "signal": y.tolist(),
        "upper": envelope.tolist(),
        "lower": (-envelope).tolist(),
    }
`;

  function loadError(step, error) {
    const message = error && error.message ? error.message : String(error);
    const wrapped = new Error(`${step}: ${message}`);
    wrapped.cause = error;
    wrapped.userMessage = `This interactive example could not be loaded. ${step}: ${message}`;
    return wrapped;
  }

  async function loadPythonSource() {
    const sourceUrl = staticAssetUrl("py/examples/python_demo.py");
    if (window.location.protocol === "file:") {
      return dampedSignalSource;
    }

    let response;
    try {
      response = await fetch(sourceUrl);
    } catch (error) {
      throw loadError(`Python source fetch failed (${sourceUrl})`, error);
    }
    if (!response.ok) {
      throw loadError(
        "Python source fetch failed",
        new Error(`${response.status} ${response.statusText}: ${sourceUrl}`)
      );
    }

    return response.text();
  }

  async function loadDampedSignalFunction() {
    if (!dampedSignalPromise) {
      dampedSignalPromise = (async () => {
        let pyodide;
        try {
          pyodide = await loadPyodideRuntime();
        } catch (error) {
          throw loadError("Pyodide runtime failed to load", error);
        }

        try {
          await pyodide.loadPackage("numpy");
        } catch (error) {
          throw loadError("NumPy package failed to load", error);
        }

        try {
          pyodide.runPython(await loadPythonSource());
          return pyodide.globals.get("damped_signal");
        } catch (error) {
          throw loadError("Python source execution failed", error);
        }
      })();
    }

    return dampedSignalPromise;
  }

  function pyProxyToObject(proxy) {
    try {
      return proxy.toJs({ dict_converter: Object.fromEntries });
    } finally {
      proxy.destroy();
    }
  }

  function computeSignal(dampedSignal, frequency, damping, timeMax, steps) {
    try {
      return pyProxyToObject(dampedSignal(frequency, damping, timeMax, steps));
    } catch (error) {
      throw loadError("Python calculation failed", error);
    }
  }

  async function initPythonDemo(element) {
    const [plotly, dampedSignal] = await Promise.all([
      loadPlotly(),
      loadDampedSignalFunction(),
    ]);
    let frequency = numberFromDataset(element, "frequency", 2);
    let damping = numberFromDataset(element, "damping", 0.15);
    const timeMax = numberFromDataset(element, "timeMax", 8);
    const steps = 320;
    let isMounted = false;

    const header = document.createElement("div");
    const title = document.createElement("p");
    const controls = document.createElement("div");
    const plot = document.createElement("div");

    header.className = "course-interactive__header";
    title.className = "course-interactive__title";
    title.textContent = "Python-backed Damped Signal";
    controls.className = "course-interactive__controls";
    plot.className = "course-interactive__plot";

    async function draw() {
      const data = computeSignal(dampedSignal, frequency, damping, timeMax, steps);

      await renderPlotly(
        plotly,
        plot,
        [
          {
            x: data.time,
            y: data.signal,
            mode: "lines",
            line: { color: "#2f6f73", width: 3 },
            name: "signal",
          },
          {
            x: data.time,
            y: data.upper,
            mode: "lines",
            line: { color: "#6b7280", width: 1.5, dash: "dash" },
            name: "envelope",
          },
          {
            x: data.time,
            y: data.lower,
            mode: "lines",
            line: { color: "#6b7280", width: 1.5, dash: "dash" },
            showlegend: false,
            hoverinfo: "skip",
          },
        ],
        {
          margin: { t: 20, r: 20, b: 45, l: 55 },
          xaxis: { title: "t", range: [0, timeMax] },
          yaxis: { title: "y(t)", range: [-1.1, 1.1] },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          legend: { orientation: "h", x: 0, y: 1.12 },
        }
      );
    }

    function redraw() {
      if (!isMounted) {
        return;
      }

      draw().catch((error) => {
        element.textContent = "The Python calculation could not be updated.";
        console.error(error);
      });
    }

    controls.append(
      makeRangeControl({
        label: "Frequency",
        min: 0.5,
        max: 6,
        step: 0.1,
        value: frequency,
        onInput: (value) => {
          frequency = value;
          redraw();
        },
      }),
      makeRangeControl({
        label: "Damping",
        min: 0,
        max: 0.6,
        step: 0.01,
        value: damping,
        onInput: (value) => {
          damping = value;
          redraw();
        },
      })
    );

    header.append(title);
    element.replaceChildren(header, controls, plot);
    isMounted = true;
    await draw();
  }

  registerExample("python-demo", initPythonDemo);
})();
