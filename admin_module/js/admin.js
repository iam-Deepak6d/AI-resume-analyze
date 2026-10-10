/* ==========================================================================
   TalentLens AI - Admin Module Dedicated Controller
   ========================================================================== */

let currentAdminUser = null;

document.addEventListener('DOMContentLoaded', async () => {
  initAdminAuthCheck();
  initAdminTabs();
  initJobModal();
  initAdminTheme();
});

async function initAdminAuthCheck() {
  currentAdminUser = await API.getMe();
  if (!currentAdminUser || currentAdminUser.role !== 'admin') {
    window.location.href = '/admin/login';
    return;
  }

  // Set user chip
  const adminName = document.getElementById('admin-chip-name');
  if (adminName) adminName.textContent = currentAdminUser.name.split(' ')[0];

  // Logout button
  const logoutBtn = document.getElementById('admin-logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await API.logout();
      window.location.href = '/admin/login';
    });
  }

  // Initial load
  loadOverviewMetrics();
}

function initAdminTabs() {
  const tabs = document.querySelectorAll('.admin-subtab-btn');
  const panes = document.querySelectorAll('.admin-pane');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panes.forEach(p => p.style.display = 'none');

      tab.classList.add('active');
      const paneId = tab.dataset.adminPane;
      const targetPane = document.getElementById(paneId);
      if (targetPane) targetPane.style.display = 'block';

      if (paneId === 'admin-pane-audit') {
        loadLiveAuditStream();
      } else if (paneId === 'admin-pane-users') {
        loadUsersDirectory();
      } else if (paneId === 'admin-pane-candidates') {
        loadCandidatesRoster();
      } else if (paneId === 'admin-pane-ranker') {
        loadRankingJobsDropdown();
      } else if (paneId === 'admin-pane-overview') {
        loadOverviewMetrics();
      }
    });
  });

  // Refresh button
  const refreshBtn = document.getElementById('admin-refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      loadOverviewMetrics();
      loadLiveAuditStream();
      loadUsersDirectory();
      showToast('Admin data refreshed from database.', 'info');
    });
  }
}

// 1. Overview KPIs
async function loadOverviewMetrics() {
  try {
    const data = await API.getAdminMetrics();
    document.getElementById('metric-total-users').textContent = data.total_users || 2;
    document.getElementById('metric-total-candidates').textContent = data.total_candidates || 0;
    document.getElementById('metric-avg-ats').textContent = `${data.avg_ats_score}%`;
    document.getElementById('metric-active-jobs').textContent = data.total_jobs_active || 0;
    document.getElementById('metric-applications').textContent = data.total_applications || 0;
    document.getElementById('metric-total-logs').textContent = data.total_logs || 0;

    // Load top skills badges
    const topSkillsWrap = document.getElementById('top-in-demand-skills-wrap');
    if (topSkillsWrap && data.top_in_demand_skills) {
      topSkillsWrap.innerHTML = data.top_in_demand_skills.map(([s, count]) => 
        `<span class="skill-pill" style="border-color: rgba(6, 182, 212, 0.4); color: #38bdf8;">${s} (${count})</span>`
      ).join('');
    }

    const topGapsWrap = document.getElementById('top-fresher-gaps-wrap');
    if (topGapsWrap && data.top_skill_gaps_fresher) {
      topGapsWrap.innerHTML = data.top_skill_gaps_fresher.map(([s, count]) => 
        `<span class="skill-pill pill-missing">⚠️ ${s} (${count})</span>`
      ).join('');
    }
  } catch (err) {
    console.error(err);
    showToast(err.message, 'error');
  }
}

// 2. Real-Time Live Activity & Login Stream
async function loadLiveAuditStream() {
  const tbody = document.getElementById('admin-audit-logs-tbody');
  if (!tbody) return;

  try {
    const data = await API.getAdminLogs(150);
    tbody.innerHTML = '';

    if (data.logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 2rem;">No logged events yet.</td></tr>';
      return;
    }

    data.logs.forEach(log => {
      const tr = document.createElement('tr');
      let pillClass = 'log-action-RESUME';
      if (log.action.includes('LOGIN')) pillClass = 'log-action-LOGIN';
      else if (log.action.includes('APPLIED')) pillClass = 'log-action-APPLIED';
      else if (log.action.includes('ENHANCED')) pillClass = 'log-action-ENHANCED';
      else if (log.action.includes('BLOCKED') || log.action.includes('FAILED')) pillClass = 'log-action-BLOCKED';

      tr.innerHTML = `
        <td style="font-family: monospace; font-size: 0.8rem; color: var(--text-dim); white-space: nowrap;">${log.created_at}</td>
        <td><strong>${log.user_name || 'Guest'}</strong><br/><span style="font-size: 0.75rem; color: var(--text-dim);">${log.user_email || 'N/A'}</span></td>
        <td><span class="hero-pill ${log.role === 'admin' ? 'badge-rose' : 'badge-indigo'}" style="margin: 0; padding: 0.15rem 0.5rem; font-size: 0.7rem;">${(log.role || 'user').toUpperCase()}</span></td>
        <td><span class="log-action-pill ${pillClass}">${log.action}</span></td>
        <td style="font-size: 0.85rem; max-width: 320px;">${log.details}</td>
        <td style="font-family: monospace; font-size: 0.78rem; color: var(--text-dim);">${log.ip_address || '127.0.0.1'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="6" style="color: var(--accent-rose); text-align: center;">Error loading logs: ${err.message}</td></tr>`;
  }
}

// 3. User Directory & Governance
async function loadUsersDirectory() {
  const tbody = document.getElementById('admin-users-tbody');
  if (!tbody) return;

  try {
    const data = await API.getAdminUsers();
    tbody.innerHTML = '';

    data.users.forEach(u => {
      const tr = document.createElement('tr');
      const isSelf = currentAdminUser && currentAdminUser.id === u.id;
      const statusClass = u.status === 'active' ? 'badge-emerald' : 'badge-rose';

      tr.innerHTML = `
        <td><strong>${u.name}</strong></td>
        <td>${u.email}</td>
        <td><span class="hero-pill ${u.role === 'admin' ? 'badge-rose' : 'badge-indigo'}" style="margin: 0; padding: 0.15rem 0.5rem; font-size: 0.7rem;">${u.role.toUpperCase()}</span></td>
        <td>${u.target_role || 'General'}</td>
        <td><span style="font-weight: 700; color: var(--primary-light);">${u.resumes_analyzed}</span></td>
        <td><span style="font-weight: 700; color: var(--secondary);">${u.jobs_applied}</span></td>
        <td style="font-size: 0.8rem; color: var(--text-dim);">${u.last_login || 'Never'}</td>
        <td><span class="hero-pill ${statusClass}" style="margin: 0; padding: 0.15rem 0.5rem; font-size: 0.7rem;">${u.status.toUpperCase()}</span></td>
        <td>
          ${isSelf ? '<span style="font-size: 0.75rem; color: var(--text-dim);">Current Admin</span>' : `
            <button class="btn btn-secondary toggle-user-btn" data-user-id="${u.id}" data-status="${u.status}" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">
              ${u.status === 'active' ? '⛔ Suspend' : '✓ Activate'}
            </button>
          `}
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.querySelectorAll('.toggle-user-btn').forEach(btn => {
      btn.onclick = async () => {
        const uid = btn.dataset.userId;
        try {
          const res = await API.toggleUserStatus(uid);
          showToast(`User status updated to ${res.new_status}.`, 'info');
          loadUsersDirectory();
        } catch (e) {
          showToast(e.message, 'error');
        }
      };
    });
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="9" style="color: var(--accent-rose); text-align: center;">Error loading users: ${err.message}</td></tr>`;
  }
}

// 4. Autonomous Candidate Ranker
async function loadRankingJobsDropdown() {
  const select = document.getElementById('admin-rank-job-select');
  if (!select) return;

  try {
    const data = await API.getJobs();
    select.innerHTML = '<option value="">-- Choose Job Opening to Rank Applicants --</option>';
    data.jobs.forEach(j => {
      select.innerHTML += `<option value="${j.id}">${j.title} @ ${j.company}</option>`;
    });

    select.onchange = () => {
      if (select.value) loadRankedResults(select.value);
    };
  } catch (err) {
    console.error(err);
  }
}

async function loadRankedResults(jobId) {
  const tbody = document.getElementById('admin-ranked-results-tbody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem;">Evaluating candidate resumes with vector fit...</td></tr>';

  try {
    const data = await API.rankCandidatesForJob(jobId);
    tbody.innerHTML = '';
    if (data.ranked_candidates.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 2rem;">No candidates uploaded yet.</td></tr>';
      return;
    }

    data.ranked_candidates.forEach((c, idx) => {
      const tr = document.createElement('tr');
      const badgeClass = c.job_match_score >= 80 ? 'badge-emerald' : 'badge-cyan';
      tr.innerHTML = `
        <td><strong>#${idx + 1}</strong></td>
        <td><strong>${c.name}</strong> (${c.target_role})</td>
        <td><span class="hero-pill ${badgeClass}" style="margin: 0; padding: 0.2rem 0.6rem;">${c.job_match_score}% Fit</span></td>
        <td>${c.ats_score}/100</td>
        <td>${c.matched_skills.slice(0, 5).join(', ')}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="color: var(--accent-rose);">${err.message}</td></tr>`;
  }
}

// 5. Candidate Resume Roster
async function loadCandidatesRoster() {
  const tbody = document.getElementById('admin-candidates-tbody');
  if (!tbody) return;

  try {
    const data = await API.getAdminCandidates();
    tbody.innerHTML = '';

    data.candidates.forEach(c => {
      const tr = document.createElement('tr');
      const badgeClass = c.ats_score >= 80 ? 'badge-emerald' : c.ats_score >= 60 ? 'badge-amber' : 'badge-rose';
      tr.innerHTML = `
        <td><strong>${c.name}</strong></td>
        <td>${c.target_role}</td>
        <td><span class="hero-pill ${badgeClass}" style="margin: 0; padding: 0.2rem 0.6rem;">${c.ats_score}/100</span></td>
        <td>${(c.skills_extracted || []).slice(0, 4).join(', ')}...</td>
        <td>${c.email || 'N/A'}</td>
        <td>${c.account_owner_name || 'Anonymous'}</td>
        <td>${c.created_at ? c.created_at.split(' ')[0] : 'Recent'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
  }
}

// Job Postings Modal
function initJobModal() {
  const postJobBtn = document.getElementById('admin-post-job-btn');
  const modal = document.getElementById('post-job-modal');
  const closeBtn = document.getElementById('post-job-close-btn');
  const form = document.getElementById('post-job-form');

  if (postJobBtn && modal) {
    postJobBtn.onclick = () => modal.classList.add('active');
  }

  if (closeBtn && modal) {
    closeBtn.onclick = () => modal.classList.remove('active');
  }

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const payload = {
        title: fd.get('title'),
        company: fd.get('company'),
        location: fd.get('location'),
        experience_level: fd.get('experience_level'),
        salary_range: fd.get('salary_range'),
        required_skills: fd.get('required_skills'),
        preferred_skills: fd.get('preferred_skills'),
        description: fd.get('description')
      };

      try {
        await API.addAdminJob(payload);
        showToast('Job opening successfully published!', 'success');
        modal.classList.remove('active');
        form.reset();
        loadOverviewMetrics();
      } catch (err) {
        showToast(err.message, 'error');
      }
    };
  }
}

function initAdminTheme() {
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (!themeBtn) return;
  themeBtn.onclick = () => {
    const isLight = document.body.classList.toggle('light-theme');
    themeBtn.textContent = isLight ? '🌙' : '☀️';
  };
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
