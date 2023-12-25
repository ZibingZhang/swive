document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById("meet-entries");
  function handleForm(event) {
    event.preventDefault();
    const match = location.pathname.match(/registration\/meet\/(\d+)\/team\/(\d+)\//);
    const meetId = match[1];
    const teamId = match[2];
    fetch(window.location.origin + `/registration/meet/${meetId}/team/${teamId}/save/`, {
      method: 'POST',
        body: new FormData(event.target),
      }).then(function (response) {
        if (response.ok) {
          console.log(response.json());
        }
        return Promise.reject(response);
      }).catch(error => {
        console.warn(error);
      });
  }
  form.addEventListener('submit', handleForm);
});

/* global bootstrap: false */
(function () {
  'use strict'
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()
