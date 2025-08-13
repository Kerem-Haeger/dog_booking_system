/**
 * Calendar Color Management - Client-side optimization
 * Handles appointment coloring logic in JavaScript for better performance
 */

class CalendarColorManager {
    constructor() {
        this.colors = {
            // Status-based colors
            approved: '#28a745', // Green
            pending: '#ffc107', // Yellow  
            completed: '#6c757d', // Gray
            rejected: '#dc3545', // Red
            default: '#6c757d' // Default gray
        };

        this.transparentSuffix = '80'; // For past appointments
    }

    /**
     * Get color for appointment based on status and time
     * @param {string} status - Appointment status
     * @param {boolean} isPast - Whether appointment is in the past
     * @returns {object} Color object with background and border colors
     */
    getAppointmentColors(status, isPast = false) {
        let baseColor = this.colors[status] || this.colors.default;

        // Apply transparency for past appointments
        if (isPast) {
            baseColor = baseColor + this.transparentSuffix;
        }

        return {
            backgroundColor: baseColor,
            borderColor: baseColor
        };
    }

    /**
     * Process calendar events and apply colors
     * @param {Array} events - Array of calendar events
     * @returns {Array} Events with color properties added
     */
    processCalendarEvents(events) {
        if (!Array.isArray(events)) {
            console.warn('CalendarColorManager: Expected events to be an array, got:', typeof events);
            return [];
        }

        const now = new Date();

        return events.map(event => {
            try {
                const eventStart = new Date(event.start);
                const isPast = eventStart < now;
                const status = event.extendedProps ? .status || 'default';
                const colors = this.getAppointmentColors(status, isPast);

                return {
                    ...event,
                    backgroundColor: colors.backgroundColor,
                    borderColor: colors.borderColor,
                    extendedProps: {
                        ...event.extendedProps,
                        is_past: isPast
                    }
                };
            } catch (error) {
                console.error('CalendarColorManager: Error processing event:', event, error);
                // Return event with default colors if processing fails
                const defaultColors = this.getAppointmentColors('default', false);
                return {
                    ...event,
                    backgroundColor: defaultColors.backgroundColor,
                    borderColor: defaultColors.borderColor,
                    extendedProps: {
                        ...event.extendedProps,
                        is_past: false
                    }
                };
            }
        });
    }

    /**
     * Real-time color update for status changes
     * @param {object} calendarInstance - FullCalendar instance
     * @param {number} appointmentId - Appointment ID to update
     * @param {string} newStatus - New appointment status
     */
    updateAppointmentColor(calendarInstance, appointmentId, newStatus) {
        const event = calendarInstance.getEventById(appointmentId);
        if (event) {
            const eventStart = new Date(event.start);
            const isPast = eventStart < new Date();
            const colors = this.getAppointmentColors(newStatus, isPast);

            event.setProp('backgroundColor', colors.backgroundColor);
            event.setProp('borderColor', colors.borderColor);
            event.setExtendedProp('status', newStatus);
        }
    }
}

// Export for use in other files
window.CalendarColorManager = CalendarColorManager;