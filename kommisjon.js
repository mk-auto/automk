// MK Auto - kommisjon & formidling page (toggle + scroll-drawn journey)
(function () {
  "use strict";

  /* responsibility toggle */
  const toggle = document.getElementById("toggle");
  if (toggle) {
    const rail = document.getElementById("rail");
    const nodeMk = document.getElementById("nodeMk");
    const nodeYou = document.getElementById("nodeYou");
    const states = Array.from(document.querySelectorAll(".state"));
    const set = (mode) => {
      toggle.classList.toggle("form", mode === "form");
      if (rail) rail.classList.toggle("form", mode === "form");
      if (nodeMk) nodeMk.classList.toggle("active", mode === "kom");
      if (nodeYou) nodeYou.classList.toggle("active", mode === "form");
      states.forEach((s) => { s.hidden = s.dataset.state !== mode; });
      toggle.querySelectorAll("button").forEach((b) =>
        b.setAttribute("aria-selected", String(b.dataset.mode === mode)));
    };
    toggle.querySelectorAll("button").forEach((b) =>
      b.addEventListener("click", () => set(b.dataset.mode)));
  }

  /* journey timeline */
  const tl = document.getElementById("timeline");
  if (tl) {
    const grow = document.getElementById("grow");
    const milestones = Array.from(tl.querySelectorAll(".milestone"));
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) {
      milestones.forEach((m) => m.classList.add("lit"));
      if (grow) grow.style.height = "100%";
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("lit"); });
      }, { threshold: 0.35, rootMargin: "0px 0px -12% 0px" });
      milestones.forEach((m) => io.observe(m));
      const onScroll = () => {
        const r = tl.getBoundingClientRect();
        const seen = Math.min(Math.max(window.innerHeight * 0.55 - r.top, 0), r.height);
        if (grow) grow.style.height = (seen / r.height * 100) + "%";
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
  }
})();
