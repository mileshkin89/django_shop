document.addEventListener('DOMContentLoaded', function() {

    // --- General logic for all pages (Login/Logout Simulation) ---
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');
    function checkLoginStatus() {
        if (localStorage.getItem('isLoggedIn') === 'true') {
            document.body.classList.add('user-logged-in');
        } else {
            document.body.classList.remove('user-logged-in');
        }
    }
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            localStorage.setItem('isLoggedIn', 'true');
            const nextUrl = new URLSearchParams(window.location.search).get('next');
            window.location.href = nextUrl || 'home.html';
        });
    }
    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('isLoggedIn');
            window.location.href = 'home.html';
        });
    }
    checkLoginStatus();


    // --- Logic for the Main Page (home.html) ---
    const homePageContent = document.querySelector('.main-content-grid');
    if (homePageContent) {
        // 1. Sort Options Logic
        const sortButtons = document.querySelectorAll('.sort-options .sort-button');
        sortButtons.forEach(button => {
            button.addEventListener('click', function() {
                sortButtons.forEach(btn => btn.classList.remove('active-sort'));
                this.classList.add('active-sort');
            });
        });

        // 2. Pagination Logic
        const paginationList = document.querySelector('.pagination-list');
        if (paginationList) {
            const paginationLinks = paginationList.querySelectorAll('.pagination__link');
            paginationLinks.forEach(link => {
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    paginationLinks.forEach(lnk => lnk.classList.remove('active'));
                    this.classList.add('active');
                });
            });
        }

        // 3. Filter Logic (Keywords and Checkboxes)
        const keywordsList = document.querySelector('.keywords-list');
        const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');

        if (keywordsList && checkboxes.length > 0) {

            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const keyword = this.dataset.keyword;
                    if (this.checked) {
                        if (!document.querySelector(`.keyword-tag[data-keyword="${keyword}"]`)) {
                            const newTag = document.createElement('span');
                            newTag.className = 'keyword-tag';
                            newTag.setAttribute('data-keyword', keyword);
                            newTag.innerHTML = `${keyword} <i class="fa-solid fa-xmark remove-keyword-icon"></i>`;
                            keywordsList.appendChild(newTag);
                        }
                    } else {
                        const tagToRemove = document.querySelector(`.keyword-tag[data-keyword="${keyword}"]`);
                        if (tagToRemove) {
                            tagToRemove.remove();
                        }
                    }
                });
            });

            keywordsList.addEventListener('click', function(event) {
                const keywordIcon = event.target.closest('.remove-keyword-icon');
                if (keywordIcon) {
                    const keywordTag = keywordIcon.closest('.keyword-tag');
                    const keywordText = keywordTag.dataset.keyword;
                    const checkbox = document.querySelector(`.checkbox-container input[data-keyword="${keywordText}"]`);
                    if (checkbox) {
                        checkbox.checked = false;
                    }
                    keywordTag.remove();
                }
            });
        }
    }

    // --- Logic for Account and Admin Pages ---
    const accountAdminWrapper = document.querySelector('.account-page-wrapper, .admin-page-wrapper');
    if (accountAdminWrapper) {
        // Account Page Tabs
        const accountTabs = document.querySelectorAll('.account-tab');
        const tabPanes = document.querySelectorAll('.tab-pane');
        if (accountTabs.length > 0 && tabPanes.length > 0) {
            accountTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    accountTabs.forEach(item => item.classList.remove('active'));
                    tabPanes.forEach(pane => pane.classList.remove('active'));
                    const targetPane = document.querySelector(this.dataset.tabTarget);
                    this.classList.add('active');
                    if (targetPane) targetPane.classList.add('active');
                });
            });
        }

        // Admin Panel - Category Tags
        const categoryTagsContainer = document.querySelector('.category-tags');
        if (categoryTagsContainer) {
            categoryTagsContainer.addEventListener('click', function(e) {
                const clickedTag = e.target.closest('.category-tag');
                if (clickedTag) {
                    categoryTagsContainer.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
                    clickedTag.classList.add('active');
                }
            });
        }

        // Image Upload Simulation
        const uploadButton = document.getElementById('upload-image-btn');
        const fileInput = document.getElementById('image-upload-input');

        if (uploadButton && fileInput) {
            uploadButton.addEventListener('click', function() {
                fileInput.click();
            });

            fileInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    const placeholder = document.querySelector('.image-upload-placeholder');

                    reader.onload = function(e) {
                        placeholder.innerHTML = '';
                        placeholder.style.backgroundImage = `url('${e.target.result}')`;
                        placeholder.style.backgroundSize = 'cover';
                        placeholder.style.backgroundPosition = 'center';
                    }
                    reader.readAsDataURL(file);
                }
            });
        }
    }
});