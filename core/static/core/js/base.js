// Base JavaScript - Dog Booking System

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initializeAlerts();
    initializeModals();
    initializeTooltips();
    initializeDropdowns();
});

function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Add close button if it doesn't exist
        if (!alert.querySelector('.alert-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'alert-close';
            closeBtn.innerHTML = '×';
            closeBtn.style.cssText = `
                background: none;
                border: none;
                font-size: 1.2rem;
                font-weight: bold;
                color: inherit;
                cursor: pointer;
                float: right;
                margin-left: 1rem;
                opacity: 0.7;
            `;
            closeBtn.addEventListener('click', () => {
                alert.remove();
            });
            alert.appendChild(closeBtn);
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = 'opacity 0.3s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

// Modal functionality
function initializeModals() {
    // Close modal when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });

    // Close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function () {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        });
    });
}

// Show modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

// Close modal
function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Tooltip functionality for disabled buttons
function initializeTooltips() {
    const elementsWithTooltips = document.querySelectorAll('[title]');

    elementsWithTooltips.forEach(element => {
        let tooltip = null;

        element.addEventListener('mouseenter', function () {
            if (this.title) {
                tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = this.title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: #333;
                    color: white;
                    padding: 0.5rem;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    z-index: 1000;
                    max-width: 250px;
                    word-wrap: break-word;
                    opacity: 0;
                    transition: opacity 0.3s;
                `;

                document.body.appendChild(tooltip);

                // Position tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + 'px';
                tooltip.style.top = (rect.bottom + 5) + 'px';

                // Show tooltip
                setTimeout(() => {
                    if (tooltip) {
                        tooltip.style.opacity = '1';
                    }
                }, 10);

                // Hide original title to prevent browser tooltip
                this.setAttribute('data-original-title', this.title);
                this.removeAttribute('title');
            }
        });

        element.addEventListener('mouseleave', function () {
            if (tooltip) {
                tooltip.remove();
                tooltip = null;

                // Restore original title
                if (this.getAttribute('data-original-title')) {
                    this.title = this.getAttribute('data-original-title');
                    this.removeAttribute('data-original-title');
                }
            }
        });
    });
}

// Form validation helpers
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Add loading state to buttons
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.setAttribute('data-original-text', button.textContent);
        button.innerHTML = '<span class="loading-spinner"></span> Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text') || 'Submit';
        button.removeAttribute('data-original-text');
    }
}

// Confirm dialog for dangerous actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Initialize dropdown menus
function initializeDropdowns() {
    // Wait a bit to ensure DOM is fully ready
    setTimeout(() => {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

        dropdownToggles.forEach(toggle => {
            // Remove any existing listeners to avoid duplicates
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);

            newToggle.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                const dropdown = this.closest('.dropdown');

                // Close all other dropdowns
                document.querySelectorAll('.dropdown.open').forEach(openDropdown => {
                    if (openDropdown !== dropdown) {
                        openDropdown.classList.remove('open');
                    }
                });

                // Toggle current dropdown
                dropdown.classList.toggle('open');
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.open').forEach(dropdown => {
                    dropdown.classList.remove('open');
                });
            }
        });

        // Close dropdowns with Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.dropdown.open').forEach(dropdown => {
                    dropdown.classList.remove('open');
                });
            }
        });
    }, 100);
}

// Export functions for use in other scripts
window.DogBookingSystem = {
    showModal,
    closeModal,
    validateForm,
    setButtonLoading,
    confirmAction
};