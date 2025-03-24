

//  Auto-dismiss flash messages after 5 seconds
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


// Premium Follow Button with HTMX Integration
document.querySelectorAll('.follow-btn').forEach(button => {
    button.addEventListener('click', async function(e) {
        e.preventDefault();
        
        // Visual feedback
        this.style.transform = 'scale(0.95)';
        this.style.opacity = '0.8';
        
        // Get data attributes
        const userId = this.dataset.userId;
        const followUrl = this.dataset.followUrl;
        const csrfToken = this.dataset.csrf;
        
        try {
            const response = await fetch(followUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ user_id: userId })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Update button state
                this.classList.toggle('following');
                if (data.is_following) {
                    this.innerHTML = '<span class="check">✓</span> Following';
                    // Pulse animation
                    this.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                        this.style.opacity = '1';
                    }, 200);
                } else {
                    this.innerHTML = '+ Follow';
                    this.style.transform = 'scale(1)';
                    this.style.opacity = '1';
                }
                
                // Update stats if function exists
                if (typeof updateStats === 'function') {
                    updateStats();
                }
            }
        } catch (error) {
            console.error('Error:', error);
            this.style.transform = 'scale(1)';
            this.style.opacity = '1';
        }
    });
});

// Advanced Profile Avatar Hover Effects
document.querySelectorAll('.profile-avatar').forEach(avatar => {
    avatar.addEventListener('mouseenter', () => {
        avatar.style.transform = 'translateY(-5px) rotate(5deg)';
        avatar.style.filter = 'drop-shadow(0 10px 8px rgba(151, 67, 244, 0.3))';
    });
    
    avatar.addEventListener('mouseleave', () => {
        avatar.style.transform = '';
        avatar.style.filter = '';
    });
    
    // Click effect
    avatar.addEventListener('click', () => {
        avatar.style.transform = 'scale(0.95)';
        setTimeout(() => {
            avatar.style.transform = 'translateY(-5px) rotate(5deg)';
        }, 100);
    });
});

// Interactive Tab System
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.profile-tabs button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active classes
            tabButtons.forEach(btn => btn.classList.remove('tab-active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active classes
            button.classList.add('tab-active');
            const targetId = button.dataset.target;
            document.getElementById(targetId).classList.add('active');
            
            // Lazy load content if empty
            if (document.getElementById(targetId).innerHTML.trim() === '') {
                loadTabContent(targetId);
            }
        });
    });
    
    // Activate first tab by default
    if (tabButtons.length > 0) {
        tabButtons[0].click();
    }
});

function loadTabContent(tabId) {
    const username = document.querySelector('.username').textContent;
    const url = `/profile/${username}/${tabId}/`;
    
    // Show loading state
    const tabContent = document.getElementById(tabId);
    tabContent.innerHTML = '<div class="loading-spinner"></div>';
    
    // Load content via HTMX
    htmx.ajax('GET', url, `#${tabId}`)
        .then(() => {
            // Initialize any components in the loaded content
            if (tabId === 'likes') {
                initLikeButtons();
            }
        });
}


// Follow Button Animation 
document.querySelectorAll('.btn-follow').forEach(button => {
    button.addEventListener('click', () => {
        if (button.textContent === 'Follow') {
            button.textContent = 'Unfollow';
            button.style.backgroundColor = '#FF6B6B';
            button.style.transform = 'scale(1.1)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        } else {
            button.textContent = 'Follow';
            button.style.backgroundColor = '#19A7CE';
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


// Stats Updater for HTMX
function updateStats() {
    const username = document.querySelector('.username').textContent;
    htmx.ajax('GET', `/profile/${username}/stats/`, '.stats-ticker');
}

// Initialize Like Buttons in Dynamic Content
function initLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('liked');
            if (button.classList.contains('liked')) {
                button.innerHTML = '❤️ Liked';
                button.style.backgroundColor = '#FF6B6B';
                button.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 200);
            } else {
                button.innerHTML = '🤍 Like';
                button.style.backgroundColor = '#9743F4';
            }
        });
    });
}

// Engagement Score Animation
function animateEngagementScore() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const targetWidth = progressBar.style.getPropertyValue('--progress');
        progressBar.style.width = '0';
        setTimeout(() => {
            progressBar.style.width = targetWidth;
        }, 100);
    }
}

// Initialize everything when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    animateEngagementScore();
    
    // Check for follow button to attach events
    if (document.querySelector('.follow-btn')) {
        document.querySelectorAll('.follow-btn').forEach(btn => {
            btn.addEventListener('click', followHandler);
        });
    }
    
    // Initialize tooltips
    initTooltips();
});

// Tooltip System
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
    
    function showTooltip(e) {
        const tooltipText = this.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width/2 - tooltip.offsetWidth/2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
    }
    
    function hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
}