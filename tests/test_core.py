from __future__ import annotations

from pathlib import Path

from a_rtd.config import new_config
from a_rtd.manifest import sha256_text
from a_rtd.profiles import ManagedFileSpec
from a_rtd.render import render_managed_file
from a_rtd.update import build_plan, get_current_block, managed_block, refresh_state


def test_render_requirements_template_contains_pinned_package() -> None:
    config = new_config("sphinx-myst-course")
    spec = ManagedFileSpec("requirements.txt", "full", "sphinx/requirements.txt.j2")

    rendered = render_managed_file(config, spec)

    assert "a-rtd==0.1.0" in rendered
    assert "sphinx>=8.2,<9" in rendered


def test_block_replacement_preserves_local_content(tmp_path: Path) -> None:
    config = new_config("sphinx-myst-course")
    spec = ManagedFileSpec("AGENTS.md", "block", "common/AGENTS.md.j2", "global-agent-policy")
    desired = managed_block(spec, render_managed_file(config, spec))
    path = tmp_path / "AGENTS.md"
    path.write_text(f"# Local\n\n{desired}\nLocal tail\n", encoding="utf-8")

    plan = build_plan(tmp_path, config, spec)

    assert plan.status == "clean"
    assert get_current_block(spec, path.read_text(encoding="utf-8")) == desired


def test_full_file_local_modification_is_detected(tmp_path: Path) -> None:
    config = new_config("sphinx-myst-course")
    spec = ManagedFileSpec("requirements.txt", "full", "sphinx/requirements.txt.j2")
    desired = render_managed_file(config, spec)
    path = tmp_path / "requirements.txt"
    path.write_text(desired, encoding="utf-8")
    refresh_state(config, spec, desired)
    path.write_text(desired + "# local edit\n", encoding="utf-8")

    plan = build_plan(tmp_path, config, spec)

    assert plan.status == "local-modified"
    assert config.state["requirements.txt"]["sha256"] == sha256_text(desired)
