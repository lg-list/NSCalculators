(function(){
  function normalize(value) {
    return value
      .replace(/\bpi\b/gi, "Math.PI")
      .replace(/\be\b/g, "Math.E")
      .replace(/\bsqrt\(/gi, "Math.sqrt(")
      .replace(/\bsin\(/gi, "Math.sin(")
      .replace(/\bcos\(/gi, "Math.cos(")
      .replace(/\btan\(/gi, "Math.tan(")
      .replace(/\blog\(/gi, "Math.log10(")
      .replace(/\bln\(/gi, "Math.log(")
      .replace(/(\d+(?:\.\d+)?)%/g, "($1/100)")
      .replace(/\^/g, "**");
  }
  function run() {
    const input = document.getElementById("sciExpression");
    const output = document.getElementById("sciResult");
    if (!input || !output) return;
    try {
      const expr = normalize(input.value);
      if (!/^[0-9+\-*/().,\sMathPIElogsqrtincota%*]+$/.test(expr)) throw new Error("Unsupported expression");
      const result = Function(`"use strict"; return (${expr})`)();
      output.textContent = Number.isFinite(result) ? result.toLocaleString("en-US", { maximumFractionDigits: 10 }) : "Check the expression";
    } catch (error) {
      output.textContent = "Check the expression";
    }
  }
  document.addEventListener("click", event => {
    if (event.target && event.target.id === "sciRun") run();
  });
  document.addEventListener("keydown", event => {
    if (event.target && event.target.id === "sciExpression" && event.key === "Enter") run();
  });
})();
