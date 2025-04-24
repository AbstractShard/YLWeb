function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.margin = '10px auto';
    notification.style.width = 'fit-content';
    notification.style.maxWidth = '80%';

    notification.className = 'alert alert-success fixed-top text-center notification';
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
            const emailField = document.querySelector('input[name="email"]');
            if (!emailField || !emailField.value.trim()) {
                return;
            }
            showNotification('Код отправлен');
        });
    }
});
