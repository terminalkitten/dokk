(() => {
  // Copy button on code blocks.
  for (const pre of document.querySelectorAll(".dk-prose pre")) {
    const wrap = document.createElement("div");
    wrap.className = "dk-code";
    pre.replaceWith(wrap);
    wrap.append(pre);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn dk-copy";
    btn.dataset.variant = "outline";
    btn.dataset.size = "xs";
    btn.textContent = "Copy";
    btn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(pre.innerText);
        btn.textContent = "Copied";
      } catch {
        btn.textContent = "Failed";
      }
      setTimeout(() => (btn.textContent = "Copy"), 1500);
    };
    wrap.append(btn);
  }

  // Search: Basecoat command palette over the Pagefind JS API (loaded on first open).
  const dlg = document.getElementById("dk-search");
  if (dlg) {
    const input = dlg.querySelector("input");
    const menu = dlg.querySelector("[role=menu]");
    let pagefind;
    const load = async () => {
      if (!pagefind) {
        pagefind = await import(dlg.dataset.bundle + "pagefind.js");
        await pagefind.options({ baseUrl: dlg.dataset.base });
      }
      return pagefind;
    };
    // Wrap query words found in plain text in <mark>, building nodes (no innerHTML).
    const highlight = (el, text, query) => {
      const words = query.split(/\s+/).filter(Boolean).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
      const parts = words.length ? text.split(new RegExp(`(${words.join("|")})`, "gi")) : [text];
      el.append(...parts.map((p, i) => (i % 2 ? Object.assign(document.createElement("mark"), { textContent: p }) : p)));
    };
    const render = (items, query) => {
      menu.dataset.empty = query ? "No results found." : "Type to search.";
      if (!items.length) {
        menu.replaceChildren();
      } else {
        const group = document.createElement("div");
        group.setAttribute("role", "group");
        group.setAttribute("aria-labelledby", "dk-search-heading");
        group.innerHTML = '<span role="heading" id="dk-search-heading">Results</span>';
        for (const r of items) {
          const a = document.createElement("a");
          a.setAttribute("role", "menuitem");
          a.href = r.url;
          const title = document.createElement("strong");
          highlight(title, r.meta.title || r.url, query);
          const excerpt = document.createElement("span");
          excerpt.innerHTML = r.excerpt; // Pagefind escapes the text; only <mark> is HTML
          a.append(title, excerpt);
          group.append(a);
        }
        menu.replaceChildren(group);
      }
      dlg.querySelector(".command").refresh?.();
    };
    input.addEventListener("input", async () => {
      const query = input.value.trim();
      const search = await (await load()).debouncedSearch(query, {}, 150);
      if (search === null) return; // superseded by a newer keystroke
      render(query ? await Promise.all(search.results.slice(0, 8).map((r) => r.data())) : [], query);
    });
    const open = () => {
      if (!dlg.open) dlg.showModal();
      input.focus();
      load();
    };
    for (const b of document.querySelectorAll("[data-dk-search]")) b.addEventListener("click", open);
    if (!/Mac|iPhone|iPad/.test(navigator.platform)) {
      for (const k of document.querySelectorAll(".dk-search-kbd")) k.textContent = "Ctrl K";
    }
    document.addEventListener("keydown", (e) => {
      const typing = e.target.closest("input, textarea, select, [contenteditable]");
      if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing)) {
        e.preventDefault();
        open();
      }
    });
  }

  // Copy page: fetch the page's Markdown and put it on the clipboard.
  const check = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
  for (const btn of document.querySelectorAll("[data-dk-copy-page]")) {
    btn.addEventListener("click", async () => {
      const url = btn.dataset.dkCopyPage;
      const icon = btn.querySelector("svg");
      const original = icon.outerHTML;
      try {
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error(res.status);
        await navigator.clipboard.writeText(await res.text());
        btn.querySelector("svg").outerHTML = check;
        setTimeout(() => (btn.querySelector("svg").outerHTML = original), 1200);
      } catch {
        window.open(url, "_blank", "noopener"); // no clipboard: show the Markdown instead
      }
    });
  }

  // ::image: open the full image in one shared dialog. Esc, the close button or a click
  // outside closes it. Without JavaScript the link opens the image file.
  let lightbox;
  document.addEventListener("click", (e) => {
    const link = e.target.closest("[data-dk-zoom]");
    if (!link || e.ctrlKey || e.metaKey || e.shiftKey) return;
    e.preventDefault();
    if (!lightbox) {
      lightbox = document.createElement("dialog");
      lightbox.className = "dk-lightbox";
      lightbox.innerHTML = '<button type="button" class="btn" data-variant="secondary" data-size="icon" aria-label="Close">' +
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>' +
        "</button><img alt=\"\">";
      lightbox.addEventListener("click", (ev) => {
        if (ev.target === lightbox || ev.target.closest("button")) lightbox.close();
      });
      document.body.append(lightbox);
    }
    const img = link.querySelector("img");
    const full = lightbox.querySelector("img");
    full.src = link.href;
    full.alt = img ? img.alt : "";
    lightbox.setAttribute("aria-label", full.alt || "Image");
    lightbox.showModal();
  });

  // Remember whether the sidebar is collapsed (desktop only: on phones it is an overlay that
  // starts closed). base.html.jinja restores it before the first paint.
  const sidebar = document.getElementById("dk-sidebar");
  if (sidebar) {
    new MutationObserver(() => {
      if (innerWidth < (parseInt(sidebar.dataset.breakpoint) || 768)) return;
      try {
        localStorage.setItem("dk-sidebar", sidebar.getAttribute("aria-hidden") === "true" ? "closed" : "open");
      } catch {}
    }).observe(sidebar, { attributes: true, attributeFilter: ["aria-hidden"] });
  }

  // Synced tabs: tab sets with the same data-sync key switch together, and the
  // choice is remembered across pages.
  const synced = [...document.querySelectorAll(".dk-tabs[data-sync]")];
  const choose = (sync, label) => {
    for (const tabs of synced.filter((t) => t.dataset.sync === sync)) {
      const tab = [...tabs.querySelectorAll('[role="tab"]')].find((b) => b.textContent.trim() === label);
      if (tab && tab.getAttribute("aria-selected") !== "true") tab.click();
    }
  };
  for (const tabs of synced) {
    tabs.addEventListener("click", (e) => {
      const tab = e.target.closest('[role="tab"]');
      if (!tab) return;
      const label = tab.textContent.trim();
      try {
        localStorage.setItem("dk-tabs:" + tabs.dataset.sync, label);
      } catch {}
      choose(tabs.dataset.sync, label);
    });
  }
  // Restore after Basecoat has initialized the tabs (it does so on DOMContentLoaded).
  document.addEventListener("DOMContentLoaded", () => {
    for (const sync of new Set(synced.map((t) => t.dataset.sync))) {
      let label = null;
      try {
        label = localStorage.getItem("dk-tabs:" + sync);
      } catch {}
      if (label) choose(sync, label);
    }
  });

  // TOC scrollspy: mark the last heading that scrolled past the top.
  const links = [...document.querySelectorAll(".dk-toc a[href^='#']")];
  const heads = links.map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1))));
  if (!heads.length || heads.includes(null)) return;
  const visible = new Set();
  const update = () => {
    let current = heads.find((h) => visible.has(h));
    if (!current) current = heads.filter((h) => h.getBoundingClientRect().top < 0).pop() || heads[0];
    // aria-current="" means false in ARIA, so set "true" explicitly.
    links.forEach((a, i) =>
      heads[i] === current ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current")
    );
  };
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) e.isIntersecting ? visible.add(e.target) : visible.delete(e.target);
      update();
    },
    { rootMargin: "-56px 0px -60% 0px" }
  );
  for (const h of heads) io.observe(h);
})();
