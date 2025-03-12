document.addEventListener('DOMContentLoaded', () => {
    initializeFormValidation();
    initializeToastNotifications();
    initializeAppointmentFetching();
});

// Toast Notifications
function initializeToastNotifications() {
    window.showToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.getElementById('toast-container').appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => toast.remove(), 3000);
    };
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', (e) => {
            const input = e.target;
            const errorSpan = input.nextElementSibling;
            if (input.checkValidity()) {
                errorSpan.style.display = 'none';
            } else {
                errorSpan.style.display = 'block';
                errorSpan.textContent = input.validationMessage;
            }
        });
    });
}

// Appointment Fetching
function initializeAppointmentFetching() {
    document.getElementById('fetch-appointments').addEventListener('click', async () => {
        const response = await fetch('/api/appointments');
        const result = await response.json();
        const list = document.getElementById('appointments-list');
        list.innerHTML = '';
        result.appointments.forEach(app => {
            const li = document.createElement('li');
            li.textContent = `${app.patientName} - ${app.date} at ${app.time} (${app.status})`;
            list.appendChild(li);
        });
    });
}

// Book Appointment
document.getElementById('book-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = collectFormData(e.target);
    const response = await fetch('/api/book-appointment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    showToast(result.message || result.error, result.error ? 'error' : 'success');
});

// Reschedule Appointment
document.getElementById('reschedule-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = collectFormData(e.target);
    const response = await fetch('/api/reschedule-appointment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    showToast(result.message || result.error, result.error ? 'error' : 'success');
});

// Cancel Appointment
document.getElementById('cancel-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = collectFormData(e.target);
    const response = await fetch('/api/cancel-appointment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    showToast(result.message || result.error, result.error ? 'error' : 'success');
});

// Helper Function to Collect Form Data
function collectFormData(form) {
    const data = {};
    Array.from(form.elements).forEach(element => {
        if (element.name) data[element.name] = element.value;
    });
    return data;
}