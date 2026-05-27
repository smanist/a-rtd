# Agent Guidelines

This repository is a static Sphinx/MyST site for interactive course notes.

## Documentation Structure

- Keep chapter content in Markdown under `docs/chapters/`.
- Name numbered chapter files as `NN_<chapter_title_slug>.md`, where `NN` is
  the two-digit chapter number and the title slug is lowercase snake case. For
  example, Chapter 1 "Model Taxonomy" should be
  `docs/chapters/01_model_taxonomy.md`.
- Prefer MyST syntax for math, cross-references, figures, and directives.
- Use the repo-local `foldbox` MyST directive for detailed math derivations or
  other optional technical detail that should be folded by default:

  ````md
  :::{foldbox} Detailed derivation

  ```{math}
  \delta \dot{x}
  = \left.\ppf{f}{x}\right|_{x^\ast} \delta x .
  ```

  :::
  ````

  Add the `:open:` option only when a foldbox should be expanded initially.
- Keep Sphinx configuration in `docs/conf.py`.
- Keep shared styling in `docs/_static/css/`.
- Keep browser-side interactive code in `docs/_static/js/`.
- When editing existing chapter content, do not change site architecture files
  such as `docs/conf.py`, built HTML files, templates, shared static assets, or
  navigation files unless the user explicitly asks for those changes.
- For a single-file chapter, or for the top-level file in a grouped chapter,
  name the final content-summary section `Summary`. Do not use alternate names
  such as `Takeaways`, `Key Takeaways`, or `Conclusion` for that section.

## Syllabus and Notation Policy

- If a repository has files under `syllabus/`, treat them as read-only
  reference material unless the user explicitly asks to edit them.
- If a repository has `syllabus/notation_convention.md`, follow it when writing
  math notation in chapters.
- When adding a notation guide to a course, keep the detailed guide in
  `syllabus/notation_convention.md` and summarize only the most frequently used
  conventions in this file.

## Avoid Raw HTML in Chapters

- Do not put large raw HTML, inline scripts, or implementation logic directly
  inside chapter Markdown files.
- A chapter may embed an interactive example in prose, but the Markdown should
  contain only a small semantic MyST placeholder when possible.
- Prefer the `course-interactive` MyST directive:

  ```md
  :::{course-interactive}
  :data-example: demo-plot

  Interactive example loading...
  :::
  ```

- Put JavaScript, plotting logic, Pyodide calls, and DOM construction in static
  JavaScript files.
- If a raw HTML block grows beyond a small placeholder, move that behavior into
  a reusable directive, template, or JavaScript module.
- Bind implemented examples with `:data-example:` only. Do not encode example
  identity in extra CSS classes.

## Interactive Spec Blocks

- Use MyST containers to mark planned interactive examples before
  implementation. Do not use raw custom HTML tags such as `<interaction>`.
- Temporary specs should use the `interactive-spec` class and a stable `:name:`
  value:

  ```md
  :::{container} interactive-spec
  :name: interactive-spec-ch01-oscillator

  Visualize the hand-derived oscillator example. Show phase-plane motion,
  time traces, and controls for frequency and initial condition.

  Reference implementation: `ch01_oscillator.py`
  :::
  ```

- When implementing a spec, replace the `interactive-spec` block with the final
  `course-interactive` directive and move all runtime behavior into
  `docs/_static/js/examples/`.
- Treat reference implementations as optional, read-only drafting aids, not as
  source files for the built site.
- Before resolving a reference path, prepend `../../scratch/`. For example,
  `ch01_oscillator.py` means `../../scratch/ch01_oscillator.py`. Agents working
  from `.a-dev/worktrees/<name>/` should look in the sibling scratch directory
  at `.a-dev/scratch/`, without requiring chapter Markdown to use those path
  prefixes.
- If a referenced scratch file is missing, proceed from the written spec rather
  than blocking.

## Importing Chapters

- Do not leave top-level LaTeX macro definitions such as `\newcommand` in the
  chapter body. Move shared macros into `mathjax3_config` in `docs/conf.py`.
- Convert display math written as `$$ ... $$` to MyST math fences:

  ````md
  ```{math}
  ...
  ```
  ````

- Preserve equation labels during conversion. For example, convert
  `$$ ... $$ {#eq:model}` to:

  ````md
  ```{math}
  :label: eq:model

  ...
  ```
  ````

- Give every imported chapter one real page title heading.
- If the sample uses level-1 headings for sections, demote them one level after
  adding the page title. This prevents Sphinx sidebars and toctrees from
  treating each section as a separate page-level entry.
- When adding a chapter, add it to the `docs/index.md` toctree unless it is
  intentionally hidden.
- After conversion, run a fresh Sphinx build when navigation, labels, or math
  parsing changed.

## Modular Interactive Examples

These conventions apply when interactive work is explicitly in scope, or when
maintaining existing interactive infrastructure.

- Keep interactive examples as individual JavaScript files whenever possible.
- Use one file per example or closely related example family.
- Keep `docs/_static/js/course-interactives.js` focused on shared loader,
  registry, and initialization behavior.
- Example files should register a small initializer that receives the
  placeholder element and reads configuration from `data-*` attributes.
- Register examples by name with `window.CourseInteractives.registerExample`;
  the name must match the placeholder's `:data-example:` value.
- Avoid duplicating CDN loading logic across example files. Use shared helpers
  for Plotly, Pyodide, p5.js, and JSXGraph.
- Pyodide-backed examples that need local Python source while opened with
  `file://` should embed that source in the example JavaScript or otherwise
  avoid fetching local files. Browser security blocks `fetch()` from local file
  pages. When an example fetches separate static Python files, test it through a
  local HTTP server.
- For Plotly examples, use the shared `renderPlotly` helper from
  `window.CourseInteractives` rather than calling `Plotly.react` directly. This
  keeps generated Plotly components resized to the main text column and prevents
  plots from overflowing or being clipped by the interactive container.
- Recompute examples from user inputs in the browser only. Do not introduce a
  backend dependency.

## Asset Loading

- Use pinned CDN versions for Plotly, Pyodide, p5.js, and JSXGraph unless the
  project explicitly switches to vendored assets.
- Lazy-load heavyweight libraries only when an example actually needs them.
- Keep the site deployable as a static Sphinx build.

## Local Website Workflow

- For quick local checks, start a server from the repository root with
  `make serve-html`.
- Visit local pages at `http://localhost:<port>/docs/_build/html/` after a
  Sphinx build, or serve a built output directory directly.
- Prefer the local HTTP server workflow for browser verification, especially
  when an example fetches static assets.
- Stop repo-local HTTP servers with `scripts/kill-local-http-server <pid>`.
  Do not use raw `kill <pid>` for this workflow.

## Verification

- Run `make check` before handing off any change that adds or edits chapters,
  updates `docs/index.md`, changes Sphinx configuration, or changes static site
  assets. This is the required pre-review check for documentation work and runs
  both the fresh Sphinx build and the test suite.
- Use `make html` for an intermediate documentation-only check while drafting.
  The handoff check is still `make check`.
- Use `make check-local-html` when you specifically need to verify the built
  site through the local HTTP server route.
- For interactive examples, verify at least one rendered page in a browser when
  behavior changes.
