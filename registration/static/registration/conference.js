document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById("myForm");
  function handleForm(event) {
    event.preventDefault();
    var data = new FormData(form);
    console.log(location.pathname);
    var match = location.pathname.match(/registration\/meet\/(\d+)\/team\/(\d+)\//);
    var meetId = match[1];
    var teamId = match[2];
    fetch(window.location.origin + `/registration/meet/${meetId}/team/${teamId}/save/`, {
      method: 'POST',
        body: new FormData(event.target),
      }).then(function (response) {
        if (response.ok) {
          return response.json();
        }
        return Promise.reject(response);
      }).then(function (data) {
        console.log(data);
      }).catch(function (error) {
        console.warn(error);
      });
  }
  form.addEventListener('submit', handleForm);
});
