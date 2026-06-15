// MK Auto - FormSubmit AJAX submit with inline success (progressive enhancement).
// Forms tagged `.js-fsajax` are intercepted and sent in the background so the
// visitor never leaves the page. Without JS the form does a normal POST to its
// `action` (the standard FormSubmit endpoint) and lands on the _next page.
// NOTE: file uploads are NOT sent via AJAX — the Selg/Innbytte photo forms use a
// plain (non-AJAX) submit instead, so they are deliberately not tagged here.
(function () {
  "use strict";

  // Selection chips (homepage finder) aren't real inputs — read their pressed
  // state and add them to the payload so the enquiry includes the choices.
  var GROUP_LABELS = { brand: "Merke", body: "Karosseri", fuel: "Drivstoff", gear: "Girkasse" };

  function collectChips(form, payload) {
    form.querySelectorAll("[data-group]").forEach(function (grp) {
      var picked = Array.prototype.slice
        .call(grp.querySelectorAll('.chip[aria-pressed="true"]'))
        .map(function (b) { return b.textContent.trim(); });
      if (picked.length) {
        var key = GROUP_LABELS[grp.getAttribute("data-group")] || grp.getAttribute("data-group");
        payload[key] = picked.join(", ");
      }
    });
  }

  function ajaxUrl(form) {
    // https://formsubmit.co/<email>  ->  https://formsubmit.co/ajax/<email>
    return form.getAttribute("action").replace("formsubmit.co/", "formsubmit.co/ajax/");
  }

  // Build the success card with safe DOM methods (no innerHTML).
  function buildDone(form) {
    var done = document.createElement("div");
    done.className = "fs-done";
    done.setAttribute("role", "status");
    done.setAttribute("aria-live", "polite");

    var mark = document.createElement("div");
    mark.className = "fs-done__mark";
    mark.setAttribute("aria-hidden", "true");
    mark.textContent = "✓"; // ✓
    done.appendChild(mark);

    var h = document.createElement("h3");
    var b = document.createElement("b");
    b.textContent = "Takk! ";
    h.appendChild(b);
    h.appendChild(document.createTextNode("Meldingen er sendt."));
    done.appendChild(h);

    var p = document.createElement("p");
    p.textContent =
      form.getAttribute("data-done-msg") || "Vi tar kontakt, vanligvis innen én arbeidsdag.";
    done.appendChild(p);
    return done;
  }

  function showDone(form) {
    var done = form.parentNode.querySelector(".fs-done");
    if (!done) {
      done = buildDone(form);
      form.parentNode.insertBefore(done, form.nextSibling);
    }
    form.hidden = true;
    done.classList.add("is-on");
    done.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function showError(form, btn, label) {
    if (btn) { btn.disabled = false; btn.textContent = label; }
    var err = form.querySelector(".fs-error");
    if (!err) {
      err = document.createElement("p");
      err.className = "fs-error";
      err.setAttribute("role", "alert");
      (btn && btn.parentNode ? btn.parentNode : form).appendChild(err);
    }
    err.textContent = "Beklager, noe gikk galt. Prøv igjen, eller ring oss på 950 93 215.";
  }

  document.querySelectorAll("form.js-fsajax").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      // Honeypot: if the hidden field is filled, silently pretend success.
      var honey = form.querySelector('[name="_honey"]');
      if (honey && honey.value) { showDone(form); return; }

      var payload = {};
      new FormData(form).forEach(function (value, key) {
        if (value instanceof File) return;            // never AJAX-post files
        if (payload[key] !== undefined) {             // repeated names -> join
          payload[key] = payload[key] + ", " + value;
        } else {
          payload[key] = value;
        }
      });
      collectChips(form, payload);

      var btn = form.querySelector('[type="submit"]');
      var label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sender …"; }

      fetch(ajaxUrl(form), {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data && String(data.success) === "true") {
            showDone(form);
          } else {
            throw new Error((data && data.message) || "Innsending feilet");
          }
        })
        .catch(function () { showError(form, btn, label); });
    });
  });
})();
