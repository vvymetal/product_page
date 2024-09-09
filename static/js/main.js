document.addEventListener('DOMContentLoaded', function() {
    function changeAgeCategory(category) {
        fetch(`/api/product/product1?age_category=${category}`)
            .then(response => response.json())
            .then(data => updateProductInfo(data, category));
    }

    function updateProductInfo(data, category) {
        const personalizedContent = data.personalizované_části.personalizovaný_obsah[category];
        document.getElementById('product-description').textContent = personalizedContent.krátký_popis;
        
        // Aktualizace popisu produktu
        document.getElementById('description-content').textContent = data.společné_části.detailní_popis;

        // Aktualizace složení a účinků
        const ingredientsContent = document.getElementById('ingredients-content');
        ingredientsContent.innerHTML = data.společné_části.složení_a_účinky.map(item => 
            `<li><strong>${item.složka}:</strong> ${item.účinek}</li>`
        ).join('');

        // Aktualizace návodu k použití
        document.getElementById('usage-content').textContent = data.společné_části.návod_k_použití;

        // Aktualizace Tiande Lifestyle sekce
        const lifestyleContent = document.getElementById('lifestyle-content');
        lifestyleContent.innerHTML = `
            <p>${personalizedContent.tiande_lifestyle_text}</p>
            <ul>
                ${personalizedContent.klíčové_hodnoty.map(value => `<li>${value}</li>`).join('')}
            </ul>
        `;

        // Aktualizace recenzí
        const reviewsContent = document.getElementById('reviews-content');
        reviewsContent.innerHTML = personalizedContent.recenze_zákazníků.map(review => `
            <div class="review">
                <h4>${review.jméno} (${review.věk} let)</h4>
                <p>Hodnocení: ${review.hodnocení}/5</p>
                <p>${review.text}</p>
            </div>
        `).join('');
    }

    document.querySelectorAll('.age-category-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.age-category-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            changeAgeCategory(this.dataset.category);
        });
    });

    // Inicializace s výchozí věkovou kategorií
    changeAgeCategory('18-29');
});