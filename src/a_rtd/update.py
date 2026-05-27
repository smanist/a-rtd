from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from a_rtd import __version__
from a_rtd.config import ARTDConfig
from a_rtd.diff import unified_diff
from a_rtd.manifest import sha256_text
from a_rtd.profiles import ManagedFileSpec
from a_rtd.render import normalize_text, render_managed_file


@dataclass(frozen=True)
class FilePlan:
    spec: ManagedFileSpec
    path: Path
    desired: str
    current: str | None
    next_text: str | None
    status: str
    diff: str = ""


def _marker_prefix(path: str) -> str:
    suffix = Path(path).suffix
    if suffix in {".py", ".toml"} or Path(path).name == "Makefile":
        return "#"
    return "<!--"


def _begin_marker(spec: ManagedFileSpec) -> str:
    name = spec.name or Path(spec.path).name
    if _marker_prefix(spec.path) == "#":
        return f'# a-rtd:begin managed name="{name}" version="{__version__}"'
    return f'<!-- a-rtd:begin managed name="{name}" version="{__version__}" -->'


def _end_marker(spec: ManagedFileSpec) -> str:
    if _marker_prefix(spec.path) == "#":
        return "# a-rtd:end managed"
    return "<!-- a-rtd:end managed -->"


def managed_block(spec: ManagedFileSpec, body: str) -> str:
    return normalize_text(f"{_begin_marker(spec)}\n{body.rstrip()}\n{_end_marker(spec)}\n")


def _block_pattern(spec: ManagedFileSpec) -> re.Pattern[str]:
    name = re.escape(spec.name or Path(spec.path).name)
    if _marker_prefix(spec.path) == "#":
        return re.compile(
            rf'(?ms)^# a-rtd:begin managed name="{name}" version="[^"]+"\n.*?^# a-rtd:end managed\n?'
        )
    return re.compile(
        rf'(?ms)^<!-- a-rtd:begin managed name="{name}" version="[^"]+" -->\n.*?^<!-- a-rtd:end managed -->\n?'
    )


def get_current_block(spec: ManagedFileSpec, text: str) -> str | None:
    match = _block_pattern(spec).search(text)
    return match.group(0) if match else None


def replace_or_append_block(spec: ManagedFileSpec, current: str | None, desired: str) -> str:
    if current is None:
        return desired
    pattern = _block_pattern(spec)
    if pattern.search(current):
        return normalize_text(pattern.sub(desired, current, count=1))
    return normalize_text(current.rstrip() + "\n\n" + desired)


def build_plan(
    repo_root: Path,
    config: ARTDConfig,
    spec: ManagedFileSpec,
    *,
    force: bool = False,
) -> FilePlan:
    target = repo_root / spec.path
    rendered = render_managed_file(config, spec)
    desired = managed_block(spec, rendered) if spec.mode == "block" else rendered
    current = target.read_text(encoding="utf-8") if target.exists() else None

    if spec.mode not in {"full", "block"}:
        return FilePlan(spec, target, desired, current, None, "invalid")

    if current is None:
        return FilePlan(
            spec,
            target,
            desired,
            current,
            desired,
            "missing",
            unified_diff("", desired, f"a/{spec.path}", f"b/{spec.path}"),
        )

    current = normalize_text(current)
    if spec.mode == "full":
        if current == desired:
            return FilePlan(spec, target, desired, current, None, "clean")
        old_hash = config.state.get(spec.path, {}).get("sha256")
        if old_hash and sha256_text(current) != old_hash and not force:
            return FilePlan(
                spec,
                target,
                desired,
                current,
                None,
                "local-modified",
                unified_diff(current, desired, f"a/{spec.path}", f"b/{spec.path}"),
            )
        return FilePlan(
            spec,
            target,
            desired,
            current,
            desired,
            "drift",
            unified_diff(current, desired, f"a/{spec.path}", f"b/{spec.path}"),
        )

    current_block = get_current_block(spec, current)
    if current_block == desired:
        return FilePlan(spec, target, desired, current, None, "clean")
    next_text = replace_or_append_block(spec, current, desired)
    status = "missing-block" if current_block is None else "drift"
    diff_old = current_block or ""
    return FilePlan(
        spec,
        target,
        desired,
        current,
        next_text,
        status,
        unified_diff(diff_old, desired, f"a/{spec.path}", f"b/{spec.path}"),
    )


def apply_plan(plan: FilePlan) -> None:
    if plan.next_text is None:
        return
    plan.path.parent.mkdir(parents=True, exist_ok=True)
    plan.path.write_text(plan.next_text, encoding="utf-8")
    if plan.spec.path.startswith("scripts/") or "/scripts/" in plan.spec.path:
        plan.path.chmod(0o755)


def refresh_state(config: ARTDConfig, spec: ManagedFileSpec, desired: str) -> None:
    config.state[spec.path] = {
        "mode": spec.mode,
        "template": spec.template,
        "version": __version__,
        "sha256": sha256_text(desired),
    }
