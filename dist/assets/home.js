(function(){
  const filter = document.getElementById("categoryFilter");
  if (filter) {
    const cards = Array.from(document.querySelectorAll("[data-home-category]"));
    filter.addEventListener("input", () => {
      const query = filter.value.toLowerCase().trim();
      cards.forEach(card => {
        card.style.display = card.textContent.toLowerCase().includes(query) ? "" : "none";
      });
    });
  }
  document.addEventListener("click", event => {
    const key = event.target.closest("[data-sci-key]");
    if (!key) return;
    const input = document.getElementById("sciExpression");
    const run = document.getElementById("sciRun");
    if (!input) return;
    const value = key.getAttribute("data-sci-key");
    if (value === "C") {
      input.value = "";
      input.focus();
      return;
    }
    if (value === "Del") {
      input.value = input.value.slice(0, -1);
      input.focus();
      return;
    }
    if (value === "=") {
      if (run) run.click();
      return;
    }
    input.value += value;
    input.focus();
  });
})();
