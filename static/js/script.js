// ✅ Auto-dismiss flash messages after 5 seconds (with fade-out effect)
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        let messages = document.querySelectorAll(".flash-message");
        messages.forEach(msg => {
            msg.style.transition = "opacity 1s ease-out";
            msg.style.opacity = "0";
            setTimeout(() => msg.style.display = "none", 1000); // Removes after fade-out
        });
    }, 5000);
});
