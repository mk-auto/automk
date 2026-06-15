// MK Auto - cookie consent + consent-gated Google Analytics (GDPR/ePrivacy).
// Google Analytics is NOT loaded until the visitor clicks "Godta". The choice is
// stored in localStorage; an "Informasjonskapsler" link in the footer reopens the
// banner so the visitor can change or withdraw consent at any time.
(function () {
  "use strict";

  // ── Config ───────────────────────────────────────────────────────────────
  var GA_ID = "G-XXXXXXXXXX";      // MK Auto GA4 Measurement ID — set this to go live
  var KEY = "mkauto-consent";       // localStorage: "granted" | "denied"

  function gaConfigured() {
    return GA_ID && GA_ID.indexOf("XXXX") === -1;
  }

  // ── Google Analytics (loaded only after consent) ─────────────────────────
  function loadGA() {
    if (!gaConfigured() || window.__mkGaLoaded) return;
    window.__mkGaLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID, { anonymize_ip: true });
  }

  function readConsent() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function writeConsent(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
    if (v === "granted") loadGA();
  }

  // ── Banner ────────────────────────────────────────────────────────────────
  function hideBanner(b) {
    b.classList.remove("is-in");
    setTimeout(function () { if (b.parentNode) b.parentNode.removeChild(b); }, 320);
  }

  function showBanner() {
    if (document.getElementById("cookieBanner")) return;

    var b = document.createElement("div");
    b.id = "cookieBanner";
    b.className = "cookie-banner";
    b.setAttribute("role", "dialog");
    b.setAttribute("aria-label", "Informasjonskapsler");

    var p = document.createElement("p");
    p.className = "cookie-banner__text";
    p.textContent =
      "Vi bruker informasjonskapsler til anonym statistikk (Google Analytics) " +
      "for å gjøre nettsiden bedre. Du velger selv.";

    var actions = document.createElement("div");
    actions.className = "cookie-banner__actions";

    var decline = document.createElement("button");
    decline.type = "button";
    decline.className = "btn btn--ghost cookie-btn";
    decline.textContent = "Avslå";
    decline.addEventListener("click", function () { writeConsent("denied"); hideBanner(b); });

    var accept = document.createElement("button");
    accept.type = "button";
    accept.className = "btn btn--accent cookie-btn";
    accept.textContent = "Godta";
    accept.addEventListener("click", function () { writeConsent("granted"); hideBanner(b); });

    actions.appendChild(decline);
    actions.appendChild(accept);
    b.appendChild(p);
    b.appendChild(actions);
    document.body.appendChild(b);
    requestAnimationFrame(function () { b.classList.add("is-in"); });
  }

  // Footer "Informasjonskapsler" link — lets visitors change their choice later.
  function injectManageLink() {
    var legal = document.querySelector(".footer-bottom .legal");
    if (!legal || document.getElementById("cookieManage")) return;
    var a = document.createElement("a");
    a.id = "cookieManage";
    a.href = "#";
    a.textContent = "Informasjonskapsler";
    a.addEventListener("click", function (e) { e.preventDefault(); showBanner(); });
    legal.appendChild(a);
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  var saved = readConsent();
  if (saved === "granted") loadGA();
  injectManageLink();
  if (saved !== "granted" && saved !== "denied") showBanner();
})();
