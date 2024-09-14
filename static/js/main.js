document.addEventListener('DOMContentLoaded', function() {
    const ageButtons = document.querySelectorAll('.age-button');
    const shortDescription = document.getElementById('shortDescription');
    const detailDescription = document.getElementById('detailDescription');
    const problemsList = document.getElementById('problemsList');
    const benefitsList = document.getElementById('benefitsList');
    const quickOverview = document.getElementById('quickOverview');
    const reviewsList = document.getElementById('reviewsList');
    const ingredientsList = document.getElementById('ingredientsList');
    const usageInstructions = document.getElementById('usageInstructions');
    const productPrice = document.getElementById('productPrice');
    const productPriceBottom = document.getElementById('productPriceBottom');
    const productNameBottom = document.getElementById('productNameBottom');

    function updateContent(age) {
        const commonData = productData.společné_části;
        const personalizedData = productData.personalizované_části.find(item => item.věková_kategorie === age);

        if (personalizedData) {
            shortDescription.textContent = personalizedData.krátký_popis;
            detailDescription.textContent = personalizedData.detailní_popis;
            problemsList.innerHTML = personalizedData.marketingový_obsah.řeší_tyto_potíže.map(item => `<li>${item}</li>`).join('');
            benefitsList.innerHTML = personalizedData.marketingový_obsah.klíčové_benefity.map(item => `<li>${item}</li>`).join('');
            quickOverview.innerHTML = personalizedData.marketingový_obsah.rychlý_přehled.map(item => `<li>${item}</li>`).join('');
            reviewsList.innerHTML = personalizedData.recenze_zákazníků.map(review => `
                <div class="review">
                    <h4>${review.jméno} (${review.věk} let) - ${review.hodnocení}/5 hvězdiček</h4>
                    <p>${review.text}</p>
                </div>
            `).join('');

            ingredientsList.innerHTML = commonData.základní_informace.složení_a_účinky.map(item => `
                <li><strong>${item.složka}:</strong> ${item.účinek}</li>
            `).join('');
            usageInstructions.textContent = commonData.základní_informace.návod_k_použití;
            productPrice.textContent = `${commonData.základní_informace.cena.s_dph} Kč`;
            productPriceBottom.textContent = `${commonData.základní_informace.cena.s_dph} Kč`;
            productNameBottom.textContent = commonData.základní_informace.název_produktu;
        }
    }

    ageButtons.forEach(button => {
        button.addEventListener('click', () => {
            ageButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            updateContent(button.dataset.age);
        });
    });

    // Inicializace s první věkovou kategorií
    if (ageButtons.length > 0) {
        updateContent(ageButtons[0].dataset.age);
        ageButtons[0].classList.add('active');
    }
});

function setMainImage(url) {
    document.getElementById('productImageMain').src = url;
}