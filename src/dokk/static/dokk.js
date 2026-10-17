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
