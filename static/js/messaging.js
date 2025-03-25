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

// REAL-TIME MESSAGING


var messagePollInterval;
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


// TYPING INDICATORS


let typingTimeout;

function showTypingIndicator(userId) {
   
    if (document.querySelector('.typing-indicator')) return;
    

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
    
  
    if (typingTimeout) clearTimeout(typingTimeout);
    
  
    typingTimeout = setTimeout(hideTypingIndicator, 5000);
}

function hideTypingIndicator() {
    const indicator = document.querySelector('.typing-indicator');
    if (indicator) indicator.remove();
}


// MESSAGE COMPOSITION


function setupMessageForms() {
    document.querySelectorAll('.message-form textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
      
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.form.submit();
            }
        });
        
  
        textarea.addEventListener('input', debounce(function() {
            if (this.value.trim().length > 0) {
                sendTypingIndicator(true);
            }
        }, 1000));
    });
    
  
    document.querySelectorAll('.message-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            }
            
           
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


// CONNECTION MONITORING


function setupConnectionMonitoring() {
    if (!document.querySelector('.message-thread-container, .inbox-container')) return;
    
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


// MOBILE COMPOSE BUTTON


function setupMobileComposeButton() {
    const composeBtn = document.querySelector('.mobile-compose-btn');
    if (!composeBtn) return;
    
    composeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = this.href;
    });
}


// UTILITY FUNCTIONS


function scrollToLatestMessage() {
    const container = document.querySelector('.messages-thread');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function formatMessageTime(timestamp) {
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

function getUserInfo(userId) {
   
    
    return {
        id: userId,
        name: 'User',
        avatar: '/static/images/default-avatar.png'
    };
}