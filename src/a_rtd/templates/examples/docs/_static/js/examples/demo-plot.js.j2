(function () {
  "use strict";

  const {
    loadPlotly,
    makeRangeControl,
    numberFromDataset,
    registerExample,
    renderPlotly,
  } = window.CourseInteractives;

  function sampleSine({ frequency, amplitude }) {
    const x = [];
    const y = [];

    for (let i = 0; i <= 240; i += 1) {
      const t = (2 * Math.PI * i) / 240;
      x.push(t);
      y.push(amplitude * Math.sin(frequency * t));
    }

    return { x, y };
  }

  async function initDemoPlot(element) {
    const plotly = await loadPlotly();
    let frequency = numberFromDataset(element, "frequency", 2);
    let amplitude = numberFromDataset(element, "amplitude", 1);

    const header = document.createElement("div");
    const title = document.createElement("p");
    const controls = document.createElement("div");
    const plot = document.createElement("div");

    header.className = "course-interactive__header";
    title.className = "course-interactive__title";
    title.textContent = "Sine Wave";
    controls.className = "course-interactive__controls";
    plot.className = "course-interactive__plot";

    function draw() {
      const data = sampleSine({ frequency, amplitude });
      renderPlotly(
        plotly,
        plot,
        [
          {
            x: data.x,
            y: data.y,
            mode: "lines",
            line: { color: "#2f6f73", width: 3 },
            name: "signal",
          },
        ],
        {
          margin: { t: 20, r: 20, b: 45, l: 55 },
          xaxis: { title: "t", range: [0, 2 * Math.PI] },
          yaxis: { title: "y(t)", range: [-2.1, 2.1] },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          showlegend: false,
        }
      );
    }

    controls.append(
      makeRangeControl({
        label: "Frequency",
        min: 1,
        max: 8,
        step: 1,
        value: frequency,
        onInput: (value) => {
          frequency = value;
          draw();
        },
      }),
      makeRangeControl({
        label: "Amplitude",
        min: 0.2,
        max: 2,
        step: 0.1,
        value: amplitude,
        onInput: (value) => {
          amplitude = value;
          draw();
        },
      })
    );

    header.append(title);
    element.replaceChildren(header, controls, plot);
    draw();
  }

  registerExample("demo-plot", initDemoPlot);
})();
