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

    console.log(`Initializing slider with ${totalAppointments} appointments`);

    if (totalAppointments > 1) {
        // Set initial state
        currentAppointment = 0;

        // Ensure first appointment is active and others are not
        cards.forEach((card, index) => {
            if (index === 0) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });

        // Same for dots
        const dots = document.querySelectorAll('.slider-dots .dot');
        dots.forEach((dot, index) => {
            if (index === 0) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });

        // Add event listeners to controls
        const prevBtn = document.querySelector('.slider-prev');
        const nextBtn = document.querySelector('.slider-next');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                console.log('Previous button clicked');
                slideAppointments(-1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                console.log('Next button clicked');
                slideAppointments(1);
            });
        }

        // Add event listeners to dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                console.log(`Dot ${index + 1} clicked`);
                showAppointment(index);
            });
        });

        console.log('Slider initialized successfully');

    } else if (totalAppointments === 1) {
        // If only one appointment, make sure it's active
        const firstCard = cards[0];
        const firstDot = document.querySelector('.slider-dots .dot');
        if (firstCard) {
            firstCard.classList.add('active');
        }
        if (firstDot) {
            firstDot.classList.add('active');
        }
        console.log('Single appointment made active');
    } else {
        console.log('No appointments to display');
    }
}

// Slide appointments in specified direction
function slideAppointments(direction) {
    const cards = document.querySelectorAll('.appointment-card.compact');
    const dots = document.querySelectorAll('.slider-dots .dot');

    if (totalAppointments <= 1) {
        return; // No sliding needed for 0 or 1 appointments
    }

    console.log(`Before slide: currentAppointment = ${currentAppointment}`);

    // Remove active class from current
    if (cards[currentAppointment]) {
        cards[currentAppointment].classList.remove('active');
        console.log(`Removed active from appointment ${currentAppointment}`);
        if (dots[currentAppointment]) {
            dots[currentAppointment].classList.remove('active');
        }
    }

    // Calculate new index
    currentAppointment += direction;
    if (currentAppointment >= totalAppointments) currentAppointment = 0;
    if (currentAppointment < 0) currentAppointment = totalAppointments - 1;

    console.log(`After calculation: currentAppointment = ${currentAppointment}`);

    // Add active class to new appointment
    if (cards[currentAppointment]) {
        cards[currentAppointment].classList.add('active');
        console.log(`Added active to appointment ${currentAppointment}`);
        console.log(`Classes on current card:`, cards[currentAppointment].className);
        console.log(`Computed style display:`, window.getComputedStyle(cards[currentAppointment]).display);
        console.log(`Card position:`, cards[currentAppointment].getBoundingClientRect());

        if (dots[currentAppointment]) {
            dots[currentAppointment].classList.add('active');
        }
    }

    // Debug all cards
    console.log('=== ALL CARDS STATUS ===');
    cards.forEach((card, index) => {
        const rect = card.getBoundingClientRect();
        console.log(`Card ${index}: classes="${card.className}", display="${window.getComputedStyle(card).display}", visible=${rect.width > 0 && rect.height > 0}`);
    });

    console.log(`Slid to appointment ${currentAppointment + 1} of ${totalAppointments}`);
}

// Show specific appointment by index
function showAppointment(index) {
    const cards = document.querySelectorAll('.appointment-card.compact');
    const dots = document.querySelectorAll('.slider-dots .dot');

    // Validate index
    if (index < 0 || index >= totalAppointments) {
        return;
    }

    // Remove active from all
    cards.forEach(card => card.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    // Add active to selected
    currentAppointment = index;
    if (cards[index]) {
        cards[index].classList.add('active');
        if (dots[index]) {
            dots[index].classList.add('active');
        }
    }

    // Debug logging (remove in production)
    console.log(`Showing appointment ${index + 1} of ${totalAppointments}`);
}

// Initialize toggle sections (past appointments, rejected appointments)
function initializeToggleSections() {
    console.log('Initializing toggle sections');

    // Past appointments toggle
    const pastToggle = document.querySelector('.past-appointments-section .section-toggle');
    if (pastToggle) {
        pastToggle.addEventListener('click', () => {
            console.log('Past appointments toggle clicked');
            togglePastAppointments();
        });
        console.log('Past appointments toggle initialized');
    } else {
        console.log('No past appointments toggle found');
    }

    // Rejected appointments toggle
    const rejectedToggle = document.querySelector('.rejected-appointments-section .section-toggle');
    if (rejectedToggle) {
        rejectedToggle.addEventListener('click', () => {
            console.log('Rejected appointments toggle clicked');
            toggleRejectedAppointments();
        });
        console.log('Rejected appointments toggle initialized');
    } else {
        console.log('No rejected appointments toggle found');
    }
}

// Toggle past appointments visibility
function togglePastAppointments() {
    const content = document.querySelector('.past-appointments-content');
    const icon = document.querySelector('.toggle-icon');

    console.log('togglePastAppointments called');

    if (content && icon) {
        // Force toggle the class and update icon
        if (content.style.display === 'none' || content.classList.contains('hidden-content')) {
            // Show content
            content.classList.remove('hidden-content');
            content.style.display = 'block';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0)';
            icon.textContent = '▲';
            console.log('Content shown');
        } else {
            // Hide content
            content.classList.add('hidden-content');
            content.style.display = 'none';
            icon.textContent = '▼';
            console.log('Content hidden');
        }
    }
}

// Toggle rejected appointments visibility
function toggleRejectedAppointments() {
    const content = document.querySelector('.rejected-appointments-content');
    const icon = document.querySelector('.toggle-icon-rejected');

    console.log('toggleRejectedAppointments called');

    if (content && icon) {
        // Force toggle the class and update icon
        if (content.style.display === 'none' || content.classList.contains('hidden-content')) {
            // Show content
            content.classList.remove('hidden-content');
            content.style.display = 'block';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0)';
            icon.textContent = '▲';
            console.log('Rejected content shown');
        } else {
            // Hide content
            content.classList.add('hidden-content');
            content.style.display = 'none';
            icon.textContent = '▼';
            console.log('Rejected content hidden');
        }
    }
} // Export functions to global scope for backward compatibility
window.slideAppointments = slideAppointments;
window.showAppointment = showAppointment;
window.togglePastAppointments = togglePastAppointments;
window.toggleRejectedAppointments = toggleRejectedAppointments;

// Export module for modern usage
window.ClientDashboard = {
    slideAppointments,
    showAppointment,
    togglePastAppointments,
    toggleRejectedAppointments,
    initializeAppointmentSlider,
    initializeToggleSections
};