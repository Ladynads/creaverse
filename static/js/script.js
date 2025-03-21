// ✅ Auto-dismiss flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", function() {
    let messages = document.querySelectorAll(".flash-message");
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500); // Fully remove after fade-out
        }, 5000);
    });

    // hide Django's default message box if still visible
    let djangoMessages = document.querySelectorAll("ul.messages li");
    djangoMessages.forEach(msg => msg.style.display = "none");
});

// Like Button Animation
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('liked');
    });
});