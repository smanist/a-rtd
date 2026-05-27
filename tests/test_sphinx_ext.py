from __future__ import annotations

from pathlib import Path

import pytest


def test_sphinx_extension_builds_minimal_site(tmp_path: Path) -> None:
    pytest.importorskip("sphinx.cmd.build")
    from sphinx.cmd.build import build_main

    src = tmp_path / "docs"
    out = tmp_path / "_build" / "html"
    src.mkdir()
    (src / "conf.py").write_text(
        """from a_rtd.sphinx_ext import apply_defaults

project = "Extension Fixture"
author = "Fixture Staff"
extensions = ["a_rtd.sphinx_ext"]
a_rtd_example_js_files = []
apply_defaults(globals())
""",
        encoding="utf-8",
    )
    (src / "index.md").write_text(
        """# Extension Fixture

:::{foldbox} Details

Folded text.

:::

:::{course-interactive}
:data-example: missing-example

Interactive example loading...
:::
""",
        encoding="utf-8",
    )

    exit_code = build_main(["-b", "html", "-W", str(src), str(out)])

    assert exit_code == 0
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "course-interactive" in html
    assert "foldbox" in html
    assert (out / "_static" / "css" / "course.css").is_file()
    assert (out / "_static" / "js" / "course-interactives.js").is_file()
