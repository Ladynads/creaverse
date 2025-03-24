// ========================
// MESSAGING SYSTEM CORE
// ========================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all messaging components
    initMessageSearch();
    setupMessagePolling();
    setupMessageForms();
    setupMobileComposeButton();
    setupConnectionMonitoring();
});

// ========================
// MESSAGE SEARCH FUNCTIONALITY
// ========================

function initMessageSearch() {
    const searchInput = document.getElementById('message-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', debounce(function() {
        const term = this.value.toLowerCase();
        document.querySelectorAll('.message-preview').forEach(preview => {
            const text = preview.textContent.toLowerCase();
            preview.style.display = text.includes(term) ? 'flex' : 'none';
        });
    }, 300));
}

// ========================
// REAL-TIME MESSAGING
// ========================

let messagePollInterval;
let currentThreadId = null;

function setupMessagePolling() {
    // Only activate on message threads
    const threadContainer = document.querySelector('.message-thread-container');
    if (!threadContainer) return;

    currentThreadId = threadContainer.dataset.threadId;
    if (!currentThreadId) return;

    // Start polling immediately
    checkForNewMessages();
    
    // Then check every 5 seconds
    messagePollInterval = setInterval(checkForNewMessages, 5000);

    // Cleanup when leaving page
    document.addEventListener('turbo:before-cache', () => {
        clearInterval(messagePollInterval);
    });
}

function checkForNewMessages() {
    const lastMessage = document.querySelector('.message-bubble:last-child');
    const lastMessageId = lastMessage ? lastMessage.dataset.messageId : null;

    fetch(`/messages/api/thread/${currentThreadId}/updates/?last_id=${lastMessageId || ''}`)
        .then(response => response.json())
        .then(data => {
            if (data.new_messages && data.new_messages.length > 0) {
                appendNewMessages(data.new_messages);
            }
            
            if (data.is_typing) {
                showTypingIndicator(data.user_id);
            } else {
                hideTypingIndicator();
            }
            
            updateConnectionStatus(data.connection_status);
        })
        .catch(error => {
            console.error('Message polling error:', error);
            updateConnectionStatus('disconnected');
        });
}

function appendNewMessages(messages) {
    const container = document.querySelector('.messages-thread');
    messages.forEach(msg => {
        // Only add if not already present
        if (!document.querySelector(`.message-bubble[data-message-id="${msg.id}"]`)) {
            const bubble = createMessageBubble(msg);
            container.appendChild(bubble);
        }
    });
    scrollToLatestMessage();
}

function createMessageBubble(message) {
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${message.is_sender ? 'sent' : 'received'}`;
    bubble.dataset.messageId = message.id;
    
    bubble.innerHTML = `
        ${message.is_sender ? '' : `<img src="${message.sender_avatar}" class="message-avatar" alt="${message.sender_name}">`}
        <div class="message-content">
            <p>${message.content}</p>
            <div class="message-meta">
                <span class="timestamp">${formatMessageTime(message.created_at)}</span>
                ${message.is_sender ? `<span class="read-status">${message.is_read ? '✓✓' : '✓'}</span>` : ''}
            </div>
        </div>
    `;
    
    return bubble;
}

// ========================
// TYPING INDICATORS
// ========================

let typingTimeout;

function showTypingIndicator(userId) {
    // Only show if we don't already have one
    if (document.querySelector('.typing-indicator')) return;
    
    // Get user info (you'll need to implement this based on your user system)
    const user = getUserInfo(userId);
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator received';
    indicator.innerHTML = `
        <img src="${user.avatar}" class="message-avatar" alt="${user.name}">
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    document.querySelector('.messages-thread').appendChild(indicator);
    scrollToLatestMessage();
    
    // Clear any existing timeout
    if (typingTimeout) clearTimeout(typingTimeout);
    
    // Auto-hide after 5 seconds if no updates
    typingTimeout = setTimeout(hideTypingIndicator, 5000);
}

function hideTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) indicator.remove();
}

// ========================
// MESSAGE COMPOSITION
// ========================

function setupMessageForms() {
    // Auto-resizing textareas
    document.querySelectorAll('.message-form textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Send on Ctrl+Enter
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.form.submit();
            }
        });
        
        // Typing indicators
        textarea.addEventListener('input', debounce(function() {
            if (this.value.trim().length > 0) {
                sendTypingIndicator(true);
            }
        }, 1000));
    });
    
    // Form submission handling
    document.querySelectorAll('.message-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            }
            
            // You might want to add AJAX form submission here
            // For now, we'll let it submit normally
        });
    });
}

function sendTypingIndicator(isTyping) {
    if (!currentThreadId) return;
    
    fetch('/messages/api/typing/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            thread_id: currentThreadId,
            is_typing: isTyping
        })
    }).catch(console.error);
}

// ========================
// CONNECTION MONITORING
// ========================

function setupConnectionMonitoring() {
    // Only on pages where messaging is active
    if (!document.querySelector('.message-thread-container, .inbox-container')) return;
    
    // Create status element if it doesn't exist
    if (!document.getElementById('connection-status')) {
        const statusEl = document.createElement('div');
        statusEl.id = 'connection-status';
        statusEl.className = 'connection-status';
        statusEl.innerHTML = `
            <span class="connection-dot"></span>
            <span class="connection-text">Connecting...</span>
        `;
        document.body.appendChild(statusEl);
    }
    
    // Check connection periodically
    setInterval(checkConnection, 10000);
}

function updateConnectionStatus(status) {
    const statusEl = document.getElementById('connection-status');
    if (!statusEl) return;
    
    statusEl.className = `connection-status ${status}`;
    
    switch(status) {
        case 'connected':
            statusEl.querySelector('.connection-text').textContent = 'Connected';
            break;
        case 'disconnected':
            statusEl.querySelector('.connection-text').textContent = 'Reconnecting...';
            break;
        case 'slow':
            statusEl.querySelector('.connection-text').textContent = 'Slow connection';
            break;
    }
}

function checkConnection() {
    // Simple ping to check connection quality
    const start = Date.now();
    fetch('/messages/api/ping/')
        .then(() => {
            const latency = Date.now() - start;
            if (latency > 1000) {
                updateConnectionStatus('slow');
            } else {
                updateConnectionStatus('connected');
            }
        })
        .catch(() => {
            updateConnectionStatus('disconnected');
        });
}

// ========================
// MOBILE COMPOSE BUTTON
// ========================

function setupMobileComposeButton() {
    const composeBtn = document.querySelector('.mobile-compose-btn');
    if (!composeBtn) return;
    
    composeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = this.href;
    });
}

// ========================
// UTILITY FUNCTIONS
// ========================

function scrollToLatestMessage() {
    const container = document.querySelector('.messages-thread');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function formatMessageTime(timestamp) {
    // Convert to relative time (e.g. "2 minutes ago")
    // You might want to use a library like moment.js for better formatting
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Mock function - replace with your actual user lookup
function getUserInfo(userId) {
    // In a real implementation, you might:
    // 1. Have user data already in the DOM
    // 2. Make an API call to get user info
    // 3. Use a client-side store
    
    return {
        id: userId,
        name: 'User',
        avatar: '/static/images/default-avatar.png'
    };
}