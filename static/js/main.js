document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Property filtering
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filterProperties();
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

function filterProperties() {
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const minSize = document.getElementById('minSize').value;

    const properties = document.querySelectorAll('.property-card');
    
    properties.forEach(property => {
        const price = parseInt(property.dataset.price);
        const size = parseInt(property.dataset.size);
        
        let visible = true;
        
        if (minPrice && price < minPrice) visible = false;
        if (maxPrice && price > maxPrice) visible = false;
        if (minSize && size < minSize) visible = false;
        
        property.style.display = visible ? 'block' : 'none';
    });
}
