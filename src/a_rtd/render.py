from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from a_rtd import __version__
from a_rtd.config import ARTDConfig
from a_rtd.profiles import ManagedFileSpec


def _environment() -> Environment:
    return Environment(
        loader=PackageLoader("a_rtd", "templates"),
        autoescape=select_autoescape(default=False),
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text if text.endswith("\n") else text + "\n"


def render_template(template_name: str, context: dict[str, Any]) -> str:
    if template_name.startswith("common/") or template_name.startswith("examples/"):
        template_path = resources.files("a_rtd").joinpath("templates", template_name)
        return normalize_text(template_path.read_text(encoding="utf-8"))
    return normalize_text(_environment().get_template(template_name).render(**context))


def render_managed_file(config: ARTDConfig, spec: ManagedFileSpec) -> str:
    context = {
        "version": __version__,
        "project": config.project,
        "a_rtd": config.a_rtd,
        "variables": config.variables,
        "managed_file": spec,
    }
    return render_template(spec.template, context)


def asset_path(*parts: str) -> Path:
    return Path(str(resources.files("a_rtd").joinpath("assets", *parts)))
