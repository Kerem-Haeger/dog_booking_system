/**
 * Appointment Booking & Editing JavaScript
 * Handles calendar integration and price calculation for appointment booking and editing
 */

class AppointmentBooking {
    constructor(urls, options = {}) {
        this.urls = urls;
        this.options = {
            isEditMode: false,
            currentAppointmentTime: null,
            ...options
        };
        this.calendar = null;
        this.serviceField = null;
        this.timeSlotInput = null;
        this.petField = null;
        this.priceDisplay = null;
        this.form = null;
        this.submitBtn = null;

        this.init();
    }

    init() {
        // Get DOM elements
        this.serviceField = document.getElementById("id_service");
        this.timeSlotInput = document.getElementById("id_time_slot");
        this.petField = document.getElementById("id_pet_profile");
        this.priceDisplay = document.getElementById("price-display");
        this.form = document.querySelector(".booking-form");
        this.submitBtn = document.getElementById("submit-btn");

        // Setup edit mode specific behavior
        if (this.options.isEditMode) {
            this.setupEditMode();
        }

        // Initialize calendar
        this.initCalendar();

        // Setup event listeners
        this.setupEventListeners();

        // Initial price update
        this.updatePrice();
    }

    setupEditMode() {
        // Make pet field readonly in edit mode
        if (this.petField) {
            this.petField.style.pointerEvents = 'none';
            this.petField.style.backgroundColor = '#f8f9fa';
            this.petField.style.color = '#6c757d';
        }

        // Form submission validation for edit mode
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                if (!this.timeSlotInput.value) {
                    e.preventDefault();
                    this.showToast('Please select a new time slot from the calendar', 'error');
                    return false;
                }

                // Disable submit button to prevent double submission
                if (this.submitBtn) {
                    this.submitBtn.disabled = true;
                    this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
                }
            });
        }
    }

    initCalendar() {
        const calendarEl = document.getElementById('calendar');

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            allDaySlot: false,
            selectable: true,
            slotMinTime: "09:00:00",
            slotMaxTime: "18:01:00",
            timeZone: 'UTC',
            hiddenDays: [0], // Sundays closed!
            validRange: {
                start: new Date() // Prevent navigation to past dates
            },
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay'
            },
            height: 'auto',
            events: (info, successCallback, failureCallback) => {
                this.loadAvailableSlots(info, successCallback, failureCallback);
            },
            eventClick: (info) => {
                this.handleSlotSelection(info);
            }
        });

        this.calendar.render();
    }

    loadAvailableSlots(info, successCallback, failureCallback) {
        const serviceId = this.serviceField.value;
        if (!serviceId) return;

        const url = `${this.urls.available_slots}?service_id=${serviceId}&start=${info.startStr}&end=${info.endStr}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                successCallback(data);
            })
            .catch(error => {
                console.error("Error loading slots:", error);
                failureCallback(error);
            });
    }

    handleSlotSelection(info) {
        // Set the selected time slot
        this.timeSlotInput.value = info.event.start.toISOString();

        // Reset all event colors and highlight selected
        this.calendar.getEvents().forEach(e => e.setProp('backgroundColor', '#3788d8'));
        info.event.setProp('backgroundColor', '#28a745');

        // Show confirmation message
        const message = this.options.isEditMode ?
            'New time slot selected: ' + info.event.start.toLocaleString() :
            'Time slot selected: ' + info.event.start.toLocaleString();

        this.showToast(message);
    }

    updatePrice() {
        const petId = this.petField.value;
        const serviceId = this.serviceField.value;

        if (!petId || !serviceId) {
            const message = this.options.isEditMode ?
                "<strong>Price:</strong> Please select a service." :
                "<strong>Price:</strong> Please choose your pet and service first!";
            this.priceDisplay.innerHTML = message;
            this.priceDisplay.className = "price-display";
            return;
        }

        const url = `${this.urls.get_price}?pet_id=${petId}&service_id=${serviceId}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.price) {
                    const priceLabel = this.options.isEditMode ? "New Price" : "Price";
                    this.priceDisplay.innerHTML = `<strong>${priceLabel}:</strong> £${data.price}`;
                    this.priceDisplay.className = "price-display price-available";
                } else {
                    this.priceDisplay.innerHTML = "<strong>Price:</strong> Not available for this selection.";
                    this.priceDisplay.className = "price-display price-unavailable";
                }
            })
            .catch(error => {
                console.error("Error fetching price:", error);
                this.priceDisplay.innerHTML = "<strong>Price:</strong> Error fetching price.";
                this.priceDisplay.className = "price-display price-error";
            });
    }

    showToast(message, type = 'success') {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.textContent = message;

        const bgColor = type === 'error' ? '#dc3545' : '#28a745';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 1000;
            transition: opacity 0.3s;
            max-width: 300px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }

    setupEventListeners() {
        // Refetch slots when service changes
        this.serviceField.addEventListener("change", () => {
            this.calendar.refetchEvents();
            this.updatePrice();
        });

        // Update price when pet changes (not in edit mode since pet is readonly)
        if (!this.options.isEditMode && this.petField) {
            this.petField.addEventListener("change", () => {
                this.updatePrice();
            });
        }
    }
}

// Make showToast available globally for compatibility
window.showToast = function (message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;

    const bgColor = type === 'error' ? '#dc3545' : '#28a745';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 1rem;
        border-radius: 4px;
        z-index: 1000;
        transition: opacity 0.3s;
        max-width: 300px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 4000);
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
    if (window.bookingUrls) {
        const options = window.bookingOptions || {};
        new AppointmentBooking(window.bookingUrls, options);
    }
});