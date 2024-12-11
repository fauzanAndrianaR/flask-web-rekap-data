document.addEventListener("DOMContentLoaded", () => {
    const rowsPerPage = 10;
    const table = document.getElementById("data-table");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const pagination = document.getElementById("pagination");
    const prevButton = document.getElementById("prev-button");
    const nextButton = document.getElementById("next-button");
    const pageInfo = document.getElementById("page-info");
    const searchInput = document.getElementById("search-input");
    let currentPage = 1;
    let filteredRows = [...rows];

    function renderTable(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        tbody.innerHTML = "";
        filteredRows.slice(start, end).forEach(row => tbody.appendChild(row));
        updatePagination();
    }

    function updatePagination() {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        pageInfo.textContent = `Page ${currentPage}`;
        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === totalPages;
    }

    // Event listeners for pagination
    prevButton.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(currentPage);
        }
    });

    nextButton.addEventListener("click", () => {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable(currentPage);
        }
    });

    // Event listener for search
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        filteredRows = rows.filter(row => {
            return Array.from(row.cells).some(cell => 
                cell.textContent.toLowerCase().includes(query)
            );
        });
        currentPage = 1;
        renderTable(currentPage);
    });

    // Initial render
    renderTable(currentPage);
});
// JavaScript untuk mengubah navbar menjadi transparan saat scroll
window.onscroll = function() {
    toggleNavbarTransparency();
};

function toggleNavbarTransparency() {
    const navbar = document.querySelector('.navigation');
    if (window.scrollY > 0) {
        navbar.classList.add('transparent'); // Tambahkan class untuk transparan
    } else {
        navbar.classList.remove('transparent'); // Hapus class saat kembali ke posisi atas
    }
}
