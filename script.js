// MK Auto - interactions (dependency-free)
(function () {
  "use strict";
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Header solid-on-scroll ---- */
  const header = document.getElementById("header");
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 24);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- Mobile menu ---- */
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("mobileMenu");
  const setMenu = (open) => {
    menu.classList.toggle("is-open", open);
    toggle.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Lukk meny" : "Åpne meny");
  };
  toggle.addEventListener("click", () => setMenu(!menu.classList.contains("is-open")));
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  /* ---- Scroll reveals ---- */
  const reveals = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach((el) => el.classList.add("in-view"));
  } else {
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add("in-view"); obs.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach((el) => io.observe(el));
  }

  /* ---- Services accordion: click/keyboard opens a panel (hover handled by CSS) ---- */
  const panels = document.querySelectorAll("#accordion .panel");
  const openPanel = (p) => { panels.forEach((x) => x.classList.remove("is-open")); p.classList.add("is-open"); };
  panels.forEach((p) => {
    p.addEventListener("click", () => openPanel(p));
    p.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openPanel(p); }
    });
  });

  /* ---- Cars scroll rail: arrows, drag, counter, progress ---- */
  const track = document.getElementById("carTrack");
  if (track) {
    const cards = track.querySelectorAll(".ecar");
    const fill = document.getElementById("carFill");
    const prev = document.getElementById("carPrev");
    const next = document.getElementById("carNext");
    const step = () => cards[0].getBoundingClientRect().width + 24;
    next.addEventListener("click", () => track.scrollBy({ left: step(), behavior: reduce ? "auto" : "smooth" }));
    prev.addEventListener("click", () => track.scrollBy({ left: -step(), behavior: reduce ? "auto" : "smooth" }));
    // continuous scroll-progress thumb (no numbers): width = visible fraction, x = scroll position
    const update = () => {
      const max = track.scrollWidth - track.clientWidth;
      const frac = max > 0 ? track.scrollLeft / max : 0;
      const thumb = max > 0 ? Math.max(14, (track.clientWidth / track.scrollWidth) * 100) : 100;
      fill.style.width = thumb + "%";
      fill.style.transform = "translateX(" + (frac * (100 - thumb) / thumb * 100) + "%)";
      prev.toggleAttribute("disabled", track.scrollLeft <= 4);
      next.toggleAttribute("disabled", track.scrollLeft >= max - 4);
    };
    track.addEventListener("scroll", update, { passive: true });
    update();
    // drag to scroll
    let down = false, sx = 0, sl = 0, moved = false;
    track.addEventListener("pointerdown", (e) => { down = true; moved = false; sx = e.pageX; sl = track.scrollLeft; });
    track.addEventListener("pointermove", (e) => {
      if (!down) return;
      if (Math.abs(e.pageX - sx) > 4) moved = true;
      track.scrollLeft = sl - (e.pageX - sx);
    });
    const end = () => { down = false; };
    track.addEventListener("pointerup", end);
    track.addEventListener("pointerleave", end);
    // prevent click navigation after a drag
    track.querySelectorAll("a").forEach((a) => a.addEventListener("click", (e) => { if (moved) e.preventDefault(); }));
  }

  /* ---- Finder: chip toggles + budget label ---- */
  document.querySelectorAll(".finder .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const on = chip.getAttribute("aria-pressed") === "true";
      chip.setAttribute("aria-pressed", String(!on));
    });
  });
  const budget = document.getElementById("budsjett");
  const budgetLabel = document.getElementById("budgetLabel");
  if (budget && budgetLabel) {
    budget.addEventListener("input", () => {
      budgetLabel.textContent = Number(budget.value).toLocaleString("nb-NO") + " kr";
    });
  }

  /* ---- Footer year ---- */
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();
})();
