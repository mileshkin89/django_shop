// product_edit.js

document.addEventListener('DOMContentLoaded', function() {
    const masterSelect = document.querySelector('#id_master_category');
    const subSelect = document.querySelector('#id_sub_category');
    const articleSelect = document.querySelector('#id_article_type');

    /**
     * Load subcategories for a given master category.
     * @param {number|string} masterId
     * @param {boolean} autoSelectFirst
     * @returns {Promise<void>} - resolves when the subcategories are loaded
     */
    function loadSubCategories(masterId, autoSelectFirst = true) {
        if (!masterId) {
            subSelect.innerHTML = '<option value="">---------</option>';
            articleSelect.innerHTML = '<option value="">---------</option>';
            return Promise.resolve();
        }

        if (autoSelectFirst) {
            subSelect.innerHTML = '<option value="">---------</option>';
            articleSelect.innerHTML = '<option value="">---------</option>';
        }

        return fetch(`/api/load-subcategories/?master_category=${masterId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.length) return;

                data.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = item.name;
                    subSelect.appendChild(opt);
                });

                if (autoSelectFirst) {
                    subSelect.selectedIndex = 1;
                    const firstSubId = data[0].id;
                    return loadArticleTypes(firstSubId, true);
                }
            })
            .catch(err => console.error('Error loading subcategories:', err));
    }

    /**
     * Load article types for a given subcategory.
     * @param {number|string} subId
     * @param {boolean} autoSelectFirst
     */
    function loadArticleTypes(subId, autoSelectFirst = true) {
        if (!subId) {
            articleSelect.innerHTML = '<option value="">---------</option>';
            return Promise.resolve();
        }

        if (autoSelectFirst) {
            articleSelect.innerHTML = '<option value="">---------</option>';
        }

        return fetch(`/api/load-article-types/?sub_category=${subId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.length) return;

                data.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = item.name;
                    articleSelect.appendChild(opt);
                });

                if (autoSelectFirst) {
                    articleSelect.selectedIndex = 1;
                }
            })
            .catch(err => console.error('Error loading article types:', err));
    }

    // 🔁 When master category changes
    masterSelect.addEventListener('change', function() {
        const masterId = this.value;
        loadSubCategories(masterId, true);
    });

    // 🔁 When subcategory changes
    subSelect.addEventListener('change', function() {
        const subId = this.value;
        loadArticleTypes(subId, true);
    });

    // 🚀 Initialization when page loads
    const initialMasterId = masterSelect.value;
    const initialSubId = subSelect.value;

    if (initialMasterId) {
    loadSubCategories(initialMasterId, false).then(() => {
        if (initialSubId) {
            subSelect.value = initialSubId;
            loadArticleTypes(initialSubId, false);
        }
    });
}
});