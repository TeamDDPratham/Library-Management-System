/**
 * Library Management System - Frontend JavaScript Logic
 * Production-ready UX: accessible confirmation modals, button loading states,
 * dynamic search filters, mobile navigation, and real-time previews.
 */

let activeConfirmCallback = null;
let activeConfirmForm = null;

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // 1. Mobile Navigation & Drawer Controls
    // -------------------------------------------------------------
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    const sidebar = document.getElementById('appSidebar') || document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function openMobileSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (mobileBtn) {
        mobileBtn.addEventListener('click', openMobileSidebar);
    }
    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', closeMobileSidebar);
    }
    if (overlay) {
        overlay.addEventListener('click', closeMobileSidebar);
    }

    // Auto-close mobile sidebar if window resized to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar && sidebar.classList.contains('open')) {
            closeMobileSidebar();
        }
    });

    // -------------------------------------------------------------
    // 2. Auto-Dismiss Flash Alerts with Smooth Fade
    // -------------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-6px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // -------------------------------------------------------------
    // 3. Modal Keydown & Backdrop Click Listeners
    // -------------------------------------------------------------
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeConfirmModal();
            const openModals = document.querySelectorAll('.modal-backdrop');
            openModals.forEach(m => {
                if (m.style.display !== 'none') {
                    m.style.display = 'none';
                }
            });
            closeMobileSidebar();
        }
    });

    const modalBackdrops = document.querySelectorAll('.modal-backdrop');
    modalBackdrops.forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                if (backdrop.id === 'globalConfirmModal') {
                    closeConfirmModal();
                } else {
                    backdrop.style.display = 'none';
                }
            }
        });
    });

    // -------------------------------------------------------------
    // 4. Form Submit Loading States & Duplicate Submission Prevention
    // -------------------------------------------------------------
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            // Skip forms handled by client-side modals or validation checks
            if (form.dataset.noLoading === 'true' || e.defaultPrevented) return;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('btn-loading')) {
                // If form is valid
                if (form.checkValidity && !form.checkValidity()) return;

                const origHtml = submitBtn.innerHTML;
                submitBtn.dataset.originalHtml = origHtml;
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;

                // Re-enable after 8 seconds timeout as safety fallback
                setTimeout(() => {
                    if (submitBtn.classList.contains('btn-loading')) {
                        submitBtn.classList.remove('btn-loading');
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.dataset.originalHtml || origHtml;
                    }
                }, 8000);
            }
        });
    });

    // -------------------------------------------------------------
    // 5. Author Search Filter in Modals
    // -------------------------------------------------------------
    initAuthorSearchFilter('add_author_search', 'add_authors_container');
    initAuthorSearchFilter('edit_author_search', 'edit_authors_container');

    // -------------------------------------------------------------
    // 6. Interactive Book Selection in Issue Loan Form
    // -------------------------------------------------------------
    initIssueBookPreview();
});

// -----------------------------------------------------------------
// Global Confirmation Modal Implementation
// -----------------------------------------------------------------
/**
 * Opens a modern, styled confirmation dialog.
 * @param {Object} options
 * @param {string} options.title - Modal title heading
 * @param {string} options.message - Main question or warning
 * @param {string} [options.details] - Contextual detail string (book/member name)
 * @param {string} [options.confirmText="Confirm"] - Text for the confirm button
 * @param {string} [options.confirmClass="btn-danger"] - CSS class for the button
 * @param {string} [options.icon="alert-triangle"] - Lucide icon name
 * @param {string} [options.iconType="danger"] - danger | warning | primary | info
 * @param {HTMLFormElement} [options.form] - Form to submit upon confirmation
 * @param {Function} [options.onConfirm] - Callback to execute upon confirmation
 */
function showConfirmDialog(options) {
    const modal = document.getElementById('globalConfirmModal');
    if (!modal) return;

    const titleEl = document.getElementById('confirmModalTitle');
    const messageEl = document.getElementById('confirmModalMessage');
    const detailsEl = document.getElementById('confirmModalDetails');
    const submitBtn = document.getElementById('confirmModalSubmitBtn');
    const iconWrapper = document.getElementById('confirmModalIconWrapper');
    const iconEl = document.getElementById('confirmModalIcon');

    titleEl.textContent = options.title || 'Are you sure?';
    messageEl.textContent = options.message || 'Please confirm to continue with this action.';

    if (options.details) {
        detailsEl.innerHTML = options.details;
        detailsEl.style.display = 'block';
    } else {
        detailsEl.style.display = 'none';
        detailsEl.innerHTML = '';
    }

    // Set button styling & text
    submitBtn.textContent = options.confirmText || 'Confirm';
    submitBtn.className = 'btn btn-block ' + (options.confirmClass || 'btn-danger');

    // Set icon type & wrapper classes
    const iconType = options.iconType || (options.confirmClass && options.confirmClass.includes('danger') ? 'danger' : 'primary');
    iconWrapper.className = 'confirm-icon-wrapper confirm-icon-' + iconType;
    if (iconEl) {
        iconEl.setAttribute('data-lucide', options.icon || 'alert-triangle');
    }

    // Store callbacks / form
    activeConfirmCallback = typeof options.onConfirm === 'function' ? options.onConfirm : null;
    activeConfirmForm = options.form || null;

    // Hook click listener on confirm button
    submitBtn.onclick = function () {
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        if (activeConfirmForm) {
            activeConfirmForm.submit();
        } else if (activeConfirmCallback) {
            activeConfirmCallback();
            closeConfirmModal();
        } else {
            closeConfirmModal();
        }
    };

    modal.style.display = 'flex';
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function closeConfirmModal() {
    const modal = document.getElementById('globalConfirmModal');
    if (modal) {
        modal.style.display = 'none';
        const submitBtn = document.getElementById('confirmModalSubmitBtn');
        if (submitBtn) {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
        }
    }
    activeConfirmCallback = null;
    activeConfirmForm = null;
}

// -----------------------------------------------------------------
// Standard Modal Open / Close Helpers
// -----------------------------------------------------------------
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// -----------------------------------------------------------------
// Filter Authors dynamically within Add/Edit Book Modals
// -----------------------------------------------------------------
function initAuthorSearchFilter(searchInputId, containerId) {
    const searchInput = document.getElementById(searchInputId);
    const container = document.getElementById(containerId);
    if (!searchInput || !container) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const labels = container.querySelectorAll('.checkbox-label');
        labels.forEach(label => {
            const authorName = label.querySelector('span')?.textContent.toLowerCase() || '';
            if (authorName.includes(query)) {
                label.style.display = 'flex';
            } else {
                label.style.display = 'none';
            }
        });
    });
}

// -----------------------------------------------------------------
// Live Book Catalog Preview in Issue Loan Form
// -----------------------------------------------------------------
function initIssueBookPreview() {
    const bookSelect = document.getElementById('issue_book_select');
    const previewContainer = document.getElementById('selectedBookPreview');
    if (!bookSelect || !previewContainer) return;

    bookSelect.addEventListener('change', () => {
        const selectedOption = bookSelect.options[bookSelect.selectedIndex];
        if (!selectedOption || !selectedOption.value) {
            previewContainer.style.display = 'none';
            return;
        }

        const title = selectedOption.dataset.title || selectedOption.text;
        const isbn = selectedOption.dataset.isbn || '';
        const category = selectedOption.dataset.category || 'General';
        const available = parseInt(selectedOption.dataset.available || '0');
        const total = parseInt(selectedOption.dataset.total || '0');
        const price = selectedOption.dataset.price || '0.00';

        document.getElementById('prev_title').textContent = title;
        document.getElementById('prev_isbn').textContent = isbn;
        document.getElementById('prev_category').textContent = category;
        document.getElementById('prev_stock').textContent = `${available} of ${total} copies available`;
        document.getElementById('prev_price').textContent = `₹${price}`;

        const stockFill = document.getElementById('prev_stock_fill');
        if (stockFill && total > 0) {
            const pct = Math.max(0, Math.min(100, Math.round((available / total) * 100)));
            stockFill.style.width = pct + '%';
            if (pct === 0) stockFill.className = 'stock-bar-fill fill-danger';
            else if (pct < 35) stockFill.className = 'stock-bar-fill fill-warning';
            else stockFill.className = 'stock-bar-fill fill-success';
        }

        previewContainer.style.display = 'block';
        if (window.lucide) window.lucide.createIcons();
    });
}
