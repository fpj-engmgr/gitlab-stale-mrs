let currentStaleDays = 7;
let currentGroup = null;
let currentSortColumn = 'days_open';
let currentSortDirection = 'desc';

async function loadGroups() {
    try {
        const response = await fetch('/api/groups');
        const data = await response.json();

        if (data.mode === 'multi') {
            populateGroupSelector(data.groups);
            document.getElementById('groupFilter').style.display = 'inline-block';
            document.querySelector('label[for="groupFilter"]').style.display = 'inline-block';
        } else {
            document.getElementById('groupFilter').style.display = 'none';
            document.querySelector('label[for="groupFilter"]').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

function populateGroupSelector(groups) {
    const selector = document.getElementById('groupFilter');
    groups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.name;
        selector.appendChild(option);
    });
}

async function fetchStaleMRs() {
    try {
        showLoading();

        const groupParam = currentGroup ? `&group_id=${currentGroup}` : '';
        const response = await fetch(`/api/stale-mrs?stale_days=${currentStaleDays}${groupParam}`);
        const data = await response.json();

        updateMetricCards(data);
        updateStaleMRsTable(data.stale_mrs);
        hideLoading();
    } catch (error) {
        console.error('Error fetching stale MRs:', error);
        showError('Failed to load stale MRs: ' + error.message);
        hideLoading();
    }
}

function showLoading() {
    document.querySelectorAll('.metric-card .value').forEach(el => {
        el.innerHTML = '<div class="loading">...</div>';
    });
}

function hideLoading() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => el.remove());
}

function showError(message) {
    const container = document.querySelector('.container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
}

function updateMetricCards(data) {
    document.getElementById('total-open').textContent = data.total_open;
    document.getElementById('stale-count').textContent = data.stale_count;

    // Calculate percentage
    const percentage = data.total_open > 0
        ? ((data.stale_count / data.total_open) * 100).toFixed(1)
        : '0.0';
    document.getElementById('stale-percentage').textContent = percentage + '%';

    // Update stale label
    document.getElementById('stale-label').textContent = `Open >${data.stale_threshold_days}d`;
    document.getElementById('threshold-display').textContent = data.stale_threshold_days;

    // Color-code stale card
    const staleCard = document.querySelector('.stale-card');
    if (data.stale_count > 0) {
        staleCard.classList.add('warning');
    } else {
        staleCard.classList.remove('warning');
    }

    // Update last updated time
    if (data.last_updated) {
        const lastUpdated = new Date(data.last_updated);
        const now = new Date();
        const diffMinutes = Math.floor((now - lastUpdated) / 1000 / 60);

        let timeAgo;
        if (diffMinutes < 1) {
            timeAgo = 'Just now';
        } else if (diffMinutes < 60) {
            timeAgo = `${diffMinutes}m ago`;
        } else {
            const hours = Math.floor(diffMinutes / 60);
            timeAgo = `${hours}h ago`;
        }

        document.getElementById('last-updated').textContent = timeAgo;
    }
}

function updateStaleMRsTable(staleMRs) {
    const tbody = document.getElementById('staleMRsTableBody');
    tbody.innerHTML = '';

    if (staleMRs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--card-subtext);">🎉 No stale MRs! Great job keeping things current.</td></tr>';
        return;
    }

    // Sort MRs
    const sorted = sortStaleMRs(staleMRs);

    sorted.forEach(mr => {
        const row = document.createElement('tr');
        row.className = `stale-${mr.severity}`;

        const createdDate = new Date(mr.created_at).toLocaleDateString();

        row.innerHTML = `
            <td>${escapeHtml(mr.title)}</td>
            <td>${escapeHtml(mr.project_name)}</td>
            <td>${escapeHtml(mr.author)}</td>
            <td><strong>${mr.days_open}</strong> days</td>
            <td>${createdDate}</td>
            <td><a href="${mr.web_url}" target="_blank" class="btn-link">View MR →</a></td>
        `;

        tbody.appendChild(row);
    });
}

function sortStaleMRs(mrs) {
    return [...mrs].sort((a, b) => {
        let aVal, bVal;

        switch (currentSortColumn) {
            case 'title':
                aVal = a.title.toLowerCase();
                bVal = b.title.toLowerCase();
                break;
            case 'project':
                aVal = a.project_name.toLowerCase();
                bVal = b.project_name.toLowerCase();
                break;
            case 'author':
                aVal = a.author.toLowerCase();
                bVal = b.author.toLowerCase();
                break;
            case 'days_open':
                aVal = a.days_open;
                bVal = b.days_open;
                break;
            case 'created':
                aVal = new Date(a.created_at);
                bVal = new Date(b.created_at);
                break;
            default:
                return 0;
        }

        if (aVal < bVal) return currentSortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

function handleSort(column) {
    if (currentSortColumn === column) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortDirection = column === 'days_open' ? 'desc' : 'asc';
    }

    // Update sort indicators
    document.querySelectorAll('th.sortable').forEach(th => {
        th.removeAttribute('data-sort');
    });
    const th = document.querySelector(`th[data-column="${column}"]`);
    th.setAttribute('data-sort', currentSortDirection);

    // Re-fetch to apply sort
    fetchStaleMRs();
}

function changeStaleDays() {
    currentStaleDays = parseInt(document.getElementById('staleDays').value);
    fetchStaleMRs();
}

function changeGroup() {
    currentGroup = document.getElementById('groupFilter').value || null;
    fetchStaleMRs();
}

async function refreshData() {
    const btn = document.getElementById('refreshBtn');
    btn.textContent = 'Refreshing...';
    btn.disabled = true;

    try {
        await fetch('/api/refresh', { method: 'POST' });
        await fetchStaleMRs();
    } catch (error) {
        console.error('Error refreshing data:', error);
        showError('Failed to refresh data: ' + error.message);
    } finally {
        btn.textContent = 'Refresh Data';
        btn.disabled = false;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Dark mode functionality
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');

    const toggleBtn = document.getElementById('darkModeToggle');
    toggleBtn.textContent = isDark ? '☀️' : '🌙';

    localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
}

function loadDarkModePreference() {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
        const toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) {
            toggleBtn.textContent = '☀️';
        }
    }
}

// Load dark mode preference before page renders
loadDarkModePreference();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGroups();
    fetchStaleMRs();

    document.getElementById('refreshBtn').addEventListener('click', refreshData);
    document.getElementById('staleDays').addEventListener('change', changeStaleDays);
    document.getElementById('groupFilter').addEventListener('change', changeGroup);
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    // Add click handlers for table sortable headers
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.getAttribute('data-column');
            handleSort(column);
        });
    });
});
