async function compileExpr() {
  const code = document.getElementById("input").value;
  const res = await fetch('/compile', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ code })
  });

  // Get the response from the backend
  const data = await res.json();

  // Update the output in the frontend
  document.getElementById("ast").innerText = data.ast || "No AST available.";
  document.getElementById("tac").innerText = (data.tac || []).join("\n") || "No TAC generated.";
  document.getElementById("opt_tac").innerText = (data.optimized_tac || []).join("\n") || "No Optimized TAC.";
}
