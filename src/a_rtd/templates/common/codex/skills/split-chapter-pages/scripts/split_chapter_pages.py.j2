#!/usr/bin/env python3
"""Split a single-file Sphinx/MyST chapter into a grouped chapter folder."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
COLON_FENCE_RE = re.compile(r"^\s*:{3,}")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line_index: int


@dataclass(frozen=True)
class SectionGroup:
    first_heading: Heading
    start: int
    end: int
    file_name: str
    link_title: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def slugify(title: str) -> str:
    value = title.lower()
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "section"


def strip_heading_markup(title: str) -> str:
    title = re.sub(r"\s*\{#[-A-Za-z0-9_:]+\}\s*$", "", title).strip()
    return title


def find_headings(lines: list[str]) -> list[Heading]:
    headings: list[Heading] = []
    in_fence = False
    colon_depth = 0
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        stripped = line.strip()
        if COLON_FENCE_RE.match(line):
            if re.fullmatch(r":{3,}", stripped):
                colon_depth = max(0, colon_depth - 1)
            else:
                colon_depth += 1
            continue
        if in_fence or colon_depth:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = strip_heading_markup(match.group(2))
        headings.append(Heading(level=level, title=title, line_index=i))
    return headings


def unique_file_name(title: str, used: set[str]) -> str:
    base = slugify(title)
    candidate = f"{base}.md"
    n = 2
    while candidate in used:
        candidate = f"{base}_{n}.md"
        n += 1
    used.add(candidate)
    return candidate


def find_summary(headings: list[Heading]) -> Heading | None:
    for heading in headings:
        if heading.level == 2 and heading.title.casefold() == "summary":
            return heading
    return None


def level2_between(headings: list[Heading], start_line: int, end_line: int) -> list[Heading]:
    return [
        h
        for h in headings
        if h.level == 2 and start_line <= h.line_index < end_line and h.title.casefold() != "summary"
    ]


def build_groups(
    headings: list[Heading],
    start_titles: list[str] | None,
) -> tuple[list[SectionGroup], int, int]:
    page_titles = [h for h in headings if h.level == 1]
    if len(page_titles) != 1:
        raise ValueError(f"expected exactly one level-1 page title, found {len(page_titles)}")

    summary = find_summary(headings)
    if summary is None:
        raise ValueError("no level-2 Summary heading found")

    middle_headings = level2_between(headings, page_titles[0].line_index + 1, summary.line_index)
    if not middle_headings:
        raise ValueError("no level-2 sections found before Summary")

    if start_titles:
        by_title = {h.title: h for h in middle_headings}
        missing = [title for title in start_titles if title not in by_title]
        if missing:
            available = "\n".join(f"- {h.title}" for h in middle_headings)
            raise ValueError(
                "requested split start not found: "
                + ", ".join(missing)
                + "\nAvailable level-2 headings:\n"
                + available
            )
        starts = [by_title[title] for title in start_titles]
        starts = sorted(starts, key=lambda h: h.line_index)
    else:
        starts = middle_headings

    if starts[0].line_index != middle_headings[0].line_index:
        raise ValueError(
            "custom split starts must include the first middle level-2 heading: "
            + middle_headings[0].title
        )

    used: set[str] = set()
    groups: list[SectionGroup] = []
    for idx, first in enumerate(starts):
        start = first.line_index
        end = starts[idx + 1].line_index if idx + 1 < len(starts) else summary.line_index
        contained = [h for h in middle_headings if start <= h.line_index < end]
        last = contained[-1]
        link_title = first.title if first.title == last.title else f"{first.title} - {last.title}"
        groups.append(
            SectionGroup(
                first_heading=first,
                start=start,
                end=end,
                file_name=unique_file_name(first.title, used),
                link_title=link_title,
            )
        )

    return groups, middle_headings[0].line_index, summary.line_index


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def make_parent(lines: list[str], groups: list[SectionGroup], middle_start: int, summary_start: int) -> str:
    before = "".join(lines[:middle_start]).rstrip()
    summary_lines = list(lines[summary_start:])
    summary_lines[0] = "**Summary**\n"
    summary = "".join(summary_lines).lstrip()
    links = ["**Sections**", ""]
    links.extend(f"- [{group.link_title}]({group.file_name})" for group in groups)
    links.extend(
        [
            "",
            "```{toctree}",
            ":hidden:",
            ":maxdepth: 1",
            "",
            *[Path(group.file_name).stem for group in groups],
            "```",
            "",
        ]
    )
    parent = before + "\n\n" + "\n".join(links) + "\n" + summary
    return ensure_trailing_newline(parent)


def rewrite_index(repo_root: Path, old_ref: str, new_ref: str, dry_run: bool) -> bool:
    index_path = repo_root / "docs" / "index.md"
    text = read_text(index_path)
    replaced = text.replace(old_ref, new_ref)
    if replaced == text:
        return False
    if not dry_run:
        write_text(index_path, replaced)
    return True


def inspect(path: Path) -> int:
    lines = read_text(path).splitlines(keepends=True)
    headings = find_headings(lines)
    for heading in headings:
        if heading.level <= 2:
            print(f"{heading.line_index + 1}: {'#' * heading.level} {heading.title}")
    return 0


def split(path: Path, start_titles: list[str] | None, dry_run: bool) -> int:
    path = path.resolve()
    repo_root = Path.cwd().resolve()
    lines = read_text(path).splitlines(keepends=True)
    headings = find_headings(lines)
    groups, middle_start, summary_start = build_groups(headings, start_titles)

    if path.parent.name != "chapters" or path.parent.parent.name != "docs":
        raise ValueError("target chapter must be a file directly under docs/chapters/")

    folder = path.with_suffix("")
    parent_path = folder / "index.md"
    old_ref = f"chapters/{path.stem}"
    new_ref = f"chapters/{path.stem}/index"

    print(f"chapter: {path}")
    print(f"folder:  {folder}")
    print(f"parent:  {parent_path}")
    print("child pages:")
    for group in groups:
        print(f"- {group.file_name}: {group.link_title}")

    if folder.exists():
        raise ValueError(f"target folder already exists: {folder}")

    index_changed = rewrite_index(repo_root, old_ref, new_ref, dry_run=True)
    if not index_changed:
        print(f"warning: did not find docs/index.md reference {old_ref!r}", file=sys.stderr)

    if dry_run:
        print("dry run only; no files changed")
        return 0

    folder.mkdir(parents=False)
    write_text(parent_path, make_parent(lines, groups, middle_start, summary_start))
    for group in groups:
        text = "".join(lines[group.start : group.end]).strip() + "\n"
        write_text(folder / group.file_name, ensure_trailing_newline(text))
    rewrite_index(repo_root, old_ref, new_ref, dry_run=False)
    path.unlink()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("chapter", type=Path)

    split_parser = subparsers.add_parser("split")
    split_parser.add_argument("chapter", type=Path)
    split_parser.add_argument("--start", action="append", default=None, help="Level-2 heading title that starts a split group")
    split_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            return inspect(args.chapter)
        if args.command == "split":
            return split(args.chapter, args.start, args.dry_run)
    except Exception as exc:  # noqa: BLE001 - command-line tool should print concise errors.
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
