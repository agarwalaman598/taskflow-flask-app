// Task Management App JavaScript

// Global app configuration
const App = {
    config: {
        apiBase: '/api',
        debounceDelay: 300,
        animationDuration: 300
    },

    // Initialize the application
    init: function () {
        this.bindEvents();
        this.initializeComponents();
        console.log('Task Management App initialized');
    },

    // Bind event listeners
    bindEvents: function () {
        // Form validation
        document.addEventListener('DOMContentLoaded', this.initFormValidation);

        // Search functionality
        const searchInputs = document.querySelectorAll('input[name="search"]');
        searchInputs.forEach(input => {
            input.addEventListener('input', this.debounce(this.handleSearch, this.config.debounceDelay));
        });

        // Auto-submit filters
        const filterSelects = document.querySelectorAll('select[name="status"], select[name="priority"]');
        filterSelects.forEach(select => {
            select.addEventListener('change', this.autoSubmitFilters);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts);

        // Auto-resize textareas
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', this.autoResizeTextarea);
        });

        // Confirm delete actions
        
        const deleteButtons = document.querySelectorAll('form[action*="/delete"] button[type="submit"], .delete-task');
        deleteButtons.forEach(button => {
            button.closest('form').addEventListener('submit', this.confirmDelete);
        });
    },

    // Initialize components
    initializeComponents: function () {
        this.initTooltips();
        this.initProgressBars();
        this.initCardAnimations();
        this.initDateInputs();
    },

    // Initialize Bootstrap tooltips
    initTooltips: function () {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    // Initialize progress bars with animation
    initProgressBars: function () {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    },

    // Initialize card animations
    initCardAnimations: function () {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 50}ms`;
            card.classList.add('fade-in');
        });
    },

    // Initialize date inputs
    initDateInputs: function () {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];

        dateInputs.forEach(input => {
            if (!input.hasAttribute('min')) {
                input.setAttribute('min', today);
            }
        });
    },

    // Form validation
    initFormValidation: function () {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    // Handle search with debouncing
    handleSearch: function (event) {
        const searchTerm = event.target.value.trim();
        const form = event.target.closest('form');

        if (searchTerm.length >= 3 || searchTerm.length === 0) {
            if (form) {
                form.submit();
            }
        }
    },

    // Auto-submit filters
    autoSubmitFilters: function (event) {
        const form = event.target.closest('form');
        if (form) {
            form.submit();
        }
    },

    // Handle keyboard shortcuts
    handleKeyboardShortcuts: function (event) {
        // Ctrl/Cmd + Enter to submit forms
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                activeForm.submit();
            }
        }

        // Escape to close modals/dropdowns
        if (event.key === 'Escape') {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                const toggle = dropdown.previousElementSibling;
                if (toggle && typeof bootstrap !== 'undefined') {
                    bootstrap.Dropdown.getInstance(toggle)?.hide();
                }
            });
        }

        // Ctrl/Cmd + N for new task (on tasks page)
        if ((event.ctrlKey || event.metaKey) && event.key === 'n' && window.location.pathname.includes('tasks')) {
            event.preventDefault();
            window.location.href = '/tasks/create';
        }
    },

    // Auto-resize textareas
    autoResizeTextarea: function (event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    },

    // Confirm delete actions
    confirmDelete: function (event) {
        const message = event.target.dataset.confirmMessage ||
            'Are you sure you want to delete this item? This action cannot be undone.';

        if (!confirm(message)) {
            event.preventDefault();
            return false;
        }
    },

    // Utility: Debounce function
    debounce: function (func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Show loading state
    showLoading: function (element) {
        if (element) {
            element.classList.add('loading');
            element.disabled = true;
        }
    },

    // Hide loading state
    hideLoading: function (element) {
        if (element) {
            element.classList.remove('loading');
            element.disabled = false;
        }
    },

    // Show alert message
    showAlert: function (type, message, duration = 5000) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('main .container');
        if (container) {
            const firstChild = container.firstElementChild;
            firstChild.insertAdjacentHTML('beforebegin', alertHtml);

            // Auto-dismiss after duration
            if (duration > 0) {
                setTimeout(() => {
                    const alert = container.querySelector('.alert');
                    if (alert && typeof bootstrap !== 'undefined') {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    }
                }, duration);
            }
        }
    },

    // API helper methods
    api: {
        // Make API request
        request: async function (url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const mergedOptions = { ...defaultOptions, ...options };

            try {
                const response = await fetch(url, mergedOptions);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Request failed');
                }

                return data;
            } catch (error) {
                console.error('API Request failed:', error);
                throw error;
            }
        },

        // Get tasks
        getTasks: function (filters = {}) {
            const params = new URLSearchParams(filters);
            return this.request(`${App.config.apiBase}/tasks?${params}`);
        },

        // Create task
        createTask: function (taskData) {
            return this.request(`${App.config.apiBase}/tasks`, {
                method: 'POST',
                body: JSON.stringify(taskData)
            });
        },

        // Update task
        updateTask: function (taskId, taskData) {
            return this.request(`${App.config.apiBase}/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify(taskData)
            });
        },

        // Delete task
        deleteTask: function (taskId) {
            return this.request(`${App.config.apiBase}/tasks/${taskId}`, {
                method: 'DELETE'
            });
        },

        // Get statistics
        getStatistics: function () {
            return this.request(`${App.config.apiBase}/statistics`);
        }
    },

    // Task management functions
    tasks: {
        // Toggle task status
        toggleStatus: async function (taskId) {
            try {
                App.showLoading(document.querySelector(`[data-task-id="${taskId}"]`));

                const response = await fetch(`/tasks/${taskId}/toggle-status`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (data.success) {
                    App.showAlert('success', data.message);
                    // Reload page after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    App.showAlert('danger', data.error || 'Failed to update task');
                }
            } catch (error) {
                console.error('Error toggling task status:', error);
                App.showAlert('danger', 'An error occurred while updating the task');
            } finally {
                App.hideLoading(document.querySelector(`[data-task-id="${taskId}"]`));
            }
        },

        // Delete task with confirmation
        delete: async function (taskId, taskTitle) {
            const confirmMessage = `Are you sure you want to delete "${taskTitle}"? This action cannot be undone.`;

            if (!confirm(confirmMessage)) {
                return;
            }

            try {
                const response = await App.api.deleteTask(taskId);
                App.showAlert('success', 'Task deleted successfully');

                // Remove task card from DOM
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.style.transition = 'opacity 0.3s ease';
                    taskCard.style.opacity = '0';
                    setTimeout(() => {
                        taskCard.remove();
                    }, 300);
                }
            } catch (error) {
                console.error('Error deleting task:', error);
                App.showAlert('danger', error.message || 'Failed to delete task');
            }
        }
    },

    // Utility functions
    utils: {
        // Format date
        formatDate: function (dateString, options = {}) {
            const defaultOptions = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            const mergedOptions = { ...defaultOptions, ...options };
            return new Date(dateString).toLocaleDateString(undefined, mergedOptions);
        },

        // Format relative time
        formatRelativeTime: function (dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);

            if (diffInSeconds < 60) return 'just now';
            if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
            if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
            if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;

            return this.formatDate(dateString);
        },

        // Get priority color class
        getPriorityColor: function (priority) {
            const colors = {
                'low': 'success',
                'medium': 'warning',
                'high': 'danger'
            };
            return colors[priority] || 'secondary';
        },

        // Get status color class
        getStatusColor: function (status) {
            const colors = {
                'pending': 'secondary',
                'in_progress': 'primary',
                'completed': 'success'
            };
            return colors[status] || 'secondary';
        },

        // Truncate text
        truncateText: function (text, maxLength = 100) {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    App.init();
});

// Global functions for template use
window.toggleTaskStatus = function (taskId) {
    App.tasks.toggleStatus(taskId);
};

window.deleteTask = function (taskId, taskTitle) {
    App.tasks.delete(taskId, taskTitle);
};

// Service Worker registration for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function (registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function (error) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}

/* =================================================================
   Timezone Conversion and Formatting
   ================================================================= */
document.addEventListener('DOMContentLoaded', function() {
    /**
     * Converts UTC timestamp strings to the user's local date and time.
     */
    function formatLocalTimes() {
        const timeElements = document.querySelectorAll('.local-time');
        timeElements.forEach(el => {
            const utcDateString = el.textContent.trim();
            if (utcDateString) {
                const localDate = new Date(utcDateString);
                // Format: Aug 16, 2025, 04:20 PM
                const options = {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                };
                el.textContent = localDate.toLocaleString('en-IN', options);
            }
        });
    }

    /**
     * Converts UTC timestamp strings to the user's local date only.
     */
    function formatLocalDates() {
        const dateElements = document.querySelectorAll('.local-date');
        dateElements.forEach(el => {
            const utcDateString = el.textContent.trim();
            if (utcDateString) {
                const localDate = new Date(utcDateString);
                // Format: Aug 16, 2025
                const options = {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                };
               el.textContent = localDate.toLocaleDateString('en-IN', options);
            }
        });
    }

    // Run the functions to format all dates and times on the page
    formatLocalTimes();
    formatLocalDates();
});
