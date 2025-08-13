// Client Dashboard JavaScript - Dog Booking System

// Global variables for appointment slider
let currentAppointment = 0;
let totalAppointments = 0;

// Initialize client dashboard functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeAppointmentSlider();
    initializeToggleSections();
});

// Initialize appointment slider functionality
function initializeAppointmentSlider() {
    const cards = document.querySelectorAll('.appointment-card.compact');
    totalAppointments = cards.length;

    if (totalAppointments > 0) {
        // Set initial state - show first appointment
        currentAppointment = 0;
        showAppointment(0);

        // Add event listeners to controls if they exist
        const prevBtn = document.querySelector('.slider-prev');
        const nextBtn = document.querySelector('.slider-next');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => slideAppointments(-1));
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => slideAppointments(1));
        }

        // Add event listeners to dots
        const dots = document.querySelectorAll('.slider-dots .dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showAppointment(index));
        });
    }
}

// Slide appointments in specified direction
function slideAppointments(direction) {
    if (totalAppointments <= 1) return;

    // Calculate new index
    currentAppointment += direction;
    if (currentAppointment >= totalAppointments) currentAppointment = 0;
    if (currentAppointment < 0) currentAppointment = totalAppointments - 1;

    // Show the new appointment
    showAppointment(currentAppointment);
}

// Show specific appointment by index
function showAppointment(index) {
    if (index < 0 || index >= totalAppointments) return;

    const cards = document.querySelectorAll('.appointment-card.compact');
    const dots = document.querySelectorAll('.slider-dots .dot');

    // Hide all cards and dots
    cards.forEach(card => card.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    // Show selected card and dot
    if (cards[index]) {
        cards[index].classList.add('active');
    }
    if (dots[index]) {
        dots[index].classList.add('active');
    }

    currentAppointment = index;
}

// Initialize toggle sections
function initializeToggleSections() {
    // Handle all section toggles with a single event listener
    const toggles = document.querySelectorAll('.section-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const target = this.getAttribute('data-target');
            if (target === 'past') {
                togglePastAppointments();
            } else if (target === 'rejected') {
                toggleRejectedAppointments();
            }
        });
    });
}

// Toggle past appointments visibility
function togglePastAppointments() {
    const content = document.querySelector('.past-appointments-content');
    const icon = document.querySelector('.toggle-icon');

    if (content && icon) {
        if (content.classList.contains('hidden-content')) {
            content.classList.remove('hidden-content');
            content.classList.add('visible-content');
            icon.textContent = '▲';
        } else {
            content.classList.remove('visible-content');
            content.classList.add('hidden-content');
            icon.textContent = '▼';
        }
    }
}

// Toggle rejected appointments visibility
function toggleRejectedAppointments() {
    const content = document.querySelector('.rejected-appointments-content');
    const icon = document.querySelector('.toggle-icon-rejected');

    if (content && icon) {
        if (content.classList.contains('hidden-content')) {
            content.classList.remove('hidden-content');
            content.classList.add('visible-content');
            icon.textContent = '▲';
        } else {
            content.classList.remove('visible-content');
            content.classList.add('hidden-content');
            icon.textContent = '▼';
        }
    }
}

// Export functions to global scope for backward compatibility
window.slideAppointments = slideAppointments;
window.showAppointment = showAppointment;
window.togglePastAppointments = togglePastAppointments;
window.toggleRejectedAppointments = toggleRejectedAppointments;