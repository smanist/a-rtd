from __future__ import annotations

from html import escape
from pathlib import Path
import re
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes

from a_rtd import __version__
from a_rtd.render import asset_path


DEFAULT_MATHJAX_MACROS = {
    "dd": r"\mathrm{d}",
    "ppf": [r"\frac{\partial #1}{\partial #2}", 2],
    "pppf": [r"\frac{\partial^2 #1}{\partial #2^2}", 2],
    "ddf": [r"\frac{\mathrm{d} #1}{\mathrm{d} #2}", 2],
    "norm": [r"\left\lVert #1 \right\rVert", 1],
    "mbf": r"\mathbf",
    "mcl": r"\mathcal",
    "mbb": r"\mathbb",
    "Re": r"\mathrm{Re}",
    "Im": r"\mathrm{Im}",
}


def _append_unique(values: list[str], additions: list[str]) -> list[str]:
    result = list(values)
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def apply_defaults(namespace: dict[str, Any]) -> None:
    """Apply the shared Sphinx/MyST course-site defaults to ``conf.py`` globals."""
    project = namespace.get("project", "Course Notes")
    description = namespace.get(
        "a_rtd_theme_description",
        "Static Sphinx/MyST notes with browser-side examples",
    )
    example_js_files = list(namespace.get("a_rtd_example_js_files", []))

    namespace["extensions"] = _append_unique(
        list(namespace.get("extensions", [])),
        ["myst_parser", "sphinx.ext.mathjax", "a_rtd.sphinx_ext"],
    )
    namespace.setdefault("source_suffix", {".md": "markdown"})
    namespace.setdefault("master_doc", "index")
    namespace["exclude_patterns"] = _append_unique(list(namespace.get("exclude_patterns", [])), ["_build", "README.md"])
    namespace.setdefault("myst_enable_extensions", ["amsmath", "colon_fence", "dollarmath"])
    namespace.setdefault("myst_heading_anchors", 3)
    namespace["suppress_warnings"] = _append_unique(list(namespace.get("suppress_warnings", [])), ["myst.header"])
    namespace.setdefault("numfig", True)

    namespace.setdefault("html_theme", "alabaster")
    namespace.setdefault("html_title", project)
    namespace["html_static_path"] = _append_unique(list(namespace.get("html_static_path", [])), [str(asset_path())])
    namespace["templates_path"] = _append_unique(list(namespace.get("templates_path", [])), [str(asset_path("templates"))])
    namespace.setdefault("html_sidebars", {"**": ["navigation.html"]})
    namespace["html_css_files"] = _append_unique(list(namespace.get("html_css_files", [])), ["css/course.css"])
    namespace["html_js_files"] = _append_unique(
        list(namespace.get("html_js_files", [])),
        ["js/course-interactives.js", "js/course-page-toc.js", *example_js_files],
    )

    mathjax = dict(namespace.get("mathjax3_config", {}))
    tex = dict(mathjax.get("tex", {}))
    macros = dict(tex.get("macros", {}))
    macros = {**DEFAULT_MATHJAX_MACROS, **macros}
    tex["macros"] = macros
    mathjax["tex"] = tex
    namespace["mathjax3_config"] = mathjax

    theme_options = dict(namespace.get("html_theme_options", {}))
    theme_options.setdefault("description", description)
    theme_options.setdefault("fixed_sidebar", True)
    namespace["html_theme_options"] = theme_options


def _doc_title(env: Any, docname: str, explicit_title: str | None = None) -> str:
    if explicit_title:
        return explicit_title
    title_node = env.titles.get(docname)
    if title_node is not None:
        return title_node.astext()
    return docname.rsplit("/", 1)[-1].replace("_", " ").title()


def _toctree_entries(env: Any, docname: str):
    doctree = env.get_doctree(docname)
    for node in doctree.findall(addnodes.toctree):
        for explicit_title, ref in node.get("entries", []):
            if ref in env.found_docs:
                yield {
                    "docname": ref,
                    "title": _doc_title(env, ref, explicit_title),
                }


def _chapter_number(docname: str) -> str | None:
    parts = docname.split("/")
    basename = parts[-2] if parts[-1] == "index" and len(parts) > 1 else parts[-1]
    match = re.match(r"(\d+)_", basename)
    if match is None:
        return None
    return str(int(match.group(1)))


class CourseInteractiveDirective(Directive):
    has_content = True
    option_spec = {
        "data-example": directives.unchanged_required,
        "name": directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        content = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, content)
        data_example = escape(self.options["data-example"], quote=True)
        return [
            nodes.raw("", f'<div class="course-interactive" data-example="{data_example}">', format="html"),
            *content.children,
            nodes.raw("", "</div>", format="html"),
        ]


class FoldBoxDirective(Directive):
    has_content = True
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "open": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        content = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, content)
        title = escape(self.arguments[0] if self.arguments else "Details", quote=True)
        open_attr = " open" if "open" in self.options else ""
        return [
            nodes.raw(
                "",
                (
                    f'<details class="foldbox"{open_attr}>'
                    f'<summary class="foldbox__summary">{title}</summary>'
                    '<div class="foldbox__content">'
                ),
                format="html",
            ),
            *content.children,
            nodes.raw("", "</div></details>", format="html"),
        ]


def add_course_sidebar_context(app: Any, pagename: str, templatename: str, context: dict[str, Any], doctree: Any) -> None:
    parts = pagename.split("/")
    group_index = None
    for length in range(len(parts) - 1, 0, -1):
        candidate = "/".join([*parts[:length], "index"])
        if candidate != pagename and candidate in app.env.found_docs:
            group_index = candidate
            break

    sidebar_items = []
    group_children = list(_toctree_entries(app.env, group_index)) if group_index else []
    for item in _toctree_entries(app.env, app.config.master_doc):
        item = dict(item)
        item["number"] = _chapter_number(item["docname"])
        item["nav_title"] = f"{item['number']}. {item['title']}" if item["number"] else item["title"]
        item["current"] = pagename == item["docname"] or group_index == item["docname"]
        item["children"] = group_children if group_index == item["docname"] else []
        sidebar_items.append(item)

    context["course_group_child"] = group_index is not None
    context["course_group_index"] = group_index
    context["course_sidebar_items"] = sidebar_items


def setup(app: Any) -> dict[str, Any]:
    app.add_directive("course-interactive", CourseInteractiveDirective)
    app.add_directive("foldbox", FoldBoxDirective)
    app.connect("html-page-context", add_course_sidebar_context)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
