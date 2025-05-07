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
  const astContainer = document.getElementById("ast");
  renderASTTree(data.ast);

  // Hide the waiting messages
  document.getElementById("tac-waiting").style.display = "none";
  document.getElementById("opt_tac-waiting").style.display = "none";

  document.getElementById("tac").innerText = (data.tac || []).join("\n") || "No TAC generated.";
  document.getElementById("opt_tac").innerText = (data.optimized_tac || []).join("\n") || "No Optimized TAC.";
}

function renderASTTree(astData) {
  const svg = d3.select("#ast");
  svg.selectAll("*").remove(); // clear previous

  const width = svg.node().getBoundingClientRect().width;
  const height = +svg.attr("height");

  const root = d3.hierarchy(astData, d => {
    const children = [];
    for (const key in d) {
      if (key !== "type" && typeof d[key] === "object") {
        const child = d[key];
        if (Array.isArray(child)) {
          child.forEach(c => children.push({ type: key, ...c }));
        } else if (child !== null) {
          children.push({ type: key, ...child });
        }
      }
    }
    return children.length ? children : null;
  });

  const treeLayout = d3.tree().size([width - 40, height - 40]);
  const treeData = treeLayout(root);

  const g = svg.append("g").attr("transform", "translate(20,20)");

  // Draw links
  g.selectAll(".link")
    .data(treeData.links())
    .enter()
    .append("line")
    .attr("class", "link")
    .attr("stroke", "#cbd5e1")
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  // Draw nodes
  const node = g.selectAll(".node")
    .data(treeData.descendants())
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", d => `translate(${d.x},${d.y})`);

  node.append("circle")
    .attr("r", 16)
    .attr("fill", "#6366f1");

  node.append("text")
    .attr("dy", 4)
    .attr("text-anchor", "middle")
    .attr("fill", "white")
    .style("font-size", "10px")
    .text(d => d.data.value);
    
}

