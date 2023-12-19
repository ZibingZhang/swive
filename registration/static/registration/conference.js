document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById("myForm");
  function handleForm(event) {
    event.preventDefault();
    var data = new FormData(form);
    fetch(window.location.origin + '/registration/signup/meet/highschool/conference/save', {
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
