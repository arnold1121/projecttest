(() => {
    document.querySelectorAll('.quantity-form input[type="number"], .detail-buy input[type="number"]').forEach(input => {
        input.addEventListener('change', () => {
            const min = Number(input.min || 1);
            const max = Number(input.max || 99);
            const value = Number(input.value || min);
            input.value = String(Math.max(min, Math.min(max, Math.trunc(value))));
        });
    });
    document.querySelectorAll('.quantity-form').forEach(form => form.addEventListener('submit', event => {
        const input = form.querySelector('input[name="quantity"]');
        if (input && Number(input.value) < 1) {
            event.preventDefault();
            input.value = '1';
        }
    }));
    document.querySelectorAll('.add-button').forEach(button => {
        button.addEventListener('click', () => {
            if (!button.disabled) {
                button.dataset.label = button.textContent;
                button.textContent = 'Adding…';
                window.setTimeout(() => {
                    if (button.isConnected) button.textContent = button.dataset.label || 'Add to basket';
                }, 1800);
            }
        });
    });
})();
