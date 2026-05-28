from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from a_rtd.cli import app


runner = CliRunner()


def assert_terminal_background_near_base(settings_path: Path) -> None:
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    color = settings["workbench.colorCustomizations"]["terminal.background"]
    assert color.startswith("#")
    assert len(color) == 7
    channels = [int(color[index : index + 2], 16) for index in range(1, 7, 2)]
    base_channels = [0x58, 0x65, 0x03]
    assert all(abs(channel - base) <= 18 for channel, base in zip(channels, base_channels))


def seed_existing_repo(root: Path) -> None:
    (root / ".git").mkdir()
    (root / "docs" / "chapters").mkdir(parents=True)
    (root / "docs" / "_static" / "js" / "examples").mkdir(parents=True)
    (root / "docs" / "index.md").write_text(
        """# Test Site

```{toctree}
:maxdepth: 1

chapters/getting-started
```
""",
        encoding="utf-8",
    )
    (root / "docs" / "chapters" / "getting-started.md").write_text(
        """# Getting Started

:::{foldbox} Details

Folded text.

:::

:::{course-interactive}
:data-example: demo-plot

Interactive example loading...
:::
""",
        encoding="utf-8",
    )
    (root / "docs" / "_static" / "js" / "examples" / "demo-plot.js").write_text(
        'window.CourseInteractives.registerExample("demo-plot", function (element) { element.textContent = "ok"; });\n',
        encoding="utf-8",
    )
    (root / "docs" / "conf.py").write_text(
        """project = "Fixture Notes"
author = "Fixture Staff"
extensions = ["myst_parser", "sphinx.ext.mathjax"]
source_suffix = {".md": "markdown"}
master_doc = "index"
html_theme_options = {"description": "Fixture description", "fixed_sidebar": True}
html_js_files = ["js/course-interactives.js", "js/examples/demo-plot.js"]
""",
        encoding="utf-8",
    )
    (root / "AGENTS.md").write_text("# Local Agent Notes\n\nKeep local notes.\n", encoding="utf-8")
    (root / ".readthedocs.yaml").write_text("version: 2\n", encoding="utf-8")
    (root / "requirements.txt").write_text("sphinx>=8.2,<9\nmyst-parser>=4.0,<5\n", encoding="utf-8")


def test_init_from_existing_and_check_clean(tmp_path: Path) -> None:
    seed_existing_repo(tmp_path)

    result = runner.invoke(
        app,
        ["init", "--from-existing", "--force", "--repo-root", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".a-rtd.yml").is_file()
    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "docs/_build" in gitignore
    assert ".vscode/settings.json" in gitignore
    assert_terminal_background_near_base(tmp_path / ".vscode" / "settings.json")
    conf = (tmp_path / "docs" / "conf.py").read_text(encoding="utf-8")
    assert "a-rtd:begin managed" in conf
    assert 'project = "Fixture Notes"' in conf
    assert 'templates_path = ["_templates"]' in conf
    assert '"js/examples/demo-plot.js"' in conf
    assert (tmp_path / ".codex" / "skills" / "split-chapter-pages" / "SKILL.md").is_file()
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "# Fixture Notes" in readme
    assert "Sync From" not in readme
    assert "scripts/prepare-template-sync" not in readme
    assert "check-local-html:" in (tmp_path / "Makefile").read_text(encoding="utf-8")
    kill_script = tmp_path / "scripts" / "kill-local-http-server"
    assert kill_script.is_file()
    assert kill_script.stat().st_mode & 0o111

    check = runner.invoke(app, ["check", "--repo-root", str(tmp_path)])

    assert check.exit_code == 0, check.output
    assert "a-rtd check clean" in check.output


def test_check_reports_drift_and_diff_shows_managed_change(tmp_path: Path) -> None:
    seed_existing_repo(tmp_path)
    runner.invoke(app, ["init", "--from-existing", "--force", "--repo-root", str(tmp_path)])
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("sphinx>=8.2,<9\n", encoding="utf-8")

    check = runner.invoke(app, ["check", "--repo-root", str(tmp_path)])
    diff = runner.invoke(app, ["diff", "--file", "requirements.txt", "--repo-root", str(tmp_path)])

    assert check.exit_code == 1
    assert "requirements.txt" in check.output
    assert diff.exit_code == 0
    assert "+a-rtd==0.1.0" in diff.output


def test_update_dry_run_does_not_write(tmp_path: Path) -> None:
    seed_existing_repo(tmp_path)
    runner.invoke(app, ["init", "--from-existing", "--force", "--repo-root", str(tmp_path)])
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("sphinx>=8.2,<9\n", encoding="utf-8")

    result = runner.invoke(app, ["update", "--dry-run", "--force", "--repo-root", str(tmp_path)])

    assert result.exit_code == 0
    assert requirements.read_text(encoding="utf-8") == "sphinx>=8.2,<9\n"


def test_init_with_examples_creates_buildable_starter_site(tmp_path: Path) -> None:
    pytest.importorskip("sphinx.cmd.build")
    from sphinx.cmd.build import build_main

    (tmp_path / ".git").mkdir()

    result = runner.invoke(
        app,
        ["init", "--with-examples", "--repo-root", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs" / "index.md").is_file()
    assert ":numbered:" in (tmp_path / "docs" / "index.md").read_text(encoding="utf-8")
    assert (tmp_path / "docs" / "chapters" / "getting-started.md").is_file()
    assert (tmp_path / "docs" / "chapters" / "interactive-example.md").is_file()
    interactive = (tmp_path / "docs" / "chapters" / "interactive-example.md").read_text(encoding="utf-8")
    assert (
        ":::{course-interactive}\n"
        ":data-example: demo-plot\n\n"
        "Interactive example loading...\n"
        ":::"
    ) in interactive
    assert (
        ":::{course-interactive}\n"
        ":data-example: python-demo\n\n"
        "Interactive example loading...\n"
        ":::"
    ) in interactive
    assert (tmp_path / "docs" / "_static" / "js" / "examples" / "demo-plot.js").is_file()
    assert (tmp_path / "docs" / "_static" / "js" / "examples" / "python-demo.js").is_file()
    assert (tmp_path / "docs" / "_static" / "py" / "examples" / "python_demo.py").is_file()
    assert (tmp_path / "tests" / "test_site.py").is_file()
    conf = (tmp_path / "docs" / "conf.py").read_text(encoding="utf-8")
    assert 'templates_path = ["_templates"]' in conf
    assert '"js/examples/demo-plot.js"' in conf
    assert '"js/examples/python-demo.js"' in conf

    check = runner.invoke(app, ["check", "--repo-root", str(tmp_path)])
    assert check.exit_code == 0, check.output

    exit_code = build_main(["-b", "html", "-W", str(tmp_path / "docs"), str(tmp_path / "docs" / "_build" / "html")])
    assert exit_code == 0
    html = (tmp_path / "docs" / "_build" / "html" / "chapters" / "interactive-example.html").read_text(
        encoding="utf-8"
    )
    assert "_static/js/examples/demo-plot.js" in html
    assert "_static/js/examples/python-demo.js" in html
    assert (tmp_path / "docs" / "_build" / "html" / "_static" / "js" / "examples" / "demo-plot.js").is_file()
    assert (tmp_path / "docs" / "_build" / "html" / "_static" / "js" / "examples" / "python-demo.js").is_file()


def test_bare_init_defaults_to_examples_and_initializes_git(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", "--repo-root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".git").exists()
    assert (tmp_path / ".a-rtd.yml").is_file()
    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "docs/_build" in gitignore
    assert ".vscode/settings.json" in gitignore
    assert_terminal_background_near_base(tmp_path / ".vscode" / "settings.json")
    assert (tmp_path / "docs" / "index.md").is_file()
    assert (tmp_path / "docs" / "_static" / "js" / "examples" / "demo-plot.js").is_file()


def test_bare_init_errors_for_non_empty_repo_without_mode(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("# Existing\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--repo-root", str(tmp_path)])

    assert result.exit_code == 2
    assert "without flags only works in an empty directory" in result.output
