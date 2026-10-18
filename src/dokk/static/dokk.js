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

  // Search: Pagefind UI is loaded on first open; "/" or Ctrl/Cmd+K opens it.
  const dlg = document.getElementById("dk-search");
  if (dlg) {
    const bundle = dlg.dataset.bundle;
    let ready;
    const load = () =>
      (ready ||= new Promise((ok, fail) => {
        const css = document.createElement("link");
        css.rel = "stylesheet";
        css.href = bundle + "pagefind-ui.css";
        const js = document.createElement("script");
        js.src = bundle + "pagefind-ui.js";
        js.onload = () => {
          new PagefindUI({ element: "#dk-search-ui", bundlePath: bundle, baseUrl: dlg.dataset.base, showSubResults: true });
          ok();
        };
        js.onerror = fail;
        document.head.append(css, js);
      }));
    const open = () => {
      if (!dlg.open) dlg.showModal();
      load().then(() => dlg.querySelector("input")?.focus());
    };
    for (const b of document.querySelectorAll("[data-dk-search]")) b.addEventListener("click", open);
    document.addEventListener("keydown", (e) => {
      const typing = e.target.closest("input, textarea, select, [contenteditable]");
      if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing)) {
        e.preventDefault();
        open();
      }
    });
  }

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
