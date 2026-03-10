// Toast Notification Logic
document.addEventListener('DOMContentLoaded', function () {
    // Check if there are any Django messages that should trigger a toast
    // For this to work efficiently with Django messages, we might need to render them as JSON or specific HTML elements.
    // However, the current base.html renders alerts. We can enhance this to show toasts for specific actions.

    // For now, let's look for a specific flag or just trigger for "Item added" if we implement an AJAX add-to-cart later.
    // But since the current flow is a full page reload, we can check for success alerts and convert them to toasts or just show them.

    // Alternatively, for "Item added to cart", if we want to show it as a toast instead of an alert:
    const alerts = document.querySelectorAll('.alert-success');
    if (alerts.length > 0) {
        const toastLiveExample = document.getElementById('liveToast');
        const toastBootstrap = new bootstrap.Toast(toastLiveExample);

        // Update toast body with the alert message
        const toastBody = toastLiveExample.querySelector('.toast-body');
        toastBody.textContent = alerts[0].innerText;

        toastBootstrap.show();

        // Optionally hide the original alert if we want to replace it
        // alerts[0].style.display = 'none';
    }
});
