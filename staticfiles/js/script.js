// ========================
// CORE FUNCTIONALITY
// ========================

// Auto-dismiss flash messages
document.addEventListener("DOMContentLoaded", function() {
    // Django messages
    document.querySelectorAll(".flash-message, ul.messages li").forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

// ========================
// MESSAGING SYSTEM
// ========================

// Real-time message updates
let messagePollInterval;

function setupMessagePolling() {
    if (document.querySelector('.message-thread-container')) {
        messagePollInterval = setInterval(checkNewMessages, 5000);
        scrollToLatestMessage();
    }
}

function checkNewMessages() {
    const lastMessage = document.querySelector('.message-bubble:last-child');
    if (!lastMessage) return;

    fetch(`/messages/check_new/?last_id=${lastMessage.dataset.messageId}`)
        .then(response => response.json())
        .then(data => {
            if (data.new_messages?.length > 0) {
                appendNewMessages(data.new_messages);
            }
        })
        .catch(console.error);
}

function appendNewMessages(messages) {
    const container = document.querySelector('.message-thread-container');
    messages.forEach(msg => {
        container.insertBefore(createMessageBubble(msg), container.querySelector('.message-form'));
    });
    scrollToLatestMessage();
}

function createMessageBubble(message) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${message.is_sender ? 'sent' : 'received'}`;
    bubble.dataset.messageId = message.id;
    bubble.innerHTML = `
        <p>${message.content}</p>
        <span class="message-time">${message.timestamp}</span>
    `;
    return bubble;
}

function scrollToLatestMessage() {
    const messages = document.querySelectorAll('.message-bubble');
    if (messages.length > 0) {
        messages[messages.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
}

// Message search
function setupMessageSearch() {
    const searchInput = document.getElementById('message-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const term = this.value.toLowerCase();
            document.querySelectorAll('.message-preview').forEach(el => {
                el.style.display = el.textContent.toLowerCase().includes(term) ? 'flex' : 'none';
            });
        }, 300));
    }
}

// ========================
// PROFILE INTERACTIONS 
// ========================

// Follow button handler
function setupFollowButtons() {
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const button = this;
            button.disabled = true;
            button.style.transform = 'scale(0.95)';  // Optional: Add scaling effect when clicked
            
            try {
                // Sending POST request to follow/unfollow the user
                const response = await fetch(button.dataset.followUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': button.dataset.csrf
                    },
                    body: JSON.stringify({ user_id: button.dataset.userId })
                });
                
                const data = await response.json();  // Get the response JSON
                
                // Toggle the button state (following or not)
                button.classList.toggle('following', data.is_following);
                
                // Update the button text and color based on follow state
                button.innerHTML = data.is_following 
                    ? '<span class="check">✓</span> Following' 
                    : '+ Follow';
                
                button.style.backgroundColor = data.is_following 
                    ? '#19A7CE'  // Blue when following
                    : '#9743F4';  // Purple when not following
                
                // Optionally update stats if a function is defined
                if (typeof updateStats === 'function') updateStats();
            } catch (error) {
                console.error('Follow error:', error);
            } finally {
                button.style.transform = '';  // Reset the scaling effect
                button.disabled = false;  // Re-enable the button
            }
        });
    });
}
// Like buttons
function setupLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('liked');
            if (this.classList.contains('liked')) {
                this.innerHTML = '❤️ Liked';
                this.style.backgroundColor = '#FF6B6B';
            } else {
                this.innerHTML = '🤍 Like';
                this.style.backgroundColor = '#9743F4';
            }
        });
    });
}

// ========================
// UI COMPONENTS
// ========================

// Avatar hover effects
function setupAvatarHovers() {
    document.querySelectorAll('.creator-avatar').forEach(avatar => {
        avatar.addEventListener('mouseenter', () => {
            avatar.style.transform = 'scale(1.05)';
            avatar.style.boxShadow = '0 0 15px rgba(151, 67, 244, 0.3)';
        });
        avatar.addEventListener('mouseleave', () => {
            avatar.style.transform = '';
            avatar.style.boxShadow = '';
        });
    });
}

// Tab system
function setupProfileTabs() {
    const tabs = document.querySelectorAll('.profile-tabs button');
    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Tab switching logic
            const targetId = tab.dataset.target;
            document.querySelectorAll('.tab-content').forEach(c => {
                c.classList.toggle('active', c.id === targetId);
            });
            
            // Update active tab style
            tabs.forEach(t => t.classList.toggle('tab-active', t === tab));
        });
    });
    
    // Activate first tab
    tabs[0].click();
}

// ========================
// UTILITIES
// ========================

function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// ========================
// INITIALIZATION
// ========================

document.addEventListener('DOMContentLoaded', function() {
    // Core
    setupMessageSearch();
    setupMessagePolling();
    
    // Profile
    setupFollowButtons();
    setupLikeButtons();
    setupAvatarHovers();
    setupProfileTabs();
    
    // Cleanup on page change
    document.addEventListener('turbo:before-cache', function() {
        clearInterval(messagePollInterval);
    });
});

