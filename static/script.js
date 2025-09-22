// Global JavaScript for GCP File Manager
// Provides interactive functionality across all pages

(function() {
    'use strict';

    // Global state
    let isLoading = false;
    let dragDropEnabled = false;
    let notifications = [];

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    function initializeApp() {
        initializeNotifications();
        initializeDragDrop();
        initializeKeyboardShortcuts();
        initializeFormValidation();
        initializeProgressIndicators();
        initializeTooltips();
        initializeSearchFunctionality();

        console.log('GCP File Manager initialized');
    }

    // Notification system
    function initializeNotifications() {
        // Auto-hide flash messages
        const flashMessages = document.querySelectorAll('.flash');
        flashMessages.forEach(function(flash) {
            // Add close functionality if not already present
            const closeBtn = flash.querySelector('.flash-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    hideNotification(flash);
                });
            }

            // Auto-hide after 5 seconds unless it's an error
            if (!flash.classList.contains('flash-error')) {
                setTimeout(function() {
                    hideNotification(flash);
                }, 5000);
            }
        });
    }

    function hideNotification(element) {
        if (element && element.parentElement) {
            element.style.transform = 'translateX(100%)';
            element.style.opacity = '0';
            setTimeout(function() {
                if (element.parentElement) {
                    element.remove();
                }
            }, 300);
        }
    }

    function showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.flash-messages') || createNotificationContainer();

        const notification = document.createElement('div');
        notification.className = `flash flash-${type}`;
        notification.innerHTML = `
            <span class="flash-message">${message}</span>
            <button class="flash-close" onclick="hideNotification(this.parentElement)">
                <i class="icon-close"></i>
            </button>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);

        // Auto-hide
        if (duration > 0) {
            setTimeout(() => hideNotification(notification), duration);
        }

        return notification;
    }

    function createNotificationContainer() {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.querySelector('.main-content').insertBefore(
            container,
            document.querySelector('.main-content').firstChild
        );
        return container;
    }

    // Drag and drop functionality
    function initializeDragDrop() {
        if (!document.getElementById('upload-form')) return;

        dragDropEnabled = true;
        let dragCounter = 0;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop zone
        ['dragenter', 'dragover'].forEach(eventName => {
            document.addEventListener(eventName, handleDragEnter, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, handleDragLeave, false);
        });

        function handleDragEnter(e) {
            dragCounter++;
            document.body.classList.add('drag-hover');

            // Show upload form if not visible
            const uploadForm = document.getElementById('upload-form');
            if (uploadForm && uploadForm.style.display === 'none') {
                showUploadFormWithHighlight();
            }
        }

        function handleDragLeave(e) {
            dragCounter--;
            if (dragCounter === 0) {
                document.body.classList.remove('drag-hover');
            }
        }

        // Handle dropped files
        document.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            dragCounter = 0;
            document.body.classList.remove('drag-hover');

            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                handleFileSelection(files);
            }
        }

        function showUploadFormWithHighlight() {
            const uploadForm = document.getElementById('upload-form');
            if (uploadForm) {
                uploadForm.style.display = 'block';
                uploadForm.classList.add('drag-highlight');
                setTimeout(() => {
                    uploadForm.classList.remove('drag-highlight');
                }, 1000);
            }
        }
    }

    function handleFileSelection(files) {
        const fileInput = document.getElementById('file-input');
        if (fileInput && files.length > 0) {
            // Show upload form
            const uploadForm = document.getElementById('upload-form');
            if (uploadForm) {
                uploadForm.style.display = 'block';
            }

            // Set files to input
            fileInput.files = files;

            // Update file info display
            if (window.updateFileInfo) {
                window.updateFileInfo(fileInput);
            }

            // Validate file
            const file = files[0];
            if (!validateFile(file)) {
                return;
            }

            showNotification(`File "${file.name}" ready for upload`, 'success');
        }
    }

    function validateFile(file) {
        // Get allowed extensions from config
        const fileInput = document.getElementById('file-input');
        const accept = fileInput ? fileInput.getAttribute('accept') : null;

        if (accept) {
            const allowedExtensions = accept.split(',').map(ext => ext.trim().toLowerCase());
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

            if (!allowedExtensions.includes(fileExtension)) {
                showNotification(
                    `File type "${fileExtension}" not allowed. Allowed types: ${allowedExtensions.join(', ')}`,
                    'error'
                );
                return false;
            }
        }

        // Check file size (assuming max size is in a data attribute or config)
        const maxSize = getMaxFileSize();
        if (file.size > maxSize) {
            showNotification(
                `File size (${formatFileSize(file.size)}) exceeds maximum allowed size (${formatFileSize(maxSize)})`,
                'error'
            );
            return false;
        }

        return true;
    }

    function getMaxFileSize() {
        // Default to 100MB, could be read from config
        return 100 * 1024 * 1024;
    }

    // Keyboard shortcuts
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Escape key - close modals and forms
            if (e.key === 'Escape') {
                closeAllModals();
                closeUploadForm();
            }

            // Ctrl/Cmd + U - show upload form
            if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
                e.preventDefault();
                if (window.showUploadForm) {
                    window.showUploadForm();
                }
            }

            // Enter key in modals - trigger primary action
            if (e.key === 'Enter' && document.querySelector('.modal:not([style*="display: none"])')) {
                const modal = document.querySelector('.modal:not([style*="display: none"])');
                const primaryBtn = modal.querySelector('.btn-primary');
                if (primaryBtn && e.target.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    primaryBtn.click();
                }
            }
        });
    }

    function closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }

    function closeUploadForm() {
        if (window.hideUploadForm) {
            window.hideUploadForm();
        }
    }

    // Form validation
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(form)) {
                    e.preventDefault();
                    return false;
                }

                // Show loading indicator for forms
                showLoading();
            });
        });

        // Real-time validation for file inputs
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.files.length > 0) {
                    validateFile(this.files[0]);
                }
            });
        });
    }

    function validateForm(form) {
        let isValid = true;

        // Check required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                clearFieldError(field);
            }
        });

        // Check file inputs
        const fileInputs = form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.required && input.files.length === 0) {
                showFieldError(input, 'Please select a file');
                isValid = false;
            } else if (input.files.length > 0) {
                if (!validateFile(input.files[0])) {
                    isValid = false;
                }
            }
        });

        return isValid;
    }

    function showFieldError(field, message) {
        clearFieldError(field);

        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        errorElement.style.color = '#dc3545';
        errorElement.style.fontSize = '0.8rem';
        errorElement.style.marginTop = '5px';

        field.parentNode.appendChild(errorElement);
        field.style.borderColor = '#dc3545';
    }

    function clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.style.borderColor = '';
    }

    // Progress indicators
    function initializeProgressIndicators() {
        // Show progress for file uploads
        const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
        uploadForms.forEach(form => {
            form.addEventListener('submit', function() {
                showUploadProgress();
            });
        });
    }

    function showUploadProgress() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            const spinner = overlay.querySelector('.loading-spinner p');
            if (spinner) {
                spinner.textContent = 'Uploading file...';
            }
        }
        showLoading();
    }

    // Tooltip functionality
    function initializeTooltips() {
        const elementsWithTitles = document.querySelectorAll('[title]');
        elementsWithTitles.forEach(element => {
            let tooltip = null;

            element.addEventListener('mouseenter', function(e) {
                const title = this.getAttribute('title');
                if (!title) return;

                // Remove title to prevent default tooltip
                this.setAttribute('data-original-title', title);
                this.removeAttribute('title');

                // Create custom tooltip
                tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: #333;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    z-index: 1000;
                    pointer-events: none;
                    white-space: nowrap;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                `;

                document.body.appendChild(tooltip);
                positionTooltip(e, tooltip);
            });

            element.addEventListener('mousemove', function(e) {
                if (tooltip) {
                    positionTooltip(e, tooltip);
                }
            });

            element.addEventListener('mouseleave', function() {
                if (tooltip) {
                    tooltip.remove();
                    tooltip = null;
                }

                // Restore original title
                const originalTitle = this.getAttribute('data-original-title');
                if (originalTitle) {
                    this.setAttribute('title', originalTitle);
                    this.removeAttribute('data-original-title');
                }
            });
        });
    }

    function positionTooltip(e, tooltip) {
        const tooltipRect = tooltip.getBoundingClientRect();
        const x = e.clientX + 10;
        const y = e.clientY - tooltipRect.height - 10;

        tooltip.style.left = Math.min(x, window.innerWidth - tooltipRect.width - 10) + 'px';
        tooltip.style.top = Math.max(y, 10) + 'px';
    }

    // Search functionality
    function initializeSearchFunctionality() {
        // Add search capability to file lists
        addQuickSearch();

        // Add filter functionality
        addFilterOptions();
    }

    function addQuickSearch() {
        const fileContainer = document.querySelector('.file-grid, .file-list');
        if (!fileContainer) return;

        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.style.cssText = 'margin-bottom: 20px;';

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search files...';
        searchInput.className = 'search-input';
        searchInput.style.cssText = `
            width: 100%;
            max-width: 300px;
            padding: 8px 12px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            font-size: 0.9rem;
        `;

        searchContainer.appendChild(searchInput);
        fileContainer.parentNode.insertBefore(searchContainer, fileContainer);

        // Search functionality
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterFiles(this.value.toLowerCase());
            }, 300);
        });
    }

    function filterFiles(searchTerm) {
        const fileItems = document.querySelectorAll('.file-item');
        let visibleCount = 0;

        fileItems.forEach(item => {
            const fileName = item.querySelector('.file-name');
            const fileType = item.querySelector('.file-type');

            if (fileName) {
                const nameText = fileName.textContent.toLowerCase();
                const typeText = fileType ? fileType.textContent.toLowerCase() : '';

                const matches = nameText.includes(searchTerm) || typeText.includes(searchTerm);

                item.style.display = matches ? '' : 'none';
                if (matches) visibleCount++;
            }
        });

        // Update file count
        updateFileCount(visibleCount);
    }

    function updateFileCount(count) {
        const fileCountElement = document.querySelector('.file-count');
        if (fileCountElement) {
            fileCountElement.textContent = `(${count})`;
        }
    }

    function addFilterOptions() {
        // Add file type filters if there are multiple file types
        const fileItems = document.querySelectorAll('.file-item');
        const fileTypes = new Set();

        fileItems.forEach(item => {
            const fileType = item.querySelector('.file-type');
            if (fileType) {
                const type = fileType.textContent.split('/')[0]; // Get main type (image, video, etc.)
                fileTypes.add(type);
            }
        });

        if (fileTypes.size > 1) {
            createFileTypeFilter(Array.from(fileTypes));
        }
    }

    function createFileTypeFilter(types) {
        const searchContainer = document.querySelector('.search-container');
        if (!searchContainer) return;

        const filterSelect = document.createElement('select');
        filterSelect.className = 'file-type-filter';
        filterSelect.style.cssText = `
            margin-left: 10px;
            padding: 8px 12px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            font-size: 0.9rem;
        `;

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'All file types';
        filterSelect.appendChild(defaultOption);

        // Add type options
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
            filterSelect.appendChild(option);
        });

        searchContainer.appendChild(filterSelect);

        // Filter functionality
        filterSelect.addEventListener('change', function() {
            filterByType(this.value);
        });
    }

    function filterByType(selectedType) {
        const fileItems = document.querySelectorAll('.file-item');
        let visibleCount = 0;

        fileItems.forEach(item => {
            const fileType = item.querySelector('.file-type');

            if (fileType) {
                const mainType = fileType.textContent.split('/')[0];
                const matches = !selectedType || mainType === selectedType;

                item.style.display = matches ? '' : 'none';
                if (matches) visibleCount++;
            }
        });

        updateFileCount(visibleCount);
    }

    // Utility functions
    window.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    window.showLoading = function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            isLoading = true;
        }
    };

    window.hideLoading = function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            isLoading = false;
        }
    };

    // API helpers
    window.apiCall = function(url, options = {}) {
        return fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API call failed:', error);
            showNotification('Request failed: ' + error.message, 'error');
            throw error;
        });
    };

    // Export functions for global use
    window.GCPFileManager = {
        showNotification,
        hideNotification,
        formatFileSize: window.formatFileSize,
        showLoading: window.showLoading,
        hideLoading: window.hideLoading,
        apiCall: window.apiCall,
        validateFile
    };

    // Handle browser back/forward
    window.addEventListener('popstate', function(event) {
        // Refresh the page to handle navigation properly
        window.location.reload();
    });

    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, pause any ongoing operations if needed
            console.log('Page hidden');
        } else {
            // Page is visible again
            console.log('Page visible');
        }
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                }
            }, 0);
        });
    }

})();