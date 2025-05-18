// Validation utility functions
const validation = {
    // Email validation
    isValidEmail: (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Username validation (3-20 characters, alphanumeric and underscore)
    isValidUsername: (username) => {
        const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
        return usernameRegex.test(username);
    },

    // Password validation (min 8 chars, at least one number, one uppercase, one lowercase)
    isValidPassword: (password) => {
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        return passwordRegex.test(password);
    },

    // Name validation (2-50 characters, letters and spaces)
    isValidName: (name) => {
        const nameRegex = /^[a-zA-Z\s]{2,50}$/;
        return nameRegex.test(name);
    },

    // Subject validation (2-100 characters)
    isValidSubject: (subject) => {
        return subject.length >= 2 && subject.length <= 100;
    },

    // Location validation (2-200 characters)
    isValidLocation: (location) => {
        return location.length >= 2 && location.length <= 200;
    },

    // Description validation (max 1000 characters)
    isValidDescription: (description) => {
        return description.length <= 1000;
    },

    // Message validation (1-500 characters)
    isValidMessage: (message) => {
        return message.length >= 1 && message.length <= 500;
    },

    // Number validation (min, max)
    isValidNumber: (number, min, max) => {
        const num = parseInt(number);
        return !isNaN(num) && num >= min && num <= max;
    },

    // Date validation (end date must be after start date)
    isValidDateRange: (startDate, endDate) => {
        return new Date(endDate) > new Date(startDate);
    },

    // Show validation error
    showError: (containerId, message) => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    },

    // Clear validation error
    clearError: (containerId) => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
}; 