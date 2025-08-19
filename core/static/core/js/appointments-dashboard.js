/**
 * Appointments Dashboard JavaScript
 * Handles FullCalendar integration, appointment management, and AJAX operations
 */

class AppointmentsDashboard {
    constructor(calendarElement, urls) {
        this.calendarEl = calendarElement;
        this.urls = urls;
        this.calendar = null;
        this.colorManager = null;
        this.modal = null;
        this.employeeFilter = null;

        this.init();
    }

    init() {
        // Initialize components
        this.colorManager = new CalendarColorManager();
        this.employeeFilter = document.getElementById('employee-filter');
        this.modal = document.getElementById('appointmentModal');

        // Initialize calendar
        this.initCalendar();

        // Setup event listeners
        this.setupEventListeners();

        // Make methods globally available for onclick handlers
        this.exposeGlobalMethods();
    }

    initCalendar() {
        this.calendar = new FullCalendar.Calendar(this.calendarEl, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next',
                center: 'title',
                right: ''
            },
            hiddenDays: [0], // Hide Sunday (0 = Sunday)
            slotMinTime: '08:00:00',
            slotMaxTime: '18:00:00',
            timeZone: 'UTC',
            allDaySlot: false,
            height: 'auto',
            events: (fetchInfo, successCallback, failureCallback) => {
                this.fetchCalendarEvents(fetchInfo, successCallback, failureCallback);
            },
            eventClick: (info) => {
                this.handleEventClick(info);
            }
        });

        this.calendar.render();
    }

    fetchCalendarEvents(fetchInfo, successCallback, failureCallback) {
        const employeeId = this.employeeFilter.value;
        const url = `${this.urls.calendar_events}?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}&employee_id=${employeeId}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                try {
                    const coloredEvents = this.colorManager.processCalendarEvents(data);
                    successCallback(coloredEvents);
                } catch (error) {
                    console.error('Error processing calendar colors:', error);
                    successCallback(data);
                }
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                failureCallback(error);
            });
    }

    handleEventClick(info) {
        const event = info.event;
        const props = event.extendedProps;

        // Show appointment details
        const modalContent = document.getElementById('modalContent');
        modalContent.innerHTML = `
            <p><strong>Pet:</strong> ${props.pet_name}</p>
            <p><strong>Service:</strong> ${props.service}</p>
            <p><strong>Employee:</strong> ${props.employee}</p>
            <p><strong>Client:</strong> ${props.client}</p>
            <p><strong>Time:</strong> ${event.start.toLocaleString()}</p>
            <p><strong>Status:</strong> <span class="status-display" data-status-color="${event.backgroundColor}">${props.status.toUpperCase()}</span></p>
            <div id="employeeSection" class="employee-section"></div>
            <div id="loadingIndicator" class="loading-indicator">
                <span>Loading...</span>
            </div>
            <div id="messageArea" class="message-area"></div>
        `;

        // Set status color dynamically
        const statusSpan = modalContent.querySelector('.status-display');
        if (statusSpan) {
            statusSpan.style.color = statusSpan.getAttribute('data-status-color');
        }

        // Load available employees and show appropriate actions
        this.loadEmployeesAndActions(props.appointment_id, props.status);

        this.modal.style.display = 'block';
    }

    loadEmployeesAndActions(appointmentId, status) {
        const employeeSection = document.getElementById('employeeSection');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const modalActions = document.getElementById('modalActions');

        loadingIndicator.style.display = 'block';

        fetch(`${this.urls.available_employees}?appointment_id=${appointmentId}`)
            .then(response => response.json())
            .then(data => {
                console.log('DEBUG: Employee data received:', data);
                loadingIndicator.style.display = 'none';

                if (data.success) {
                    if (status === 'pending') {
                        this.setupPendingAppointmentUI(data.employees, appointmentId, employeeSection, modalActions);
                    } else if (status === 'approved') {
                        this.setupApprovedAppointmentUI(data.employees, data.current_employee, appointmentId, employeeSection, modalActions);
                    } else {
                        // No actions for rejected/completed appointments
                        employeeSection.innerHTML = '';
                        modalActions.innerHTML = '';
                    }
                } else {
                    this.showMessage('Error loading employees: ' + data.error, 'error');
                }
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                this.showMessage('Error loading employees: ' + error.message, 'error');
            });
    }

    setupPendingAppointmentUI(employees, appointmentId, employeeSection, modalActions) {
        const employeeOptions = employees.map(emp =>
            `<option value="${emp.id}">${emp.name}</option>`
        ).join('');

        employeeSection.innerHTML = `
            <label for="employeeSelect"><strong>Assign to Employee:</strong></label>
            <select id="employeeSelect" class="employee-select">
                <option value="">Select an employee...</option>
                ${employeeOptions}
            </select>
            <p class="employee-note">Employee assignment is only required for approval.</p>
        `;

        modalActions.innerHTML = `
            <button onclick="appointmentDashboard.approveAppointment(${appointmentId})" class="approve-btn-modal">✅ Approve</button>
            <button onclick="appointmentDashboard.rejectAppointment(${appointmentId})" class="reject-btn-modal">❌ Reject</button>
        `;
    }

    setupApprovedAppointmentUI(employees, currentEmployee, appointmentId, employeeSection, modalActions) {
        console.log('DEBUG: Setting up approved appointment UI');
        console.log('DEBUG: Available employees:', employees);
        console.log('DEBUG: Current employee:', currentEmployee);

        const employeeOptions = employees.map(emp => {
            const isSelected = emp.id === currentEmployee ? 'selected' : '';
            console.log(`DEBUG: Employee ${emp.id} (${emp.name}) - selected: ${isSelected}`);
            return `<option value="${emp.id}" ${isSelected}>${emp.name}</option>`;
        }).join('');

        console.log('DEBUG: Generated employee options:', employeeOptions);

        employeeSection.innerHTML = `
            <label for="employeeSelect"><strong>Reassign to Employee:</strong></label>
            <select id="employeeSelect" class="employee-select">
                ${employeeOptions}
            </select>
        `;

        modalActions.innerHTML = `
            <button onclick="appointmentDashboard.reassignAppointment(${appointmentId})" class="reassign-btn-modal">🔄 Reassign</button>
        `;

        console.log('DEBUG: UI setup complete for approved appointment');
    }

    approveAppointment(appointmentId) {
        const employeeSelect = document.getElementById('employeeSelect');
        const employeeId = employeeSelect.value;

        if (!employeeId) {
            this.showMessage('Please select an employee first.', 'error');
            return;
        }

        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'block';

        const csrfToken = this.getCSRFToken();

        fetch(this.urls.approve_appointment, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    appointment_id: appointmentId,
                    employee_id: employeeId
                })
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';

                if (data.success) {
                    this.showMessage(data.message, 'success');
                    this.colorManager.updateAppointmentColor(this.calendar, appointmentId, 'approved');
                    setTimeout(() => {
                        this.modal.style.display = 'none';
                    }, 2000);
                } else {
                    this.showMessage('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                this.showMessage('Error: ' + error.message, 'error');
            });
    }

    rejectAppointment(appointmentId) {
        if (!confirm('Are you sure you want to reject this appointment?')) {
            return;
        }

        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'block';

        const csrfToken = this.getCSRFToken();

        fetch(this.urls.reject_appointment, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    appointment_id: appointmentId
                })
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';

                if (data.success) {
                    this.showMessage(data.message, 'success');
                    const event = this.calendar.getEventById(appointmentId);
                    if (event) {
                        event.remove();
                    }
                    setTimeout(() => {
                        this.modal.style.display = 'none';
                    }, 2000);
                } else {
                    this.showMessage('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                this.showMessage('Error: ' + error.message, 'error');
            });
    }

    reassignAppointment(appointmentId) {
        const employeeSelect = document.getElementById('employeeSelect');
        const employeeId = employeeSelect.value;

        console.log('DEBUG: Reassign function called', {
            appointmentId: appointmentId,
            employeeId: employeeId,
            selectElement: employeeSelect
        });

        if (!employeeId) {
            this.showMessage('Please select an employee.', 'error');
            return;
        }

        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = 'block';

        console.log('DEBUG: Sending reassign request');

        const csrfToken = this.getCSRFToken();
        console.log('DEBUG: CSRF token:', csrfToken);

        fetch(this.urls.reassign_appointment, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    appointment_id: appointmentId,
                    employee_id: employeeId
                })
            })
            .then(response => {
                console.log('DEBUG: Response received', response);
                return response.json();
            })
            .then(data => {
                console.log('DEBUG: Response data', data);
                loadingIndicator.style.display = 'none';

                if (data.success) {
                    this.showMessage(data.message, 'success');
                    this.calendar.refetchEvents();
                    setTimeout(() => {
                        this.modal.style.display = 'none';
                    }, 2000);
                } else {
                    this.showMessage('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('DEBUG: Fetch error', error);
                loadingIndicator.style.display = 'none';
                this.showMessage('Error: ' + error.message, 'error');
            });
    }

    showMessage(message, type) {
        const messageArea = document.getElementById('messageArea');
        const cssClass = type === 'error' ? 'message-error' : 'message-success';
        messageArea.innerHTML = `<div class="${cssClass}">${message}</div>`;

        setTimeout(() => {
            messageArea.innerHTML = '';
        }, 3000);
    }

    getCSRFToken() {
        let csrfToken = null;
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            csrfToken = csrfInput.value;
        } else {
            csrfToken = this.getCookie('csrftoken');
        }
        return csrfToken;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setupEventListeners() {
        // Employee filter change
        this.employeeFilter.addEventListener('change', () => {
            this.calendar.refetchEvents();
        });

        // Modal close functionality
        const closeModal = document.getElementById('closeModal');
        closeModal.onclick = () => {
            this.modal.style.display = 'none';
        };

        window.onclick = (event) => {
            if (event.target === this.modal) {
                this.modal.style.display = 'none';
            }
        };
    }

    exposeGlobalMethods() {
        // Make methods available globally for onclick handlers (legacy support)
        window.loadEmployeesAndActions = this.loadEmployeesAndActions.bind(this);
        window.approveAppointmentAjax = this.approveAppointment.bind(this);
        window.rejectAppointmentAjax = this.rejectAppointment.bind(this);
        window.reassignAppointmentAjax = this.reassignAppointment.bind(this);
    }
}

// Global variable to hold the dashboard instance
let appointmentDashboard = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        // URLs will be set from the template
        appointmentDashboard = new AppointmentsDashboard(calendarEl, window.dashboardUrls);
    }

    // Initialize appointment approval form management
    if (typeof ApprovalFormManager !== 'undefined') {
        new ApprovalFormManager({
            formSelector: '.appointment-approval-form',
            sizeSelectSelector: 'select', // This will target the employee select field
            approveButtonSelector: '.approve-btn'
        });
    }
});