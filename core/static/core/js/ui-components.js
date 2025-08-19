/**
 * UI Components JavaScript
 * Reusable UI interaction components
 */

class TabManager {
    constructor(options = {}) {
        this.options = {
            tabButtonSelector: '.tab-button',
            tabContentSelector: '.tab-content',
            activeClass: 'active',
            ...options
        };
        this.init();
    }

    init() {
        const tabButtons = document.querySelectorAll(this.options.tabButtonSelector);
        const tabContents = document.querySelectorAll(this.options.tabContentSelector);

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active from all tabs
                tabButtons.forEach(btn => btn.classList.remove(this.options.activeClass));
                tabContents.forEach(content => content.classList.remove(this.options.activeClass));

                // Add active to clicked tab
                button.classList.add(this.options.activeClass);
                const targetTab = button.getAttribute('data-tab');
                const targetContent = document.getElementById(targetTab + '-tab');
                if (targetContent) {
                    targetContent.classList.add(this.options.activeClass);
                }
            });
        });
    }
}

class CollapsibleManager {
    constructor(options = {}) {
        this.options = {
            headerSelector: '.collapsible-header',
            contentSelector: '.collapsible-content',
            activeClass: 'active',
            ...options
        };
        this.init();
    }

    init() {
        const headers = document.querySelectorAll(this.options.headerSelector);

        headers.forEach(header => {
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                const isActive = header.classList.contains(this.options.activeClass);

                if (isActive) {
                    header.classList.remove(this.options.activeClass);
                    content.style.maxHeight = null;
                } else {
                    header.classList.add(this.options.activeClass);
                    content.style.maxHeight = content.scrollHeight + 'px';
                }
            });
        });
    }
}

class ConfirmationDialogs {
    constructor(options = {}) {
        this.options = {
            confirmButtonSelector: '.confirm-action',
            defaultMessage: 'Are you sure you want to proceed?',
            ...options
        };
        this.init();
    }

    init() {
        document.addEventListener('click', (e) => {
            if (e.target.matches(this.options.confirmButtonSelector) ||
                e.target.closest(this.options.confirmButtonSelector)) {

                const element = e.target.matches(this.options.confirmButtonSelector) ?
                    e.target :
                    e.target.closest(this.options.confirmButtonSelector);

                const message = element.getAttribute('data-confirm-message') || this.options.defaultMessage;

                if (!confirm(message)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }
}

class AlertManager {
    constructor(options = {}) {
        this.options = {
            alertSelector: '.alert',
            dismissibleSelector: '.alert-dismissible',
            closeButtonSelector: '.alert-close',
            autoDismissDelay: 5000,
            ...options
        };
        this.init();
    }

    init() {
        // Auto-dismiss alerts
        const dismissibleAlerts = document.querySelectorAll(this.options.dismissibleSelector);
        dismissibleAlerts.forEach(alert => {
            setTimeout(() => {
                this.dismissAlert(alert);
            }, this.options.autoDismissDelay);
        });

        // Manual close buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches(this.options.closeButtonSelector)) {
                const alert = e.target.closest(this.options.alertSelector);
                if (alert) {
                    this.dismissAlert(alert);
                }
            }
        });
    }

    dismissAlert(alert) {
        alert.style.transition = 'opacity 0.3s ease';
        alert.style.opacity = '0';
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }

    showAlert(message, type = 'info', duration = 5000) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible">
                ${message}
                <button type="button" class="alert-close">&times;</button>
            </div>
        `;

        const container = document.querySelector('.alert-container') || document.body;
        container.insertAdjacentHTML('afterbegin', alertHtml);

        if (duration > 0) {
            setTimeout(() => {
                const alert = container.querySelector('.alert');
                if (alert) {
                    this.dismissAlert(alert);
                }
            }, duration);
        }
    }
}

class SearchManager {
    constructor(options = {}) {
        this.options = {
            searchInputSelectors: ['#pet-search', '#user-search'],
            searchItemSelector: '.collapsible-item',
            searchContentAttribute: 'data-search-content',
            ...options
        };
        this.init();
    }

    init() {
        this.options.searchInputSelectors.forEach(selector => {
            const searchInput = document.querySelector(selector);
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    const searchTerm = e.target.value.toLowerCase();
                    const items = document.querySelectorAll(this.options.searchItemSelector);

                    items.forEach(item => {
                        const searchContent = item.getAttribute(this.options.searchContentAttribute);
                        if (searchContent && searchContent.includes(searchTerm)) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                });
            }
        });
    }
}

class RoleUpdateManager {
    constructor(options = {}) {
        this.options = {
            formSelector: '.inline-form',
            roleInputSelector: '.role-input',
            ...options
        };
        this.init();
    }

    init() {
        const forms = document.querySelectorAll(this.options.formSelector);

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const hiddenInput = form.querySelector(this.options.roleInputSelector);
                if (hiddenInput) {
                    const userId = hiddenInput.getAttribute('data-user-id');
                    const roleSelect = document.getElementById('role_' + userId);

                    if (roleSelect) {
                        hiddenInput.value = roleSelect.value;
                    } else {
                        e.preventDefault();
                        alert('Error: Could not find role selection for this user');
                    }
                }
            });
        });
    }
}

class ApprovalFormManager {
    constructor(options = {}) {
        this.options = {
            formSelector: '.pet-approval-form',
            sizeSelectSelector: 'select',
            approveButtonSelector: '.approve-btn',
            ...options
        };
        this.init();
    }

    init() {
        const forms = document.querySelectorAll(this.options.formSelector);

        forms.forEach(form => {
            const sizeSelect = form.querySelector(this.options.sizeSelectSelector);
            const approveBtn = form.querySelector(this.options.approveButtonSelector);

            if (sizeSelect && approveBtn) {
                // Enable/disable approve button based on size selection
                sizeSelect.addEventListener('change', () => {
                    approveBtn.disabled = !sizeSelect.value;
                });
            }
        });
    }
}

class CancelAppointmentManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            // Prevent base.js from auto-dismissing our custom confirmation
            const cancelWarning = document.getElementById('cancelWarning');
            if (cancelWarning) {
                // Remove any alert classes that might trigger auto-dismiss
                cancelWarning.classList.remove('alert', 'alert-warning');
            }
        });
    }

    toggleWarning() {
        const warning = document.getElementById('cancelWarning');
        if (warning) {
            warning.classList.toggle('hidden');
        }
    }
}

// Auto-initialize common components
document.addEventListener('DOMContentLoaded', function () {
    // Initialize tab management
    if (document.querySelector('.tab-button')) {
        new TabManager();
    }

    // Initialize collapsible management
    if (document.querySelector('.collapsible-header')) {
        new CollapsibleManager();
    }

    // Initialize search functionality
    if (document.querySelector('#pet-search') || document.querySelector('#user-search')) {
        new SearchManager();
    }

    // Initialize approval forms
    if (document.querySelector('.pet-approval-form')) {
        new ApprovalFormManager();
    }

    // Initialize role update forms
    if (document.querySelector('.inline-form')) {
        new RoleUpdateManager();
    }

    // Initialize confirmation dialogs
    new ConfirmationDialogs();

    // Initialize alert management
    new AlertManager();

    // Initialize cancel appointment functionality if present
    if (document.getElementById('cancelWarning')) {
        window.cancelAppointmentManager = new CancelAppointmentManager();
        // Expose toggle function globally for form usage
        window.toggleWarning = () => window.cancelAppointmentManager.toggleWarning();
    }
});

// Export classes for manual initialization
window.TabManager = TabManager;
window.CollapsibleManager = CollapsibleManager;
window.SearchManager = SearchManager;
window.RoleUpdateManager = RoleUpdateManager;
window.ApprovalFormManager = ApprovalFormManager;
window.ConfirmationDialogs = ConfirmationDialogs;
window.AlertManager = AlertManager;
window.CancelAppointmentManager = CancelAppointmentManager;