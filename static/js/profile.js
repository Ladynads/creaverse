// ========================
// PROFILE-SPECIFIC FUNCTIONALITY
// ========================

// Tab System with HTMX
function setupProfileTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all tabs & contents
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });

            // Activate clicked tab
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');

                // Load via HTMX if content is empty
                if (tabContent.innerHTML.trim() === '') {
                    const url = `/profile/${tabId}/`;
                    htmx.ajax('GET', url, { target: `#${tabId}` });
                }
            }
        });
    });
}

// Cover Photo Editor
function setupCoverPhotoUpload() {
    const editBtn = document.querySelector('.edit-cover-btn');
    if (!editBtn) return;

    editBtn.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file && file.size < 5 * 1024 * 1024) {
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
                alert('Please upload an image under 5MB.');
            }
        };

        input.click();
    });
}

// Follow Button Toggle
function setupFollowButton() {
    const followBtn = document.querySelector('.follow-btn');
    if (!followBtn) return;

    followBtn.addEventListener('click', async function () {
        this.disabled = true;

        try {
            const response = await fetch(this.dataset.followUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.dataset.csrf,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `user_id=${this.dataset.userId}`
            });

            if (response.ok) {
                const data = await response.json();
                this.classList.toggle('following', data.is_following);
                this.innerHTML = data.is_following
                    ? '<span class="check">✓</span> Following'
                    : '+ Follow';

                // Update follower count
                document.querySelectorAll('.stat .count').forEach(el => {
                    if (el.previousElementSibling.textContent.includes('Followers')) {
                        el.textContent = data.follower_count;
                    }
                });
            }
        } catch (err) {
            console.error('Follow error:', err);
        } finally {
            this.disabled = false;
        }
    });
}

// ========================
// INIT
// ========================
function initProfilePage() {
    if (document.querySelector('.profile-container')) {
        setupProfileTabs();
        setupCoverPhotoUpload();
        setupFollowButton();
    }
}

document.addEventListener('DOMContentLoaded', initProfilePage);
document.body.addEventListener('htmx:afterSwap', initProfilePage);

