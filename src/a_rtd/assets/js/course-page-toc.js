(function () {
  "use strict";

  function headingText(heading) {
    const clone = heading.cloneNode(true);
    clone.querySelectorAll(".headerlink").forEach((link) => link.remove());
    return clone.textContent.trim();
  }

  function sectionIdForHeading(heading) {
    const section = heading.closest("section[id]");
    return section ? section.id : "";
  }

  function createItem(heading) {
    const sectionId = sectionIdForHeading(heading);
    const text = headingText(heading);

    if (!sectionId || !text) {
      return null;
    }

    const item = document.createElement("li");
    const link = document.createElement("a");

    item.className = `course-page-toc__item course-page-toc__item--${heading.tagName.toLowerCase()}`;
    item.dataset.sectionId = sectionId;
    link.href = `#${sectionId}`;
    link.textContent = text;
    item.append(link);

    return item;
  }

  function setCurrentTocItem(toc, sectionId) {
    toc.querySelectorAll(".course-page-toc__item").forEach((item) => {
      const isCurrent = item.dataset.sectionId === sectionId;
      item.classList.toggle("course-page-toc__item--current", isCurrent);
      const link = item.querySelector("a");
      if (link) {
        if (isCurrent) {
          link.setAttribute("aria-current", "location");
        } else {
          link.removeAttribute("aria-current");
        }
      }
    });
  }

  function initCurrentSectionTracking(toc, headings) {
    function currentSectionId() {
      const offset = 24;
      let current = sectionIdForHeading(headings[0]);

      headings.forEach((heading) => {
        if (heading.getBoundingClientRect().top <= offset) {
          current = sectionIdForHeading(heading);
        }
      });

      return current;
    }

    function refresh() {
      setCurrentTocItem(toc, currentSectionId());
    }

    window.addEventListener("scroll", refresh, { passive: true });
    window.addEventListener("resize", refresh);
    window.addEventListener("hashchange", refresh);
    refresh();
  }

  function initPageToc() {
    const documentWrapper = document.querySelector(".documentwrapper");
    const body = document.querySelector(".body[role='main']");

    if (!documentWrapper || !body) {
      return;
    }

    const isGroupChild = Boolean(document.querySelector(".sphinxsidebar .toctree-l2.current"));
    const selector = isGroupChild
      ? "section[id] > h1, section[id] > h2, section[id] > h3"
      : "section[id] > h2, section[id] > h3";
    const headings = [...body.querySelectorAll(selector)];
    const items = headings
      .map(createItem)
      .filter(Boolean);

    if (items.length < (isGroupChild ? 1 : 2)) {
      return;
    }

    const toc = document.createElement("nav");
    const title = document.createElement("div");
    const list = document.createElement("ol");

    toc.className = "course-page-toc";
    toc.setAttribute("aria-label", "Page table of contents");
    title.className = "course-page-toc__title";
    title.textContent = "On this page";
    list.className = "course-page-toc__list";
    list.append(...items);
    toc.append(title, list);

    documentWrapper.prepend(toc);
    initCurrentSectionTracking(toc, headings);
  }

  document.addEventListener("DOMContentLoaded", initPageToc);
})();
