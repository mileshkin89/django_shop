// per-page-select.js

document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("perPageSelect");
  if (!select) return;

  const defaultPerPage = "16";
  const defaultPage = "1";
  const storageKey = "catalog_per_page";

  const url = new URL(window.location.href);
  const params = url.searchParams;

  let perPage = params.get("per_page");
  let page = params.get("page");

  const storedPerPage = localStorage.getItem(storageKey);

  if (!perPage) {
    perPage = storedPerPage || defaultPerPage;
    params.set("per_page", perPage);
  }

  if (!page) {
    params.set("page", defaultPage);
  }


  // If the URL has changed, we update it without restarting.
  const newUrl = `${url.pathname}?${params.toString()}`;
  if (newUrl !== window.location.href) {
    window.history.replaceState({}, "", newUrl);
  }

  // Set the current value of the selector
  select.value = perPage;

  // Handling selector changes
  select.addEventListener("change", function () {
    const newPerPage = select.value;
    localStorage.setItem(storageKey, newPerPage);

    params.set("per_page", newPerPage);
    params.set("page", "1");

    const newUrl = `${url.pathname}?${params.toString()}`;
    window.location.href = newUrl;
  });
});

