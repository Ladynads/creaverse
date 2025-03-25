// ========================
// PROFILE-SPECIFIC FUNCTIONALITY
// ========================

// Tab System with HTMX
function setupProfileTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            
            // Add to clicked tab
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            const tabContent = document.getElementById(tabId);
            tabContent?.classList.add('active');
            
            // Load content via HTMX if empty
            if(tabContent && tabContent.children.length === 0) {
                htmx.ajax('GET', `/profile/${tabId}/`, `#${tabId}`);
            }
        });
    });
}

// Cover Photo Editor
function setupCoverPhotoUpload() {
    document.querySelector('.edit-cover-btn')?.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file && file.size < 5 * 1024 * 1024) { // 5MB limit
                const formData = new FormData();
                formData.append('cover_image', file);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                try {
                    const response = await fetch('/profile/update_cover/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        document.querySelector('.cover-photo').style.backgroundImage = `url(${data.new_cover_url})`;
                    }
                } catch (error) {
                    console.error('Upload error:', error);
                }
            } else {
                alert('Please select an image under 5MB');
            }
        };
        input.click();
    });
}

// Follow Button
function setupFollowButton() {
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
}

// ========================
// INITIALIZATION
// ========================

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.profile-container')) {
        setupProfileTabs();
        setupCoverPhotoUpload();
        setupFollowButton();
    }
});

// HTMX Event Handlers
document.body.addEventListener('htmx:afterSwap', function() {
    if (document.querySelector('.profile-container')) {
        setupProfileTabs();
        setupFollowButton();
    }
});