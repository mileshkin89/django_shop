document.getElementById('forgot-password-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const forgotPasswordUrl = this.dataset.forgotPasswordUrl;

    const response = await fetch(forgotPasswordUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ email })
    });

    const data = await response.json();
    showToast(data.message || "Something went wrong");

    if (data.success) {
        const loginUrl = this.dataset.loginUrl;
        setTimeout(() => {
            window.location.href = loginUrl;
        }, 10000);
    }
});

// Toast logic
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 6000);
}