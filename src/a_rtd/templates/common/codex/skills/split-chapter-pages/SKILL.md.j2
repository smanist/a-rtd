---
name: split-chapter-pages
description: Split a single-file Sphinx/MyST chapter in this repository into a grouped chapter folder. Use when the user selects a chapter and asks to split, group, paginate, or break it into subpages while preserving the original page as the foreword plus Summary and replacing middle sections with links to child pages. Supports default splits at each level-2 heading and custom split starts specified by section heading.
---

# Split Chapter Pages

Use this skill to convert one chapter file under `docs/chapters/` into a folder containing an `index.md` page plus one or more child pages.

## Required Shape

- Start from one chapter Markdown file named `docs/chapters/NN_slug.md`.
- Move it to `docs/chapters/NN_slug/index.md`.
- Keep the original page title, foreword content before the first split section, and final `## Summary` section in `index.md`.
- Replace the middle content with links to child pages.
- Put child pages in the same folder, one file per split group.
- Add a hidden toctree for the child pages so Sphinx includes them in the grouped chapter navigation.
- Update `docs/index.md` so the toctree entry points to `chapters/NN_slug/index`.
- Run `make check` before handoff.

## Split Rules

- Default split: each level-2 section between the foreword and `## Summary` becomes one child page.
- Custom split: if the user names split starts, make each group begin at that `##` heading and include following sections until the next specified split start or `## Summary`.
- Treat `## Summary` as the final section that remains on `index.md`; do not create a child page for it.
- In the new `index.md`, render `Sections` and `Summary` as bold text, not Markdown headings.
- In child pages, preserve the moved section heading levels exactly; a moved `##` heading must remain `##`, not become `#`.
- Preserve all content inside each moved section, including subsections, MyST directives, labels, math fences, figures, and interactive placeholders.
- Do not split inside fenced code blocks, math fences, MyST directives, or raw HTML blocks.

## Workflow

1. Identify the selected chapter file. If the user gives only a number or title, match it against `docs/chapters/NN_*.md`.
2. Inspect headings with:

   ```bash
   python .codex/skills/split-chapter-pages/scripts/split_chapter_pages.py inspect docs/chapters/NN_slug.md
   ```

3. Choose split starts:
   - Use every non-`Summary` level-2 heading by default.
   - Use the user's specified level-2 headings for custom grouping.
   - Include the first non-summary level-2 heading as the first split start for custom grouping.
4. Preview the operation:

   ```bash
   python .codex/skills/split-chapter-pages/scripts/split_chapter_pages.py split docs/chapters/NN_slug.md --dry-run
   ```

   For custom starts, add repeated `--start "Heading text"` arguments in the requested order.

5. Apply the split:

   ```bash
   python .codex/skills/split-chapter-pages/scripts/split_chapter_pages.py split docs/chapters/NN_slug.md
   ```

6. Review the diff manually. Check that:
   - `index.md` still has exactly one `#` page title and no `## Sections` or `## Summary` headings.
   - The visible link list and hidden toctree appear between the foreword and bold `**Summary**`.
   - Child pages begin with the original moved heading level, usually `##`.
   - Slugs are readable and stable.
   - `docs/index.md` links to `chapters/NN_slug/index`.
7. Run `make check`. For behavior-changing interactives, also verify one rendered page in a browser.

## Link List Style

Use a compact MyST-friendly list on the parent page, followed by a hidden toctree:

````md
**Sections**

- [Section title](section-title.md)
- [First section - Last section](first-section.md)

```{toctree}
:hidden:
:maxdepth: 1

section-title
first-section
```

**Summary**
````

If the original chapter already has a level-2 heading between the foreword and content that should not be moved, do not invent a different structure; ask the user for split starts or handle it conservatively after inspecting the chapter.

## Sidebar Numbering

Grouped chapters use `chapters/NN_slug/index` in the root toctree. The custom sidebar code in `docs/conf.py` must compute the chapter number from the folder name when a docname ends in `/index`; otherwise grouped chapters appear unnumbered in the left navigation.

Because child pages intentionally preserve original `##` headings, the repo configuration should suppress the expected `myst.header` warning for these grouped pages.

The right page navigation script should treat grouped child pages specially: include rendered `h1` headings and show the page TOC even when there is only one item. This keeps single-section child pages navigable after Sphinx renders preserved `##` source headings as page-level HTML headings.

## Failure Handling

- If the target folder already exists, stop and inspect before editing; do not overwrite child pages blindly.
- If there is no `## Summary`, ask the user whether the final level-2 section should be treated as summary before splitting.
- If a requested split start does not exactly match a level-2 heading, show the available headings and ask for clarification.
- If `make check` fails because of pre-existing unrelated failures, report that clearly and include the relevant failure lines.
