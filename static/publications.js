// Client-side filtering for the publications page. The page is complete
// without this script; it only reveals and wires up the filter controls.
(function () {
  const filters = document.getElementById("pub-filters");
  if (!filters) return;
  const search = document.getElementById("pub-search");
  const chips = filters.querySelectorAll("[data-filter]");
  const count = document.getElementById("pub-count");
  const empty = document.getElementById("pub-empty");
  const groups = document.querySelectorAll("[data-year-group]");
  let type = "all";

  function apply() {
    const terms = search.value.toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    groups.forEach((group) => {
      let visible = 0;
      group.querySelectorAll(".pub").forEach((pub) => {
        const text = pub.dataset.search;
        const match = (type === "all" || pub.dataset.type === type) &&
          terms.every((t) => text.includes(t));
        pub.hidden = !match;
        if (match) visible++;
      });
      group.hidden = visible === 0;
      shown += visible;
    });
    count.textContent = shown === 1 ? "1 publication" : shown + " publications";
    empty.hidden = shown !== 0;
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      type = chip.dataset.filter;
      chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      apply();
    });
  });
  search.addEventListener("input", apply);
  filters.hidden = false;
})();
