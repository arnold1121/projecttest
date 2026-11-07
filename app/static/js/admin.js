(() => {
    // Destructive actions in the admin templates use data-confirm; ask once before submitting.
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', event => {
            if (!window.confirm(form.dataset.confirm || 'Continue with this action?')) event.preventDefault();
        });
    });
    document.querySelectorAll('.admin-table tbody tr').forEach((row, index) => {
        row.style.animationDelay = `${Math.min(index, 8) * 25}ms`;
    });
})();
