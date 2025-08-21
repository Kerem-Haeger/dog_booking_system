/**
 * Appointment Slider JavaScript
 * Handles appointment carousel functionality
 */

class AppointmentSlider {
    // Appointment slider constructor
    constructor(options = {}) {
        this.options = {
            cardSelector: '.appointment-card.compact',
            dotSelector: '.slider-dots .dot',
            prevButtonSelector: '.slider-button.prev',
            nextButtonSelector: '.slider-button.next',
            activeClass: 'active',
            autoSlide: false,
            autoSlideInterval: 5000,
            ...options
        };

        this.currentAppointment = 0;
        this.totalAppointments = 0;
        this.autoSlideTimer = null;

        this.init();
    }

    init() {
        const cards = document.querySelectorAll(this.options.cardSelector);
        const dots = document.querySelectorAll(this.options.dotSelector);

        this.totalAppointments = cards.length;

        if (this.totalAppointments === 0) return;

        // Setup navigation buttons
        this.setupNavigation();

        // Setup dot navigation
        this.setupDotNavigation();

        // Show first appointment
        this.showAppointment(0);

        // Setup auto-slide if enabled
        if (this.options.autoSlide) {
            this.startAutoSlide();
        }
    }

    setupNavigation() {
        const prevButton = document.querySelector(this.options.prevButtonSelector);
        const nextButton = document.querySelector(this.options.nextButtonSelector);

        if (prevButton) {
            prevButton.addEventListener('click', () => this.slideAppointments(-1));
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => this.slideAppointments(1));
        }
    }

    setupDotNavigation() {
        const dots = document.querySelectorAll(this.options.dotSelector);

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => this.showAppointment(index));
        });
    }

    slideAppointments(direction) {
        const newIndex = this.currentAppointment + direction;

        if (newIndex >= this.totalAppointments) {
            this.showAppointment(0);
        } else if (newIndex < 0) {
            this.showAppointment(this.totalAppointments - 1);
        } else {
            this.showAppointment(newIndex);
        }

        // Reset auto-slide timer
        if (this.options.autoSlide) {
            this.resetAutoSlide();
        }
    }

    showAppointment(index) {
        const cards = document.querySelectorAll(this.options.cardSelector);
        const dots = document.querySelectorAll(this.options.dotSelector);

        // Remove active class from current
        if (cards[this.currentAppointment]) {
            cards[this.currentAppointment].classList.remove(this.options.activeClass);
        }
        if (dots[this.currentAppointment]) {
            dots[this.currentAppointment].classList.remove(this.options.activeClass);
        }

        // Update current index
        this.currentAppointment = index;

        // Add active class to new
        if (cards[this.currentAppointment]) {
            cards[this.currentAppointment].classList.add(this.options.activeClass);
        }
        if (dots[this.currentAppointment]) {
            dots[this.currentAppointment].classList.add(this.options.activeClass);
        }
    }

    startAutoSlide() {
        this.autoSlideTimer = setInterval(() => {
            this.slideAppointments(1);
        }, this.options.autoSlideInterval);
    }

    stopAutoSlide() {
        if (this.autoSlideTimer) {
            clearInterval(this.autoSlideTimer);
            this.autoSlideTimer = null;
        }
    }

    resetAutoSlide() {
        this.stopAutoSlide();
        this.startAutoSlide();
    }
}

class AppointmentToggleManager {
    // Appointment toggle manager constructor
    constructor() {
        this.init();
    }

    init() {
        // Setup toggle functions globally for template use
        window.togglePastAppointments = this.togglePastAppointments;
        window.toggleRejectedAppointments = this.toggleRejectedAppointments;
    }

    togglePastAppointments() {
        const content = document.querySelector('.past-appointments-content');
        const icon = document.querySelector('.toggle-icon');

        if (content && icon) {
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.textContent = '▲';
            } else {
                content.style.display = 'none';
                icon.textContent = '▼';
            }
        }
    }

    toggleRejectedAppointments() {
        const content = document.querySelector('.rejected-appointments-content');
        const icon = document.querySelector('.toggle-icon-rejected');

        if (content && icon) {
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.textContent = '▲';
            } else {
                content.style.display = 'none';
                icon.textContent = '▼';
            }
        }
    }
}

// Auto-initialize appointment slider
document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelector('.appointment-card.compact')) {
        new AppointmentSlider();
    }

    // Initialize toggle functionality
    new AppointmentToggleManager();
});

// Export for manual initialization
window.AppointmentSlider = AppointmentSlider;
window.AppointmentToggleManager = AppointmentToggleManager;