(() => {
    const menu = document.getElementById('menuToggle');
    const nav = document.getElementById('mainNav');
    if (menu && nav) {
        menu.addEventListener('click', () => {
            const open = nav.classList.toggle('open');
            menu.setAttribute('aria-expanded', String(open));
            menu.textContent = open ? '×' : '☰';
        });
        nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
            nav.classList.remove('open');
            menu.setAttribute('aria-expanded', 'false');
            menu.textContent = '☰';
        }));
    }
    const newsletter = document.getElementById('newsletterForm');
    if (newsletter) newsletter.addEventListener('submit', event => {
        event.preventDefault();
        const feedback = document.getElementById('newsletterFeedback');
        if (feedback) feedback.textContent = 'Thanks! This demo does not store or email your address.';
        newsletter.reset();
    });
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const submit = form.querySelector('button[type="submit"]');
            if (submit && !submit.disabled && !form.classList.contains('status-form')) {
                submit.dataset.originalLabel ||= submit.textContent;
                submit.classList.add('is-submitting');
                if (!form.checkValidity()) {
                    submit.classList.remove('is-submitting');
                    return;
                }
                window.setTimeout(() => submit.classList.remove('is-submitting'), 2500);
            }
        });
    });
    document.querySelectorAll('img[loading="lazy"]').forEach(img => img.addEventListener('error', () => img.classList.add('image-fallback')));
    document.querySelectorAll('[data-confirm]').forEach(form => form.addEventListener('submit', event => {
        if (!window.confirm(form.dataset.confirm || 'Continue with this action?')) event.preventDefault();
    }));
})();
