// ✅ Auto-dismiss flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
    let messages = document.querySelectorAll(".flash-message");
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500); // Fully remove after fade-out
        }, 5000);
    });

    // Hide Django's default message box if still visible
    let djangoMessages = document.querySelectorAll("ul.messages li");
    djangoMessages.forEach(msg => msg.style.display = "none");
});

// Like Button Animation
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('liked');
        if (button.classList.contains('liked')) {
            // Add a subtle animation when liked
            button.innerHTML = '❤️ Liked';
            button.style.backgroundColor = '#FF6B6B'; // Change button color
            button.style.transform = 'scale(1.1)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        } else {
            button.innerHTML = '🤍 Like';
            button.style.backgroundColor = '#9743F4'; // Revert button color
        }
    });
});

// Follow Button Animation
document.querySelectorAll('.btn-follow').forEach(button => {
    button.addEventListener('click', () => {
        if (button.textContent === 'Follow') {
            button.textContent = 'Unfollow';
            button.style.backgroundColor = '#FF6B6B'; // Change to red for unfollow
            button.style.transform = 'scale(1.1)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        } else {
            button.textContent = 'Follow';
            button.style.backgroundColor = '#19A7CE'; // Revert to blue for follow
        }
    });
});

// Hover Effects for Profile Picture
document.querySelectorAll('.profile-picture').forEach(picture => {
    picture.addEventListener('mouseenter', () => {
        picture.style.transform = 'scale(1.05)';
        picture.style.boxShadow = '0 0 15px rgba(151, 67, 244, 0.5)';
    });
    picture.addEventListener('mouseleave', () => {
        picture.style.transform = 'scale(1)';
        picture.style.boxShadow = 'none';
    });
});

// Smooth Scroll for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Lazy Loading for Images
document.addEventListener('DOMContentLoaded', function () {
    let lazyImages = document.querySelectorAll('img.lazy');
    lazyImages.forEach(img => {
        img.src = img.dataset.src;
        img.classList.remove('lazy');
    });
});