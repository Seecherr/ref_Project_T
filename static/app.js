/* ===================================================================
   Library Management System — Client-Side Application Logic
   =================================================================== */

const API = '/api';

// ---------------------------------------------------------------------------
// Tab Navigation
// ---------------------------------------------------------------------------

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Deactivate all
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

        // Activate selected
        btn.classList.add('active');
        const tabId = 'tab-' + btn.dataset.tab;
        document.getElementById(tabId).classList.add('active');

        // Load data for the tab
        loadTabData(btn.dataset.tab);
    });
});

function loadTabData(tab) {
    switch (tab) {
        case 'books': loadBooks(); break;
        case 'members': loadMembers(); break;
        case 'loans': loadLoans(); break;
        case 'reservations': loadReservations(); break;
        case 'fines': break; // loaded on demand
    }
}

// ---------------------------------------------------------------------------
// API Helper
// ---------------------------------------------------------------------------

async function apiCall(endpoint, options = {}) {
    try {
        const resp = await fetch(API + endpoint, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        const data = await resp.json();
        if (!resp.ok) {
            throw new Error(data.error || `Request failed (${resp.status})`);
        }
        return data;
    } catch (err) {
        throw err;
    }
}

// ---------------------------------------------------------------------------
// Toast Notifications
// ---------------------------------------------------------------------------

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Modal Management
// ---------------------------------------------------------------------------

function showModal(id) {
    document.getElementById(id).classList.add('show');
}

function hideModal(id) {
    document.getElementById(id).classList.remove('show');
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('show');
        }
    });
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.show').forEach(m => m.classList.remove('show'));
    }
});

// ---------------------------------------------------------------------------
// Books
// ---------------------------------------------------------------------------

async function loadBooks() {
    try {
        const books = await apiCall('/books');
        renderBooks(books);
    } catch (err) {
        showToast('Failed to load books: ' + err.message, 'error');
    }
}

async function searchBooks() {
    const query = document.getElementById('bookSearch').value.trim();
    try {
        const endpoint = query ? `/books?q=${encodeURIComponent(query)}` : '/books';
        const books = await apiCall(endpoint);
        renderBooks(books);
    } catch (err) {
        showToast('Search failed: ' + err.message, 'error');
    }
}

// Search on Enter key
document.getElementById('bookSearch').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchBooks();
});

function renderBooks(books) {
    const tbody = document.getElementById('booksBody');
    const empty = document.getElementById('booksEmpty');

    if (books.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = books.map(b => `
        <tr>
            <td><code style="color:var(--accent)">${escapeHtml(b.isbn)}</code></td>
            <td style="color:var(--text-primary);font-weight:500">${escapeHtml(b.title)}</td>
            <td>${escapeHtml(b.author)}</td>
            <td>${escapeHtml(b.subject || '—')}</td>
            <td>${b.year || '—'}</td>
            <td><span class="badge ${b.available_copies > 0 ? 'badge-available' : 'badge-overdue'}">${b.available_copies}</span></td>
            <td>${b.total_copies}</td>
        </tr>
    `).join('');
}

async function addBook(e) {
    e.preventDefault();
    try {
        await apiCall('/books', {
            method: 'POST',
            body: JSON.stringify({
                isbn: document.getElementById('bookIsbn').value.trim(),
                title: document.getElementById('bookTitle').value.trim(),
                author: document.getElementById('bookAuthor').value.trim(),
                subject: document.getElementById('bookSubject').value.trim(),
                year: parseInt(document.getElementById('bookYear').value) || 0,
            }),
        });
        hideModal('addBookModal');
        e.target.reset();
        showToast('Book added successfully', 'success');
        loadBooks();
    } catch (err) {
        showToast('Failed to add book: ' + err.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Members
// ---------------------------------------------------------------------------

async function loadMembers() {
    try {
        const members = await apiCall('/members');
        renderMembers(members);
    } catch (err) {
        showToast('Failed to load members: ' + err.message, 'error');
    }
}

function renderMembers(members) {
    const tbody = document.getElementById('membersBody');
    const empty = document.getElementById('membersEmpty');

    if (members.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = members.map(m => {
        const statusClass = m.status === 'active' ? 'badge-active' : 'badge-blocked';
        const booksOut = m.total_books_checked_out !== undefined ? m.total_books_checked_out : '—';
        return `
        <tr>
            <td><code style="color:var(--accent)">${escapeHtml(m.member_id)}</code></td>
            <td style="color:var(--text-primary);font-weight:500">${escapeHtml(m.name)}</td>
            <td>${escapeHtml(m.email)}</td>
            <td><span class="badge badge-${m.type === 'Librarian' ? 'fulfilled' : 'available'}">${m.type}</span></td>
            <td><span class="badge ${statusClass}">${m.status}</span></td>
            <td>${booksOut}</td>
        </tr>
        `;
    }).join('');
}

async function addMember(e) {
    e.preventDefault();
    const body = {
        name: document.getElementById('memberName').value.trim(),
        email: document.getElementById('memberEmail').value.trim(),
        type: document.getElementById('memberType').value,
    };
    const memberId = document.getElementById('memberId').value.trim();
    if (memberId) body.member_id = memberId;

    try {
        await apiCall('/members', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        hideModal('addMemberModal');
        e.target.reset();
        showToast('Member registered successfully', 'success');
        loadMembers();
    } catch (err) {
        showToast('Failed to register member: ' + err.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Loans
// ---------------------------------------------------------------------------

async function loadLoans() {
    try {
        const loans = await apiCall('/loans');
        renderLoans(loans);
    } catch (err) {
        showToast('Failed to load loans: ' + err.message, 'error');
    }
}

function renderLoans(loans) {
    const tbody = document.getElementById('loansBody');
    const empty = document.getElementById('loansEmpty');

    if (loans.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = loans.map(l => {
        let statusBadge;
        if (!l.is_active) {
            statusBadge = '<span class="badge badge-returned">Returned</span>';
        } else if (l.is_overdue) {
            statusBadge = '<span class="badge badge-overdue">Overdue</span>';
        } else {
            statusBadge = '<span class="badge badge-loaned">Active</span>';
        }
        return `
        <tr>
            <td><code style="color:var(--text-muted);font-size:0.8rem">${escapeHtml(l.loan_id.substring(0, 8))}…</code></td>
            <td><code style="color:var(--accent)">${escapeHtml(l.member_id)}</code></td>
            <td style="font-weight:500">${escapeHtml(l.book_item_barcode)}</td>
            <td>${l.issue_date}</td>
            <td>${l.due_date}</td>
            <td>${l.return_date || '—'}</td>
            <td>${statusBadge}</td>
        </tr>
        `;
    }).join('');
}

async function borrowBook(e) {
    e.preventDefault();
    try {
        await apiCall('/loans', {
            method: 'POST',
            body: JSON.stringify({
                member_id: document.getElementById('borrowMemberId').value.trim(),
                barcode: document.getElementById('borrowBarcode').value.trim(),
            }),
        });
        hideModal('borrowModal');
        e.target.reset();
        showToast('Book borrowed successfully', 'success');
        loadLoans();
        loadBooks(); // refresh availability
    } catch (err) {
        showToast('Failed to borrow: ' + err.message, 'error');
    }
}

async function returnBook(e) {
    e.preventDefault();
    try {
        const result = await apiCall('/loans/return', {
            method: 'POST',
            body: JSON.stringify({
                barcode: document.getElementById('returnBarcode').value.trim(),
            }),
        });
        hideModal('returnModal');
        e.target.reset();

        let msg = 'Book returned successfully';
        if (result.fine_created) {
            msg += ` — Fine of $${result.fine_created.amount} created`;
        }
        showToast(msg, 'success');
        loadLoans();
        loadBooks();
    } catch (err) {
        showToast('Failed to return: ' + err.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Reservations
// ---------------------------------------------------------------------------

async function loadReservations() {
    try {
        const reservations = await apiCall('/reservations');
        renderReservations(reservations);
    } catch (err) {
        showToast('Failed to load reservations: ' + err.message, 'error');
    }
}

function renderReservations(reservations) {
    const tbody = document.getElementById('reservationsBody');
    const empty = document.getElementById('reservationsEmpty');

    if (reservations.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = reservations.map(r => {
        const statusClass = {
            waiting: 'badge-waiting',
            fulfilled: 'badge-fulfilled',
            cancelled: 'badge-cancelled',
        }[r.status] || '';
        return `
        <tr>
            <td><code style="color:var(--text-muted);font-size:0.8rem">${escapeHtml(r.reservation_id.substring(0, 8))}…</code></td>
            <td><code style="color:var(--accent)">${escapeHtml(r.member_id)}</code></td>
            <td><code>${escapeHtml(r.book_isbn)}</code></td>
            <td>${new Date(r.created_at).toLocaleDateString()}</td>
            <td><span class="badge ${statusClass}">${r.status}</span></td>
        </tr>
        `;
    }).join('');
}

async function placeReservation(e) {
    e.preventDefault();
    try {
        await apiCall('/reservations', {
            method: 'POST',
            body: JSON.stringify({
                member_id: document.getElementById('reserveMemberId').value.trim(),
                book_isbn: document.getElementById('reserveIsbn').value.trim(),
            }),
        });
        hideModal('reserveModal');
        e.target.reset();
        showToast('Reservation placed successfully', 'success');
        loadReservations();
    } catch (err) {
        showToast('Failed to place reservation: ' + err.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Fines
// ---------------------------------------------------------------------------

async function lookupFines() {
    const memberId = document.getElementById('fineMemberSearch').value.trim();
    if (!memberId) {
        showToast('Please enter a Member ID', 'error');
        return;
    }

    try {
        const data = await apiCall(`/fines/${encodeURIComponent(memberId)}`);
        renderFines(data);
    } catch (err) {
        showToast('Failed to load fines: ' + err.message, 'error');
    }
}

// Lookup on Enter
document.getElementById('fineMemberSearch').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') lookupFines();
});

function renderFines(data) {
    const summary = document.getElementById('finesSummary');
    const tbody = document.getElementById('finesBody');
    const empty = document.getElementById('finesEmpty');

    document.getElementById('finesMemberId').textContent = data.member_id;
    document.getElementById('finesTotalUnpaid').textContent = '$' + data.total_unpaid;
    summary.style.display = 'flex';

    if (data.fines.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        empty.querySelector('p').textContent = 'No unpaid fines for this member';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = data.fines.map(f => `
        <tr>
            <td><code style="color:var(--text-muted);font-size:0.8rem">${escapeHtml(f.fine_id.substring(0, 8))}…</code></td>
            <td><code style="font-size:0.8rem">${escapeHtml(f.loan_id.substring(0, 8))}…</code></td>
            <td style="font-weight:600;color:var(--text-primary)">$${f.amount}</td>
            <td>$${f.paid}</td>
            <td style="color:var(--red);font-weight:600">$${f.outstanding}</td>
            <td>
                ${f.is_fully_paid
                    ? '<span class="badge badge-available">Paid</span>'
                    : `<button class="btn btn-sm btn-primary" onclick="openPayFine('${f.fine_id}', ${parseFloat(f.outstanding)})">Pay</button>`
                }
            </td>
        </tr>
    `).join('');
}

function openPayFine(fineId, outstanding) {
    document.getElementById('payFineId').value = fineId;
    document.getElementById('payAmount').value = outstanding;
    document.getElementById('payAmount').max = outstanding;
    showModal('payFineModal');
}

async function payFine(e) {
    e.preventDefault();
    const fineId = document.getElementById('payFineId').value;
    const amount = document.getElementById('payAmount').value;

    try {
        await apiCall(`/fines/${encodeURIComponent(fineId)}/pay`, {
            method: 'POST',
            body: JSON.stringify({ amount: amount }),
        });
        hideModal('payFineModal');
        showToast('Payment applied successfully', 'success');
        lookupFines(); // refresh
    } catch (err) {
        showToast('Payment failed: ' + err.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Health Check
// ---------------------------------------------------------------------------

async function checkHealth() {
    const status = document.getElementById('headerStatus');
    try {
        await apiCall('/health');
        status.innerHTML = '<span class="status-dot"></span><span>API Connected</span>';
        status.style.color = 'var(--green)';
        status.style.background = 'var(--green-soft)';
    } catch {
        status.innerHTML = '<span>⚠️ Disconnected</span>';
        status.style.color = 'var(--red)';
        status.style.background = 'var(--red-soft)';
    }
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadBooks();
});
