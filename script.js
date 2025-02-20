const CSV_URL = "amazon_products.csv";

document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#product-table tbody");

    // Add a unique query parameter to the CSV URL to prevent caching
    const uniqueUrl = `${CSV_URL}?t=${new Date().getTime()}`;

    fetch(uniqueUrl)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to fetch CSV: ${response.status}`);
            }
            return response.text();
        })
        .then((csvText) => {
            Papa.parse(csvText, {
                header: true,
                skipEmptyLines: true,
                complete: (results) => {
                    const data = results.data;

                    // Clear old table rows
                    tableBody.innerHTML = "";

                    // Populate the table
                    data.forEach((row, index) => {
                        const tr = document.createElement("tr");

                        // Add serial number
                        const serialNumberCell = document.createElement("td");
                        serialNumberCell.textContent = index + 1;
                        tr.appendChild(serialNumberCell);

                        // Create columns for each key in the row
                        for (const key in row) {
                            const td = document.createElement("td");

                            // Add hyperlinks for the "Link" column
                            if (key === "Link") {
                                const link = document.createElement("a");
                                link.href = row[key];
                                link.textContent = "View on Amazon";
                                link.target = "_blank";
                                td.appendChild(link);
                            } else {
                                td.textContent = row[key];
                            }

                            tr.appendChild(td);
                        }

                        tableBody.appendChild(tr);
                    });
                },
            });
        })
        .catch((error) => {
            console.error("Error fetching or parsing CSV:", error);
        });
});
