async function compileExpr() {
  const code = document.getElementById("input").value;
  const res = await fetch('/compile', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ code })
  });

  // Get the response from the backend
  const data = await res.json();

  // Display error if any
  if (data.error) {
    document.getElementById("tac").innerText = `Error: ${data.error}`;
    document.getElementById("opt_tac").innerText = "";
    return;
  }

  // Update the output in the frontend
  renderASTTree(data.ast);

  // Clear waiting messages
  document.getElementById("tac").innerText = "";
  document.getElementById("opt_tac").innerText = "";

  // Display original and processed expressions
  let tacOutput = `Original: ${data.original_expr}\n`;
  if (data.processed_expr && data.original_expr !== data.processed_expr) {
    tacOutput += `Processed: ${data.processed_expr}\n\n`;
  } else {
    tacOutput += "\n";
  }

  // Display TAC
  if (data.tac && data.tac.length > 0) {
    tacOutput += data.tac.join("\n");
    document.getElementById("tac").innerText = tacOutput;
  } else {
    document.getElementById("tac").innerText = tacOutput + "No TAC generated.";
  }

  // Display optimized TAC
  if (data.optimized_tac && data.optimized_tac.length > 0) {
    document.getElementById("opt_tac").innerText = data.optimized_tac.join("\n");
  } else {
    document.getElementById("opt_tac").innerText = "No Optimized TAC.";
  }
}

function renderASTTree(astData) {
  const svg = d3.select("#ast");
  svg.selectAll("*").remove(); // clear previous

  const width = svg.node().getBoundingClientRect().width;
  const height = svg.node().getBoundingClientRect().height;

  // Create a hierarchy from the AST data
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

  // Use more compact spacing for the tree layout
  const treeLayout = d3.tree()
    .size([width * 0.8, height * 0.8]) // Make tree use less space
    .separation((a, b) => (a.parent === b.parent ? 1 : 1.2)); // Reduce separation between nodes
  
  const treeData = treeLayout(root);

  // Center the tree in the SVG
  const g = svg.append("g")
    .attr("transform", `translate(${width * 0.1}, ${height * 0.1})`);

  // Draw links
  g.selectAll(".link")
    .data(treeData.links())
    .enter()
    .append("line")
    .attr("class", "link")
    .attr("stroke", "#8b5cf6")
    .attr("stroke-width", 1.5)
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
    .attr("r", 12) // Smaller circles
    .attr("fill", "#6d28d9")
    .attr("stroke", "#8b5cf6")
    .attr("stroke-width", 1.5);

  node.append("text")
    .attr("dy", 4)
    .attr("text-anchor", "middle")
    .attr("fill", "white")
    .style("font-size", "8px") // Smaller text
    .style("font-weight", "bold")
    .text(d => d.data.value || d.data.type);
}

async function randomizeExpr() {
  try {
    const response = await fetch('/random-expression');
    const data = await response.json();
    
    if (data.expression) {
      document.getElementById("input").value = data.expression;
      // Automatically compile the expression
      compileExpr();
    }
  } catch (error) {
    console.error("Error fetching random expression:", error);
  }
}

