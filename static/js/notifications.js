function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.margin = '10px auto';
    notification.style.width = 'fit-content';
    notification.style.maxWidth = '80%';

    notification.className = `alert fixed-top text-center notification alert-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Trigger reflow to enable transition
    void notification.offsetWidth;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 2700);
}

document.addEventListener('DOMContentLoaded', function() {
    const verifyButton = document.getElementById('send_verify_code');
    if (verifyButton) {
        verifyButton.addEventListener('click', function() {
            // Find the closest form and get the email field
            const form = verifyButton.closest('form');
            let subject = 'verify_email';
            if (window.location.pathname.includes('change_password')) {
                subject = 'change_password';
            } else if (window.location.pathname.includes('forgot_password')) {
                subject = 'forgot_password';
            } else if (window.location.pathname.includes('register')) {
                subject = 'register';
            }
            let email = null;
            if (subject !== 'forgot_password') {
                let emailField = form.querySelector('input[name="email"]');
                email = emailField ? emailField.value.trim() : null;
                if (!email && form.dataset.email) {
                    email = form.dataset.email;
                }
                if (!email) {
                    showNotification('email не указан', 'danger');
                    return;
                }
            }
            fetch('/send_verify_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email, subject: subject })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Код отправлен', 'success');
                } else {
                    showNotification('Ошибка: ' + data.message, 'danger');
                }
            })
            .catch(() => {
                showNotification('Ошибка при отправке кода', 'danger');
            });
        });
    }
});
