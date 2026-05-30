// MK Auto - bildetaljside (dependency-free)
(function () {
  "use strict";

  /* ---- Header + mobile menu ---- */
  const header = document.getElementById("header");
  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }
  const toggle = document.getElementById("navToggle");
  const menu = document.getElementById("mobileMenu");
  if (toggle && menu) {
    const setMenu = (open) => {
      menu.classList.toggle("is-open", open);
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Lukk meny" : "Åpne meny");
    };
    toggle.addEventListener("click", () => setMenu(!menu.classList.contains("is-open")));
    menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
  }
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---- Gallery thumbs ---- */
  const main = document.getElementById("gmain");
  const thumbs = Array.from(document.querySelectorAll(".gthumb"));
  if (main && thumbs.length) {
    const select = (btn) => {
      main.src = btn.dataset.src;
      thumbs.forEach((t) => t.removeAttribute("aria-current"));
      btn.setAttribute("aria-current", "true");
    };
    thumbs.forEach((btn) => btn.addEventListener("click", () => select(btn)));
  }
})();
