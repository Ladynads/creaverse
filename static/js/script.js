
// CORE FUNCTIONALITY


// Auto-dismiss flash messages
document.addEventListener("DOMContentLoaded", function() {
    // Dismiss flash messages after 5 seconds
    document.querySelectorAll(".flash-message").forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Close buttons for flash messages
    document.querySelectorAll(".flash-message .close").forEach(btn => {
        btn.addEventListener("click", function() {
            this.closest(".flash-message").remove();
        });
    });
});


// MESSAGING SYSTEM


let messagePollInterval;

function setupMessagePolling() {
    if (document.querySelector('.message-thread-container')) {
        // Check for new messages every 5 seconds
        messagePollInterval = setInterval(checkNewMessages, 5000);
        scrollToLatestMessage();
    }
}

function checkNewMessages() {
    const lastMessage = document.querySelector('.message-bubble:last-child');
    if (!lastMessage) return;

    fetch(`/messages/check_new/?last_id=${lastMessage.dataset.messageId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.new_messages?.length > 0) {
                appendNewMessages(data.new_messages);
            }
        })
        .catch(error => {
            console.error('Error checking messages:', error);
            clearInterval(messagePollInterval);
        });
}

function appendNewMessages(messages) {
    const container = document.querySelector('.message-thread-container');
    if (!container) return;

    messages.forEach(msg => {
        const messageElement = createMessageBubble(msg);
        const messageForm = container.querySelector('.message-form');
        if (messageForm) {
            container.insertBefore(messageElement, messageForm);
        } else {
            container.appendChild(messageElement);
        }
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
        messages[messages.length - 1].scrollIntoView({
            behavior: 'smooth',
            block: 'end'
        });
    }
}

// Message search functionality
function setupMessageSearch() {
    const searchInput = document.getElementById('message-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', debounce(function() {
        const term = this.value.toLowerCase().trim();
        document.querySelectorAll('.message-preview').forEach(el => {
            el.style.display = el.textContent.toLowerCase().includes(term) ? 'flex' : 'none';
        });
    }, 300));
}


// UTILITIES


// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Safe element selector
function $(selector, parent = document) {
    return parent.querySelector(selector);
}

// Safe elements selector (returns array)
function $$(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
}

//Creator Carousel//
document.addEventListener('DOMContentLoaded', function() {
    // Featured Creators Carousel
    const featuredCarousel = document.querySelector('.featured-carousel');
    if (featuredCarousel) {
        let isDown = false;
        let startX;
        let scrollLeft;

        featuredCarousel.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - featuredCarousel.offsetLeft;
            scrollLeft = featuredCarousel.scrollLeft;
            featuredCarousel.style.cursor = 'grabbing';
        });

        featuredCarousel.addEventListener('mouseleave', () => {
            isDown = false;
            featuredCarousel.style.cursor = 'grab';
        });

        featuredCarousel.addEventListener('mouseup', () => {
            isDown = false;
            featuredCarousel.style.cursor = 'grab';
        });

        featuredCarousel.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - featuredCarousel.offsetLeft;
            const walk = (x - startX) * 2;
            featuredCarousel.scrollLeft = scrollLeft - walk;
        });
    }

});


// INITIALISATION


// Run when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize messaging system if on messaging page
    if ($('.message-thread-container')) {
        setupMessagePolling();
    }

   
    if ($('#message-search')) {
        setupMessageSearch();
    }
});

// Cleanup when leaving page
window.addEventListener('beforeunload', function() {
    if (messagePollInterval) {
        clearInterval(messagePollInterval);
    }
});