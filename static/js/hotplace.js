

document.addEventListener('DOMContentLoaded', function() {
    if (typeof userExists !== 'undefined' && !userExists) {
        setTimeout(function() {
            location.reload();
        }, 2000); // 5000ms = 5초
    }
});
