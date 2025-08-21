/**
 * Form Validation JavaScript
 * Reusable form validation utilities
 */

// Form validation class
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.validators = [];
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validate()) {
                e.preventDefault();
            }
        });
    }

    addValidator(validator) {
        this.validators.push(validator);
        return this;
    }

    validate() {
        let isValid = true;
        for (const validator of this.validators) {
            if (!validator.validate()) {
                isValid = false;
            }
        }
        return isValid;
    }
}

// Date validator class
class DateValidator {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            maxYearsBack: 30,
            allowFuture: false,
            validationMessageId: null,
            submitButtonId: null,
            ...options
        };
        this.validationMessage = this.options.validationMessageId ?
            document.getElementById(this.options.validationMessageId) :
            null;
        this.submitBtn = this.options.submitButtonId ?
            document.getElementById(this.options.submitButtonId) :
            null;

        this.init();
    }

    init() {
        // Set max date to today if future dates not allowed
        if (!this.options.allowFuture) {
            const today = new Date().toISOString().split('T')[0];
            this.input.setAttribute('max', today);
        }

        // Setup event listeners
        this.input.addEventListener('change', () => this.validate());
        this.input.addEventListener('blur', () => this.validate());

        // Initial validation if there's already a value
        if (this.input.value) {
            this.validate();
        }
    }

    validate() {
        const selectedDate = new Date(this.input.value);
        const currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0); // Reset time for comparison

        // Clear previous styles
        this.input.classList.remove('error-input');
        if (this.validationMessage) {
            this.validationMessage.classList.add('date-validation-message');
        }

        if (this.input.value && !this.options.allowFuture && selectedDate > currentDate) {
            // Future date selected
            this.showError('Birth date cannot be in the future.');
            return false;
        } else if (this.input.value && this.options.maxYearsBack) {
            // Check if date is too old
            const maxYearsAgo = new Date();
            maxYearsAgo.setFullYear(maxYearsAgo.getFullYear() - this.options.maxYearsBack);

            if (selectedDate < maxYearsAgo) {
                this.showError(`Birth date cannot be more than ${this.options.maxYearsBack} years ago.`);
                return false;
            }
        }

        // Valid date or empty
        this.clearError();
        return true;
    }

    showError(message) {
        this.input.classList.add('error-input');
        if (this.validationMessage) {
            this.validationMessage.textContent = message;
            this.validationMessage.classList.remove('date-validation-message');
        }
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
        }
    }

    clearError() {
        this.input.classList.remove('error-input');
        if (this.validationMessage) {
            this.validationMessage.textContent = '';
            this.validationMessage.classList.add('date-validation-message');
        }
        if (this.submitBtn) {
            this.submitBtn.disabled = false;
        }
    }
}

// Confirmation validator class
class ConfirmationValidator {
    constructor(options = {}) {
        this.options = {
            message: 'Are you sure you want to proceed?',
            confirmButtonSelectors: ['.confirm-action', '[data-confirm]'],
            ...options
        };
        this.init();
    }

    init() {
        // Setup confirmation for buttons/links
        this.options.confirmButtonSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                element.addEventListener('click', (e) => {
                    const customMessage = element.getAttribute('data-confirm-message') || this.options.message;
                    if (!confirm(customMessage)) {
                        e.preventDefault();
                        return false;
                    }
                });
            });
        });
    }
}

// Auto-initialize common validations
document.addEventListener('DOMContentLoaded', function () {
    // Initialize confirmation dialogs
    new ConfirmationValidator();

    // Auto-initialize pet birth date validation if present
    const petBirthDateInput = document.querySelector('input[name="date_of_birth"]');
    if (petBirthDateInput) {
        new DateValidator(petBirthDateInput, {
            validationMessageId: 'dateValidationMessage',
            submitButtonId: 'submitBtn',
            maxYearsBack: 30,
            allowFuture: false
        });
    }
});

// Export for manual initialization
window.FormValidator = FormValidator;
window.DateValidator = DateValidator;
window.ConfirmationValidator = ConfirmationValidator;