(function(){
  let items = window.NORTHSTAR_ITEMS || [];
  let loading = null;
  const basePath = window.NORTHSTAR_BASE_PATH || "";
  const q = document.getElementById("siteSearch");
  const box = document.getElementById("searchResults");
  if (!q || !box) return;
  function loadItems() {
    if (items.length) return Promise.resolve(items);
    if (!loading) {
      loading = fetch(basePath + "/assets/search-index.json")
        .then(response => response.ok ? response.json() : [])
        .then(data => { items = Array.isArray(data) ? data : []; return items; })
        .catch(() => []);
    }
    return loading;
  }
  q.addEventListener("input", async () => {
    const s = q.value.toLowerCase().trim();
    if (!s) {
      box.style.display = "none";
      box.innerHTML = "";
      return;
    }
    await loadItems();
    if (q.value.toLowerCase().trim() !== s) return;
    const r = items.filter(x => (x.title + " " + x.desc + " " + x.cat + " " + (x.keyword || "")).toLowerCase().includes(s)).slice(0, 8);
    box.innerHTML = r.map(x => `<a href="${basePath}/${x.slug}/"><strong>${x.title}</strong><small>${x.cat}: ${x.desc}</small></a>`).join("");
    box.style.display = r.length ? "block" : "none";
  });
})();
