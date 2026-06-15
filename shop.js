// MK Auto - bilbutikk (dependency-free)
(function () {
  "use strict";

  /* ---- Header + mobile menu (shared pattern) ---- */
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

  /* ---- Filtering state ---- */
  const grid = document.getElementById("grid");
  const cars = Array.from(grid.querySelectorAll(".scar"));
  const count = document.getElementById("count");
  const empty = document.getElementById("empty");
  const sortSel = document.getElementById("sort");
  const q = document.getElementById("q");
  const maxpris = document.getElementById("maxpris");
  const maxprisLabel = document.getElementById("maxprisLabel");
  const activePills = document.getElementById("activePills");
  const loadMore = document.getElementById("loadMore");
  const PAGE = 9;
  let shown = PAGE;

  const state = { brand: new Set(), body: new Set(), fuel: new Set(), gear: new Set(), q: "", maxpris: Number(maxpris.max) };
  const nf = new Intl.NumberFormat("nb-NO");

  /* chip toggles */
  document.querySelectorAll(".filters .chips").forEach((group) => {
    const key = group.dataset.filter;
    group.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = chip.dataset.val;
        const on = chip.getAttribute("aria-pressed") === "true";
        chip.setAttribute("aria-pressed", String(!on));
        if (on) state[key].delete(val); else state[key].add(val);
        shown = PAGE;
        apply();
      });
    });
  });

  q.addEventListener("input", () => { state.q = q.value.trim().toLowerCase(); shown = PAGE; apply(); });
  maxpris.addEventListener("input", () => {
    state.maxpris = Number(maxpris.value);
    const isMax = state.maxpris >= Number(maxpris.max);
    maxprisLabel.textContent = isMax ? "Ingen grense" : nf.format(state.maxpris) + " kr";
    shown = PAGE;
    apply();
  });
  sortSel.addEventListener("change", apply);

  /* clear */
  const clearBtn = document.getElementById("clearFilters");
  if (clearBtn) clearBtn.addEventListener("click", () => {
    state.brand.clear(); state.body.clear(); state.fuel.clear(); state.gear.clear();
    state.q = ""; state.maxpris = Number(maxpris.max);
    q.value = ""; maxpris.value = maxpris.max;
    maxprisLabel.textContent = "Ingen grense";
    document.querySelectorAll(".filters .chip[aria-pressed='true']").forEach((c) => c.setAttribute("aria-pressed", "false"));
    shown = PAGE;
    apply();
  });

  /* mobile filter toggle */
  const filterToggle = document.getElementById("filterToggle");
  const filterBody = document.getElementById("filterBody");
  if (filterToggle && filterBody) {
    filterToggle.addEventListener("click", () => {
      const open = filterBody.classList.toggle("open");
      filterToggle.setAttribute("aria-expanded", String(open));
      filterToggle.textContent = open ? "Skjul filter" : "Vis filter";
    });
  }

  function matches(car) {
    const d = car.dataset;
    if (state.brand.size && !state.brand.has(d.brand)) return false;
    if (state.body.size && !state.body.has(d.body)) return false;
    if (state.fuel.size && !state.fuel.has(d.fuel)) return false;
    if (state.gear.size && !state.gear.has(d.gear)) return false;
    if (Number(d.price) > state.maxpris) return false;
    if (state.q && !d.name.toLowerCase().includes(state.q)) return false;
    return true;
  }

  function sortCars(list) {
    const v = sortSel.value;
    const by = {
      "nyest": (a, b) => b.dataset.year - a.dataset.year || a.dataset.price - b.dataset.price,
      "pris-lav": (a, b) => a.dataset.price - b.dataset.price,
      "pris-hoy": (a, b) => b.dataset.price - a.dataset.price,
      "km-lav": (a, b) => a.dataset.km - b.dataset.km,
    }[v] || (() => 0);
    return list.slice().sort((a, b) => (a.dataset.sold - b.dataset.sold) || by(a, b));
  }

  function renderPills() {
    while (activePills.firstChild) activePills.removeChild(activePills.firstChild);
    const add = (key, val) => {
      const pill = document.createElement("span");
      pill.className = "apill";
      pill.appendChild(document.createTextNode(val));
      const x = document.createElement("button");
      x.type = "button";
      x.setAttribute("aria-label", "Fjern filter " + val);
      x.textContent = "×";
      x.addEventListener("click", () => {
        state[key].delete(val);
        const chip = document.querySelector(`.filters .chips[data-filter="${key}"] .chip[data-val="${CSS.escape(val)}"]`);
        if (chip) chip.setAttribute("aria-pressed", "false");
        shown = PAGE; apply();
      });
      pill.appendChild(x);
      activePills.appendChild(pill);
    };
    ["brand", "body", "fuel", "gear"].forEach((k) => state[k].forEach((v) => add(k, v)));
  }

  function apply() {
    const visible = sortCars(cars.filter(matches));
    visible.forEach((car) => grid.appendChild(car));
    cars.forEach((car) => car.classList.add("is-hidden"));
    visible.slice(0, shown).forEach((car) => car.classList.remove("is-hidden"));

    // "biler til salgs" counts only cars actually for sale (sold ones are shown, badged, at the end)
    count.textContent = visible.filter((car) => car.dataset.sold !== "1").length;
    empty.style.display = visible.length ? "none" : "";
    loadMore.parentElement.style.display = visible.length > shown ? "" : "none";
    renderPills();
  }

  loadMore.addEventListener("click", () => { shown += PAGE; apply(); });

  maxprisLabel.textContent = "Ingen grense";
  apply();
})();
