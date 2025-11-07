document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.querySelector('.account-page-wrapper');
    const tabs = Array.from(document.querySelectorAll('.account-tab'));
    const panes = Array.from(document.querySelectorAll('.tab-pane'));

    if (!wrapper || tabs.length === 0 || panes.length === 0) {
        return;
    }

    const toPathname = (value) => {
        if (!value) {
            return null;
        }

        try {
            const url = new URL(value, window.location.origin);
            return url.pathname.replace(/\/+$/, '') || '/';
        } catch (error) {
            return null;
        }
    };

    const updateActiveTab = (tab) => {
        const targetSelector = tab?.dataset?.tabTarget;
        const targetPane = targetSelector ? document.querySelector(targetSelector) : null;

        if (!tab || !targetPane) {
            return;
        }

        tabs.forEach((item) => item.classList.remove('active'));
        panes.forEach((pane) => pane.classList.remove('active'));

        tab.classList.add('active');
        targetPane.classList.add('active');
    };

    const currentPath = toPathname(window.location.href);
    const initialTab = tabs.find((tab) => toPathname(tab.dataset.url) === currentPath) || tabs[0];

    updateActiveTab(initialTab);

    tabs.forEach((tab) => {
        tab.addEventListener('click', (event) => {
            const redirectUrl = tab.dataset.url;

            if (redirectUrl) {
                event.preventDefault();
                window.location.assign(redirectUrl);
            }
        });
    });
});

