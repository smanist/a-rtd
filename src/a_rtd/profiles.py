from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagedFileSpec:
    path: str
    mode: str
    template: str
    name: str | None = None


@dataclass(frozen=True)
class Profile:
    name: str
    docs_dir: str
    managed_files: tuple[ManagedFileSpec, ...]
    variables: dict[str, object]


SPHINX_MYST_COURSE = Profile(
    name="sphinx-myst-course",
    docs_dir="docs",
    variables={
        "site_name": "Course Notes",
        "author": "Course Staff",
        "description": "Static Sphinx/MyST notes with browser-side examples",
        "example_js_files": [],
    },
    managed_files=(
        ManagedFileSpec(".readthedocs.yaml", "full", "sphinx/readthedocs.yaml.j2"),
        ManagedFileSpec("requirements.txt", "full", "sphinx/requirements.txt.j2"),
        ManagedFileSpec("docs/conf.py", "block", "sphinx/conf.py.j2", "sphinx-myst-course"),
        ManagedFileSpec("AGENTS.md", "block", "common/AGENTS.md.j2", "global-agent-policy"),
        ManagedFileSpec(
            ".codex/skills/split-chapter-pages/SKILL.md",
            "full",
            "common/codex/skills/split-chapter-pages/SKILL.md.j2",
        ),
        ManagedFileSpec(
            ".codex/skills/split-chapter-pages/scripts/split_chapter_pages.py",
            "full",
            "common/codex/skills/split-chapter-pages/scripts/split_chapter_pages.py.j2",
        ),
        ManagedFileSpec(
            ".codex/skills/split-chapter-pages/agents/openai.yaml",
            "full",
            "common/codex/skills/split-chapter-pages/agents/openai.yaml.j2",
        ),
    ),
)

PROFILES = {
    SPHINX_MYST_COURSE.name: SPHINX_MYST_COURSE,
}


def get_profile(name: str) -> Profile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        known = ", ".join(sorted(PROFILES))
        raise ValueError(f"unknown profile {name!r}; expected one of: {known}") from exc
