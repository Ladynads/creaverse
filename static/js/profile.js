// profile.js - Updated with all profile functionality

// ========================
// PROFILE TAB SYSTEM
// ========================
document.addEventListener("DOMContentLoaded", function() {
    // Initialize tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            
            // Add to clicked tab
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            document.getElementById(tabId).classList.add('active');
            
            // Load content via HTMX if empty
            if(document.getElementById(tabId).children.length === 0) {
                htmx.ajax('GET', `/profile/${tabId}/`, `#${tabId}`);
            }
        });
    });

    // ========================
    // COVER PHOTO EDITOR
    // ========================
    document.querySelector('.edit-cover-btn')?.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('cover_image', file);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                try {
                    const response = await fetch('/profile/update_cover/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        location.reload(); // Refresh to show new cover
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        };
        input.click();
    });

    // ========================
    // FOLLOW BUTTON
    // ========================
    document.querySelector('.follow-btn')?.addEventListener('click', async function() {
        const btn = this;
        btn.disabled = true;
        
        try {
            const response = await fetch(btn.dataset.followUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': btn.dataset.csrf,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `user_id=${btn.dataset.userId}`
            });
            
            if(response.ok) {
                const data = await response.json();
                btn.classList.toggle('following', data.is_following);
                btn.innerHTML = data.is_following 
                    ? '<span class="check">✓</span> Following' 
                    : '+ Follow';
                
                // Update counts display
                document.querySelectorAll('.stat .count').forEach(el => {
                    if(el.previousElementSibling.textContent.includes('Followers')) {
                        el.textContent = data.follower_count;
                    }
                });
            }
        } catch(error) {
            console.error('Error:', error);
        } finally {
            btn.disabled = false;
        }
    });
});

// ========================
// LOADING STATES
// ========================
// Keep your existing loading animations
document.addEventListener('htmx:beforeRequest', function() {
    const target = document.getElementById(htmx.config.currentTarget);
    if (target) {
        target.classList.add('loading-state');
        target.innerHTML = `
            <div class="spinner"></div>
            <p>Loading...</p>
        `;
    }
});

document.addEventListener('htmx:afterRequest', function() {
    const target = document.getElementById(htmx.config.currentTarget);
    if (target) {
        target.classList.remove('loading-state');
    }
});