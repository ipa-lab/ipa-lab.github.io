// Cycles through the home page's research questions, one at a time.
// Pauses while the pointer or keyboard focus is inside, and has prev/next/
// pause controls. With prefers-reduced-motion it starts paused (no auto-advance).
(function () {
  const root = document.getElementById("questions");
  if (!root) return;
  const items = [...root.querySelectorAll(".question-list > li")];
  if (items.length < 2) return;
  const controls = root.querySelector(".question-controls");
  const count = root.querySelector('[data-q="count"]');
  const pauseBtn = root.querySelector('[data-q="pause"]');
  const INTERVAL = 5000;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let index = 0;
  let timer = null;
  let paused = reduced; // user's choice (pause button / reduced motion)
  let hovering = false;

  function show(next) {
    const prev = items[index];
    index = (next + items.length) % items.length;
    if (prev !== items[index]) {
      prev.classList.remove("current");
      prev.classList.add("leaving");
      setTimeout(() => prev.classList.remove("leaving"), 500);
    }
    items.forEach((li, i) => li.toggleAttribute("aria-hidden", i !== index));
    items[index].classList.add("current");
    count.textContent = index + 1 + " / " + items.length;
  }

  function schedule() {
    clearTimeout(timer);
    if (!paused && !hovering) timer = setTimeout(() => { show(index + 1); schedule(); }, INTERVAL);
  }

  function setPaused(value) {
    paused = value;
    pauseBtn.textContent = paused ? "play" : "pause";
    pauseBtn.setAttribute("aria-label", paused ? "Play" : "Pause");
    schedule();
  }

  root.querySelector('[data-q="next"]').addEventListener("click", () => { show(index + 1); schedule(); });
  root.querySelector('[data-q="prev"]').addEventListener("click", () => { show(index - 1); schedule(); });
  pauseBtn.addEventListener("click", () => setPaused(!paused));

  // Hold still while someone is reading or about to click a paper link.
  root.addEventListener("pointerenter", () => { hovering = true; schedule(); });
  root.addEventListener("pointerleave", () => { hovering = false; schedule(); });
  // Keyboard focus pauses too; a mouse click on next/prev should not.
  root.addEventListener("focusin", (e) => {
    if (e.target.matches(":focus-visible")) { hovering = true; schedule(); }
  });
  root.addEventListener("focusout", (e) => {
    if (!root.contains(e.relatedTarget)) { hovering = false; schedule(); }
  });
  document.addEventListener("visibilitychange", () => (document.hidden ? clearTimeout(timer) : schedule()));

  root.classList.add("cycling");
  controls.hidden = false;
  show(0);
  setPaused(paused);
})();
