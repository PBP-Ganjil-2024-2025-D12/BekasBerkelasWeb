window.addEventListener('load', function() {
    setTimeout(function() {
        const messages = document.querySelectorAll('[role="alert"]');
        messages.forEach(function(message) {
            message.style.transition = 'opacity 0.5s ease-out';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        });
    }, 3000);
});

