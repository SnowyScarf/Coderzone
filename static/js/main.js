// Main JavaScript file for CodeMarket
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(function() {
                    alert.remove();
                }, 150);
            }
        }, 5000);
    });

    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                let feedback = input.parentElement.querySelector('.file-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'file-feedback mt-2';
                    input.parentElement.appendChild(feedback);
                }
                
                if (file.type === 'application/zip' || file.name.endsWith('.zip')) {
                    feedback.innerHTML = `
                        <small class="text-success">
                            <i class="fas fa-check-circle me-1"></i>
                            ${fileName} (${fileSize} MB)
                        </small>
                    `;
                } else {
                    feedback.innerHTML = `
                        <small class="text-danger">
                            <i class="fas fa-exclamation-circle me-1"></i>
                            Please select a ZIP file
                        </small>
                    `;
                }
            }
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function(input) {
        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });

    // Price formatting
    const priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Confirmation dialogs
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Dynamic badge colors based on content
    const badges = document.querySelectorAll('.badge');
    badges.forEach(function(badge) {
        const text = badge.textContent.toLowerCase();
        if (text.includes('python')) {
            badge.classList.add('bg-success');
        } else if (text.includes('javascript')) {
            badge.classList.add('bg-warning');
        } else if (text.includes('java')) {
            badge.classList.add('bg-danger');
        } else if (text.includes('web')) {
            badge.classList.add('bg-info');
        }
    });

    // Loading states for buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = this.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    });

    // Store original button text
    submitButtons.forEach(function(button) {
        button.setAttribute('data-original-text', button.textContent);
    });
});

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 3000);
    }
}

// Export functions for global use
window.CodeMarket = {
    formatPrice,
    formatDate,
    showNotification
};
