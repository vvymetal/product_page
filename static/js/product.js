function renderPersonalizedContent(ageCategory) {
    const content = window.productData.personalizované_části.find(p => p.věková_kategorie === ageCategory);
    if (content) {
        // Klíčové benefity
        const benefitsList = document.getElementById('benefits-list');
        benefitsList.innerHTML = content.marketingový_obsah.klíčové_benefity.map(benefit => `<li>${benefit}</li>`).join('');

        // Popis produktu
        document.getElementById('detailed-description').textContent = content.detailní_popis;

        // Recenze zákazníků
        const reviewsList = document.getElementById('reviews-list');
        reviewsList.innerHTML = content.recenze_zákazníků.map(review => `
            <div class="review-item">
                <div class="review-data">
                    <div class="review-data-user-wrapper">
                        <div class="review-avatar"></div>
                        <div class="review-data-user">
                            <div class="review-stars review-stars-${review.hodnocení}">
                                ${'<i class="fc icons_star_full"></i>'.repeat(review.hodnocení)}
                            </div>
                            ${review.jméno}<br>
                            <span>${review.věk} let</span>
                        </div>
                    </div>
                </div>
                <div class="review-text">
                    <p class="summary">${review.text}</p>
                </div>
            </div>
        `).join('');

        // Často kladené otázky
        const faqList = document.getElementById('faq-list');
        faqList.innerHTML = content.často_kladené_otázky.map(faq => `
            <li><strong>${faq.otázka}</strong><br>${faq.odpověď}</li>
        `).join('');

        // Nakupováno společně
        const boughtTogetherList = document.getElementById('bought-together-list');
        if (content.často_kupováno_společně) {
            boughtTogetherList.innerHTML = content.často_kupováno_společně.map(product => `<li>${product}</li>`).join('');
        } else {
            boughtTogetherList.innerHTML = '<li>Pro tuto věkovou kategorii nejsou k dispozici žádné údaje o společných nákupech.</li>';
        }

        // Doporučené produkty
        const recommendedList = document.getElementById('recommended-list');
        recommendedList.innerHTML = content.doporučené_produkty.map(product => `<li>${product}</li>`).join('');

        // Aktualizace TianDe Lifestyle textu
        const tiandeLifestyle = document.getElementById('tiande-lifestyle-text');
        if (content.tiande_lifestyle_text) {
            tiandeLifestyle.textContent = content.tiande_lifestyle_text;
        }
    }
}

function renderCommonContent() {
    const commonData = window.productData.společné_části.základní_informace;
    
    // Složení a účinky
    const ingredientsList = document.getElementById('ingredients-list');
    ingredientsList.innerHTML = commonData.složení_a_účinky.map(item => 
        `<li><strong>${item.složka}:</strong> ${item.účinek}</li>`
    ).join('');

    // Návod k použití
    document.getElementById('usage-text').textContent = commonData.návod_k_použití;
}

function changeMainImage(imageUrl) {
    document.getElementById('main-image').src = imageUrl;
}

function initializeAgeCategoryButtons() {
    const ageButtons = document.querySelectorAll('.age-button');
    ageButtons.forEach(button => {
        button.addEventListener('click', function() {
            ageButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            renderPersonalizedContent(this.dataset.age);
        });
    });

    // Inicializace s první věkovou kategorií
    if (ageButtons.length > 0) {
        ageButtons[0].click();
    }
}

function initializeGallery() {
    const thumbnails = document.querySelectorAll('.product-thumbnail img');
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            changeMainImage(this.src);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeAgeCategoryButtons();
    initializeGallery();
    renderCommonContent();

    // Generování náhodného počtu hodnocení
    const reviewsCount = document.querySelector('.reviews-count');
    const randomCount = Math.floor(Math.random() * (350 - 50 + 1)) + 50;
    reviewsCount.textContent = `${randomCount}x hodnoceno`;
});