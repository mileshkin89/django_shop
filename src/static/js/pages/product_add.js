// product_add.js

/**
 * Event listener for the DOMContentLoaded event.
 * Initializes the cascading dropdowns for product categories.
 */
document.addEventListener('DOMContentLoaded', function() {
    const masterSelect = document.querySelector('#id_master_category');
    const subSelect = document.querySelector('#id_sub_category');
    const articleSelect = document.querySelector('#id_article_type');

    /**
     * Loads sub-categories based on the selected master category.
     * @param {string} masterId - The ID of the master category.
     * @param {boolean} [autoSelectFirst=true] - Whether to automatically select the first sub-category.
     */
    function loadSubCategories(masterId, autoSelectFirst = true) {
        if (!masterId) {
            subSelect.innerHTML = '<option value="">---------</option>';
            articleSelect.innerHTML = '<option value="">---------</option>';
            return;
        }

        subSelect.innerHTML = '<option value="">---------</option>';
        articleSelect.innerHTML = '<option value="">---------</option>';

        fetch(`/api/load-subcategories/?master_category=${masterId}`)
            .then(res => res.json())
            .then(data => {
                subSelect.innerHTML = '<option value="">---------</option>';

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
                    loadArticleTypes(firstSubId, true);
                }
            })
            .catch(err => {
                console.error('Error loading subcategories:', err);
            });
    }

    /**
     * Loads article types based on the selected sub-category.
     * @param {string} subId - The ID of the sub-category.
     * @param {boolean} [autoSelectFirst=true] - Whether to automatically select the first article type.
     */
    function loadArticleTypes(subId, autoSelectFirst = true) {
        if (!subId) {
            articleSelect.innerHTML = '<option value="">---------</option>';
            return;
        }

        articleSelect.innerHTML = '<option value="">---------</option>';

        fetch(`/api/load-article-types/?sub_category=${subId}`)
            .then(res => res.json())
            .then(data => {
                articleSelect.innerHTML = '<option value="">---------</option>';

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
            .catch(err => {
                console.error('Error loading article types:', err);
            });
    }

    /**
     * Event handler for changes in the master category select.
     * Loads sub-categories when the master category changes.
     */
    masterSelect.addEventListener('change', function() {
        const masterId = this.value;
        loadSubCategories(masterId, true);
    });

    /**
     * Event handler for changes in the sub-category select.
     * Loads article types when the sub-category changes.
     */
    subSelect.addEventListener('change', function() {
        const subId = this.value;
        loadArticleTypes(subId, true);
    });

    /**
     * Initializes the cascading dropdowns on page load.
     * If a master category is already selected, it loads the corresponding sub-categories.
     */
    const initialMasterId = masterSelect.value;
    if (initialMasterId) {
        loadSubCategories(initialMasterId, true);
    }
});
