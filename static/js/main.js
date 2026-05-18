// --- filtering ---
function filterFunction() {
  const filter = document.getElementById("input-search").value.toUpperCase();
  const tbChecked = document.getElementById("TB-checkbox").checked;
  const dsChecked = document.getElementById("DS-checkbox").checked;

  const rows = document.querySelectorAll("#full-table tr:not(.header)");

  rows.forEach(row => {
    const cells = row.querySelectorAll("td");

    // --- text search ---
    const textMatch = Array.from(cells).some(cell =>
      cell.textContent.toUpperCase().includes(filter)
    );

    // --- checkbox inclusion filter ---
    const type = row.getAttribute("data-type");

    let typeMatch;

    // If nothing selected → allow all
    if (!tbChecked && !dsChecked) {
      typeMatch = true;
    } else {
      typeMatch =
        (tbChecked && type === "Testbed") ||
        (dsChecked && type === "Dataset");
    }

    row.style.display = (textMatch && typeMatch) ? "" : "none";
  });
}

document.getElementById("TB-checkbox").addEventListener("change", filterFunction);
document.getElementById("DS-checkbox").addEventListener("change", filterFunction);


// --- column visibility ---
function updateColumnVisibility() {
  const table = document.getElementById("full-table");
  const headers = table.querySelectorAll("th");
  const rows = table.querySelectorAll("tr");

  headers.forEach((th, colIndex) => {
    const colName = th.getAttribute("data-col");
    const checkbox = document.querySelector(`.col-toggle[data-col="${colName}"]`);

    // If no checkbox exists, leave column visible
    if (!checkbox) return;

    const show = checkbox.checked;

    rows.forEach(row => {
      const cells = row.querySelectorAll("th, td");
      if (cells[colIndex]) {
        cells[colIndex].style.display = show ? "" : "none";
      }
    });
  });
}

document.querySelectorAll(".col-toggle").forEach(cb => {
  cb.addEventListener("change", updateColumnVisibility);
});


// --- sorting ---
let sortDirection = {};
let currentSortedCol = null;

document.querySelectorAll("#full-table th").forEach((th, index) => {
  th.style.cursor = "pointer";

  th.addEventListener("click", () => {
    sortTableByColumn(index, th);
    updateArrows(th, index);
  });
});

function sortTableByColumn(colIndex, th) {
  const table = document.getElementById("full-table");
  const rows = Array.from(table.querySelectorAll("tr:not(.header)"));

  const isNumber = th.getAttribute("data-type") === "number";

  sortDirection[colIndex] = !sortDirection[colIndex];
  const asc = sortDirection[colIndex];

  rows.sort((a, b) => {
    let aVal = a.children[colIndex]?.textContent.trim() || "";
    let bVal = b.children[colIndex]?.textContent.trim() || "";

    if (isNumber) {
      aVal = parseFloat(aVal) || 0;
      bVal = parseFloat(bVal) || 0;
    } else {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (aVal < bVal) return asc ? -1 : 1;
    if (aVal > bVal) return asc ? 1 : -1;
    return 0;
  });

  rows.forEach(row => table.appendChild(row));
}

function updateArrows(activeTh, colIndex) {
  const headers = document.querySelectorAll("#full-table th");

  headers.forEach((th, i) => {
    const span = th.querySelector("span");
    if (!span) return;

    // reset text (remove arrows)
    span.textContent = span.textContent.replace(/[\u2191\u2193]/g, "").trim();

    // add arrow only to active column
    if (i === colIndex) {
      const arrow = sortDirection[colIndex] ? " ↑" : " ↓";
      span.textContent += arrow;
    }
  });

  currentSortedCol = colIndex;
}

// default ordering 
document.addEventListener("DOMContentLoaded", () => {
  const defaultColIndex = 1; // Class
  const th = document.querySelectorAll("#full-table th")[defaultColIndex];

  // force initial direction (true = ascending, false = descending)
  sortDirection[defaultColIndex] = false;
  sortTableByColumn(defaultColIndex, th);
  updateArrows(th, defaultColIndex);
});