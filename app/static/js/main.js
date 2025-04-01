/**
 * Study Together - Main JavaScript
 * Contains common functions used across the application
 */

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up tooltips (Bootstrap)
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize date formatters
    initDateFormatters();
    
    // Set up auto-dismissing alerts
    setupAutoDismissAlerts();
    
    // Add active class to current nav item
    highlightCurrentNavItem();
    
    // Theme toggling
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        
        // Apply saved theme if it exists
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.documentElement.classList.add('dark-theme');
            updateThemeToggleText(true);
        }
        
        // Add click event to toggle theme
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle dark theme class on both body and html element
            const isDarkTheme = document.body.classList.toggle('dark-theme');
            document.documentElement.classList.toggle('dark-theme', isDarkTheme);
            
            // Save theme preference
            localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
            
            // Update toggle button text
            updateThemeToggleText(isDarkTheme);
        });
    }
    
    // Helper function to update theme toggle button text and icon
    function updateThemeToggleText(isDarkTheme) {
        if (!themeToggle) return;
        
        const icon = themeToggle.querySelector('i');
        
        if (isDarkTheme) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            themeToggle.innerHTML = icon.outerHTML + ' Light Mode';
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            themeToggle.innerHTML = icon.outerHTML + ' Dark Mode';
        }
    }
});

/**
 * Format dates for display using the browser's locale
 */
function initDateFormatters() {
    // Process all elements with the date-format class
    document.querySelectorAll('.date-format').forEach(element => {
        const dateStr = element.getAttribute('data-date');
        if (dateStr) {
            const date = new Date(dateStr);
            element.textContent = formatDate(date, element.getAttribute('data-format') || 'medium');
        }
    });
}

/**
 * Format a date according to the specified format
 * @param {Date} date - The date to format
 * @param {string} format - The format to use (short, medium, long, full)
 * @returns {string} The formatted date string
 */
function formatDate(date, format = 'medium') {
    try {
        const options = { dateStyle: format };
        return new Intl.DateTimeFormat(navigator.language, options).format(date);
    } catch (e) {
        console.error('Error formatting date:', e);
        return date.toDateString();
    }
}

/**
 * Format a time according to the specified format
 * @param {Date} date - The date object containing the time to format
 * @param {string} format - The format to use (short, medium, long, full)
 * @returns {string} The formatted time string
 */
function formatTime(date, format = 'short') {
    try {
        const options = { timeStyle: format };
        return new Intl.DateTimeFormat(navigator.language, options).format(date);
    } catch (e) {
        console.error('Error formatting time:', e);
        return date.toTimeString().substring(0, 5);
    }
}

/**
 * Set up alerts to auto-dismiss after a delay
 */
function setupAutoDismissAlerts() {
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        if (!alert.classList.contains('alert-persistent')) {
            setTimeout(() => {
                // Create a bootstrap alert instance and dismiss it
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000); // 5 seconds
        }
    });
}

/**
 * Add 'active' class to the current nav item based on the URL
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, info, warning)
 */
function showToast(message, type = 'info') {
    // Map type to Bootstrap class
    const typeClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'info': 'bg-info',
        'warning': 'bg-warning'
    }[type] || 'bg-info';
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast ${typeClass} text-white`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Study Together</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add to toast container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toastEl);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Remove the element when hidden
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @returns {Promise} A promise that resolves when the text is copied
 */
function copyToClipboard(text) {
    // Use the newer Clipboard API if available
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text)
            .then(() => true)
            .catch(err => {
                console.error('Failed to copy text:', err);
                return false;
            });
    } else {
        // Fallback for older browsers
        try {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';  // Avoid scrolling to bottom
            document.body.appendChild(textarea);
            textarea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            return Promise.resolve(successful);
        } catch (err) {
            console.error('Failed to copy text:', err);
            return Promise.resolve(false);
        }
    }
} 