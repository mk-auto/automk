// MK Auto - kontakt page: open-now status + today's hours highlight (progressive enhancement)
(function () {
  "use strict";

  // Opening hours in minutes from midnight, keyed by JS getDay() (0 = Sunday).
  var SCHEDULE = {
    1: [540, 1020], // Mon 09:00-17:00
    2: [540, 1020],
    3: [540, 1020],
    4: [540, 1020],
    5: [540, 1020],
    6: [600, 840],  // Sat 10:00-14:00
    0: null,        // Sun closed
  };

  var now = new Date();
  var day = now.getDay();
  var minutes = now.getHours() * 60 + now.getMinutes();
  var span = SCHEDULE[day];
  var isOpen = !!span && minutes >= span[0] && minutes < span[1];

  var status = document.getElementById("openStatus");
  if (status) {
    status.hidden = false;
    status.textContent = isOpen ? "Åpent nå" : "Stengt nå";
    status.classList.add(isOpen ? "status--open" : "status--closed");
  }

  // Highlight the row covering today.
  var rows = document.querySelectorAll(".hours-list li[data-days]");
  rows.forEach(function (li) {
    var days = li.getAttribute("data-days").split(",");
    if (days.indexOf(String(day)) !== -1) li.classList.add("is-today");
  });
})();
