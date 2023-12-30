window.addEventListener("DOMContentLoaded", function() {
  const urlParams = new URLSearchParams(window.location.search);
  const query = urlParams.get("q");
  if (!query || !query.trim()) {
    return;
  }
  document.querySelectorAll("#page-links a").forEach(element => {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set("page", element.dataset.page);
    const url = `${window.location.origin}${window.location.pathname}?${urlParams.toString()}`;
    element.href = url;
  });
}, false);