from __future__ import annotations

from pathlib import Path
import ast
import subprocess
import sys
from typing import Annotated, Any

import typer

from a_rtd import __version__
from a_rtd.config import ARTDConfig, config_path, load_config, new_config, write_config
from a_rtd.profiles import get_profile
from a_rtd.render import render_template
from a_rtd.update import apply_plan, build_plan, refresh_state


app = typer.Typer(help="Manage shared files for a-rtd documentation repositories.")

STARTER_EXAMPLE_FILES = {
    "docs/index.md": "examples/docs/index.md.j2",
    "docs/chapters/getting-started.md": "examples/docs/chapters/getting-started.md.j2",
    "docs/chapters/interactive-example.md": "examples/docs/chapters/interactive-example.md.j2",
    "docs/_static/js/examples/demo-plot.js": "examples/docs/_static/js/examples/demo-plot.js.j2",
    "docs/_static/js/examples/python-demo.js": "examples/docs/_static/js/examples/python-demo.js.j2",
    "docs/_static/py/examples/python_demo.py": "examples/docs/_static/py/examples/python_demo.py.j2",
    "tests/helpers.py": "examples/tests/helpers.py.j2",
    "tests/test_site.py": "examples/tests/test_site.py.j2",
}

STARTER_EXAMPLE_JS_FILES = ["js/examples/demo-plot.js", "js/examples/python-demo.js"]


def _repo_root(option_root: Path | None) -> Path:
    if option_root is not None:
        return option_root.resolve()
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / ".git").exists():
            return candidate
    return cwd


def _has_git(repo_root: Path) -> bool:
    return (repo_root / ".git").exists()


def _is_empty_repo_root(repo_root: Path) -> bool:
    if not repo_root.exists():
        return False
    return all(path.name == ".git" for path in repo_root.iterdir())


def _git_init(repo_root: Path) -> None:
    try:
        subprocess.run(
            ["git", "init"],
            cwd=repo_root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        typer.echo(f"error: could not initialize git repository in {repo_root}: {exc}", err=True)
        raise typer.Exit(2) from exc


def _load_or_exit(repo_root: Path) -> ARTDConfig:
    try:
        return load_config(repo_root)
    except FileNotFoundError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(2) from exc
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(2) from exc


def _literal_assignment(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        return ast.literal_eval(node.value)
                    except ValueError:
                        return None
    return None


def _infer_variables(repo_root: Path) -> dict[str, Any]:
    conf = repo_root / "docs" / "conf.py"
    project = _literal_assignment(conf, "project") or "Course Notes"
    author = _literal_assignment(conf, "author") or "Course Staff"
    html_theme_options = _literal_assignment(conf, "html_theme_options") or {}
    html_js_files = _literal_assignment(conf, "html_js_files") or []
    description = html_theme_options.get("description") or "Static Sphinx/MyST notes with browser-side examples"
    example_js_files = [item for item in html_js_files if isinstance(item, str) and item.startswith("js/examples/")]
    return {
        "site_name": project,
        "author": author,
        "description": description,
        "example_js_files": example_js_files,
    }


def _with_starter_examples(variables: dict[str, Any]) -> dict[str, Any]:
    existing = [
        item
        for item in variables.get("example_js_files", [])
        if isinstance(item, str)
    ]
    for script in STARTER_EXAMPLE_JS_FILES:
        if script not in existing:
            existing.append(script)
    return {**variables, "example_js_files": existing}


def _select_specs(config: ARTDConfig, file_path: str | None):
    if file_path is None:
        return config.managed_files
    selected = [spec for spec in config.managed_files if spec.path == file_path]
    if not selected:
        typer.echo(f"error: {file_path} is not managed by a-rtd", err=True)
        raise typer.Exit(2)
    return selected


def _write_starter_examples(repo_root: Path, *, force: bool) -> tuple[dict[str, int], list[str]]:
    summary = {"created": 0, "updated": 0, "skipped": 0, "conflict": 0}
    conflicts: list[str] = []
    for relative_path, template_name in STARTER_EXAMPLE_FILES.items():
        path = repo_root / relative_path
        if path.exists() and not force:
            summary["conflict"] += 1
            conflicts.append(f"{relative_path}: already exists; use --force to replace")
            continue
        text = render_template(template_name, {})
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        path.write_text(text, encoding="utf-8")
        summary["updated" if existed else "created"] += 1
    return summary, conflicts


@app.command()
def init(
    profile: Annotated[str, typer.Option("--profile")] = "sphinx-myst-course",
    from_existing: Annotated[bool, typer.Option("--from-existing")] = False,
    with_examples: Annotated[bool, typer.Option("--with-examples")] = False,
    force: Annotated[bool, typer.Option("--force")] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Initialize an existing Sphinx/MyST repo for a-rtd management."""
    root = _repo_root(repo_root)
    try:
        get_profile(profile)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(2) from exc

    explicit_mode = from_existing or with_examples
    if not explicit_mode:
        if _is_empty_repo_root(root):
            if not _has_git(root):
                _git_init(root)
            with_examples = True
        else:
            typer.echo(
                "error: a-rtd init without flags only works in an empty directory or empty git repo; "
                "use --from-existing for existing docs repos or --with-examples to add starter files",
                err=True,
            )
            raise typer.Exit(2)
    elif with_examples and not _has_git(root) and _is_empty_repo_root(root):
        _git_init(root)

    if config_path(root).exists() and not force:
        typer.echo(f"error: {config_path(root)} already exists; use --force to replace it", err=True)
        raise typer.Exit(2)

    variables = _infer_variables(root)
    if with_examples:
        variables = _with_starter_examples(variables)
    config = new_config(profile, variables)
    summary = {"created": 0, "updated": 0, "skipped": 0, "conflict": 0}
    conflicts: list[str] = []

    for spec in config.managed_files:
        plan = build_plan(root, config, spec, force=force)
        if plan.status in {"local-modified", "invalid"}:
            summary["conflict"] += 1
            conflicts.append(f"{spec.path}: {plan.status}")
            continue
        if plan.current is not None and spec.mode == "full" and plan.status == "drift" and not force:
            summary["conflict"] += 1
            conflicts.append(f"{spec.path}: existing full-managed file differs; use --force to replace")
            continue
        if plan.next_text is None:
            summary["skipped"] += 1
        else:
            if spec.path == "docs/conf.py" and plan.status == "missing-block":
                plan.path.parent.mkdir(parents=True, exist_ok=True)
                plan.path.write_text(plan.desired, encoding="utf-8")
                summary["updated"] += 1
                refresh_state(config, spec, plan.desired)
                continue
            apply_plan(plan)
            if plan.current is None:
                summary["created"] += 1
            else:
                summary["updated"] += 1
        refresh_state(config, spec, plan.desired)

    if with_examples:
        example_summary, example_conflicts = _write_starter_examples(root, force=force)
        for key, value in example_summary.items():
            summary[key] += value
        conflicts.extend(example_conflicts)

    write_config(root, config)

    typer.echo(f"Initialized {root}")
    typer.echo(
        "summary: "
        + ", ".join(f"{key}={value}" for key, value in summary.items())
    )
    if conflicts:
        typer.echo("conflicts:", err=True)
        for conflict in conflicts:
            typer.echo(f"- {conflict}", err=True)
        raise typer.Exit(1)


@app.command()
def check(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Check whether managed files match the installed a-rtd version."""
    root = _repo_root(repo_root)
    config = _load_or_exit(root)
    missing = []
    drift = []

    for spec in config.managed_files:
        plan = build_plan(root, config, spec)
        if plan.status in {"missing", "missing-block"}:
            missing.append(f"{spec.path}: {plan.status}")
        elif plan.status not in {"clean"}:
            drift.append(f"{spec.path}: {plan.status}")

    requirements = root / "requirements.txt"
    if requirements.is_file() and "a-rtd==0.1.0" not in requirements.read_text(encoding="utf-8"):
        drift.append("requirements.txt: missing a-rtd==0.1.0")

    if missing:
        for item in missing:
            typer.echo(item, err=True)
        raise typer.Exit(3)
    if drift:
        for item in drift:
            typer.echo(item, err=True)
        raise typer.Exit(1)

    typer.echo("a-rtd check clean")


@app.command(name="diff")
def diff_command(
    file: Annotated[str | None, typer.Option("--file")] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show what a-rtd update would change."""
    root = _repo_root(repo_root)
    config = _load_or_exit(root)
    chunks = []
    for spec in _select_specs(config, file):
        plan = build_plan(root, config, spec)
        if plan.diff:
            chunks.append(plan.diff)
    if chunks:
        typer.echo("\n".join(chunks), nl=False)


@app.command()
def update(
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    file: Annotated[str | None, typer.Option("--file")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Apply managed file updates from the installed a-rtd version."""
    root = _repo_root(repo_root)
    config = _load_or_exit(root)
    summary = {"clean": 0, "updated": 0, "missing": 0, "conflict": 0}
    conflicts: list[str] = []

    for spec in _select_specs(config, file):
        plan = build_plan(root, config, spec, force=force)
        if plan.status in {"local-modified", "invalid"}:
            summary["conflict"] += 1
            conflicts.append(f"{spec.path}: {plan.status}")
            continue
        if plan.next_text is None:
            summary["clean"] += 1
            continue
        if plan.status in {"missing", "missing-block"}:
            summary["missing"] += 1
        else:
            summary["updated"] += 1
        if not dry_run:
            apply_plan(plan)
            refresh_state(config, spec, plan.desired)

    if not dry_run:
        config.a_rtd["version"] = __version__
        write_config(root, config)

    typer.echo(
        ("dry-run " if dry_run else "")
        + "summary: "
        + ", ".join(f"{key}={value}" for key, value in summary.items())
    )
    if conflicts:
        for conflict in conflicts:
            typer.echo(conflict, err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    sys.exit(app())
