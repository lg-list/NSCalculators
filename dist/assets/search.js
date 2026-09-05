(function(){
  const items = window.NORTHSTAR_ITEMS || [];
  const basePath = window.NORTHSTAR_BASE_PATH || "";
  const q = document.getElementById("siteSearch");
  const box = document.getElementById("searchResults");
  if (!q || !box) return;
  q.addEventListener("input", () => {
    const s = q.value.toLowerCase().trim();
    if (!s) {
      box.style.display = "none";
      box.innerHTML = "";
      return;
    }
    const r = items.filter(x => (x.title + " " + x.desc + " " + x.cat + " " + (x.keyword || "")).toLowerCase().includes(s)).slice(0, 8);
    box.innerHTML = r.map(x => `<a href="${basePath}/${x.slug}/"><strong>${x.title}</strong><small>${x.cat}: ${x.desc}</small></a>`).join("");
    box.style.display = r.length ? "block" : "none";
  });
})();
