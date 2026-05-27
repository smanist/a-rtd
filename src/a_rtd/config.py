from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from a_rtd import __version__
from a_rtd.profiles import ManagedFileSpec, get_profile


CONFIG_NAME = ".a-rtd.yml"


@dataclass
class ARTDConfig:
    version: int
    project: dict[str, Any]
    a_rtd: dict[str, Any]
    profile: str
    managed_files: list[ManagedFileSpec]
    variables: dict[str, Any]
    state: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def docs_dir(self) -> str:
        return str(self.project.get("docs_dir") or "docs")


def config_path(repo_root: Path) -> Path:
    return repo_root / CONFIG_NAME


def load_config(repo_root: Path) -> ARTDConfig:
    path = config_path(repo_root)
    if not path.is_file():
        raise FileNotFoundError(f"missing {CONFIG_NAME}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    try:
        managed = [
            ManagedFileSpec(
                path=str(item["path"]),
                mode=str(item["mode"]),
                template=str(item["template"]),
                name=item.get("name"),
            )
            for item in raw["managed_files"]
        ]
        return ARTDConfig(
            version=int(raw["version"]),
            project=dict(raw["project"]),
            a_rtd=dict(raw["a_rtd"]),
            profile=str(raw["profile"]),
            managed_files=managed,
            variables=dict(raw.get("variables") or {}),
            state=dict(raw.get("state") or {}),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid {CONFIG_NAME}: {exc}") from exc


def dump_config(config: ARTDConfig) -> str:
    data = {
        "version": config.version,
        "project": config.project,
        "a_rtd": config.a_rtd,
        "profile": config.profile,
        "managed_files": [
            {
                "path": spec.path,
                "mode": spec.mode,
                "template": spec.template,
                **({"name": spec.name} if spec.name else {}),
            }
            for spec in config.managed_files
        ],
        "variables": config.variables,
        "state": config.state,
    }
    return yaml.safe_dump(data, sort_keys=False)


def write_config(repo_root: Path, config: ARTDConfig) -> None:
    config_path(repo_root).write_text(dump_config(config), encoding="utf-8")


def new_config(profile_name: str, variables: dict[str, Any] | None = None) -> ARTDConfig:
    profile = get_profile(profile_name)
    merged_variables = {**profile.variables, **(variables or {})}
    site_name = str(merged_variables.get("site_name") or "Course Notes")
    return ARTDConfig(
        version=1,
        project={
            "name": site_name,
            "profile": profile.name,
            "docs_dir": profile.docs_dir,
            "site_url": None,
        },
        a_rtd={
            "version": __version__,
            "update_policy": "managed-blocks",
        },
        profile=profile.name,
        managed_files=list(profile.managed_files),
        variables=merged_variables,
        state={},
    )
