/* ==========================================================================
   TalentLens AI - API Client Layer with Authentication & Session Management
   ========================================================================== */

const API_BASE = window.location.origin;

const API = {
  getToken() {
    return localStorage.getItem('talentlens_token') || null;
  },

  setSession(token, user) {
    if (token) localStorage.setItem('talentlens_token', token);
    if (user) localStorage.setItem('talentlens_user', JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem('talentlens_token');
    localStorage.removeItem('talentlens_user');
  },

  getCurrentUser() {
    try {
      const u = localStorage.getItem('talentlens_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  getAuthHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  // Auth: Login
  async login(email, password) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Login failed');
    this.setSession(data.token, data.user);
    return data;
  },

  // Auth: Register
  async register(name, email, password, target_role) {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, target_role })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Registration failed');
    if (data.token && data.user) {
      this.setSession(data.token, data.user);
    }
    return data;
  },

  // Auth: Logout
  async logout() {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        headers: { ...this.getAuthHeaders() }
      });
    } catch (e) {
      console.warn('Logout error', e);
    } finally {
      this.clearSession();
    }
  },

  // Auth: Verify current user
  async getMe() {
    const token = this.getToken();
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { ...this.getAuthHeaders() }
      });
      if (!res.ok) {
        this.clearSession();
        return null;
      }
      const data = await res.json();
      this.setSession(token, data.user);
      return data.user;
    } catch {
      return null;
    }
  },

  // Analyze resume via file upload or raw text (Protected)
  async analyzeResume(payload, isFormData = false) {
    const options = {
      method: 'POST',
      headers: { ...this.getAuthHeaders() }
    };
    if (isFormData) {
      options.body = payload;
    } else {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(payload);
    }

    const response = await fetch(`${API_BASE}/api/analyze-resume`, options);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Analysis failed' }));
      if (response.status === 401) {
        throw new Error('Please sign in to analyze your resume.');
      }
      throw new Error(err.error || 'Server error occurred during analysis');
    }
    return await response.json();
  },

  // AI STAR Bullet Point Enhancer (Protected)
  async enhanceBullet(bulletText, role = 'Software Engineer') {
    const response = await fetch(`${API_BASE}/api/enhance-bullet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders()
      },
      body: JSON.stringify({ bullet: bulletText, role })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Failed to enhance bullet' }));
      throw new Error(err.error || 'Failed to enhance bullet point');
    }
    return await response.json();
  },

  // Fetch active jobs
  async getJobs() {
    const response = await fetch(`${API_BASE}/api/jobs`);
    if (!response.ok) throw new Error('Failed to load jobs');
    return await response.json();
  },

  // Apply to job (Protected)
  async applyJob(candidateId, jobId, matchScore) {
    const response = await fetch(`${API_BASE}/api/jobs/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders()
      },
      body: JSON.stringify({ candidate_id: candidateId, job_id: jobId, match_score: matchScore })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Application failed' }));
      throw new Error(err.error || 'Application submission failed');
    }
    return await response.json();
  },

  // Download ATS-compliant PDF (Protected)
  async downloadAtsPdf(candidateData) {
    const response = await fetch(`${API_BASE}/api/download-ats-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders()
      },
      body: JSON.stringify(candidateData)
    });
    if (!response.ok) throw new Error('PDF generation failed');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const name = (candidateData.name || 'Candidate').replace(/\s+/g, '_');
    a.download = `${name}_ATS_Optimized_Resume.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  },

  // Admin Portal Metrics (Admin Only)
  async getAdminMetrics() {
    const response = await fetch(`${API_BASE}/api/admin/metrics`, {
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to load metrics (Admin required)');
    return await response.json();
  },

  // Admin Candidates (Admin Only)
  async getAdminCandidates() {
    const response = await fetch(`${API_BASE}/api/admin/candidates`, {
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to load candidates (Admin required)');
    return await response.json();
  },

  // Admin Audit Logs: Track who is logging in and who is using what!
  async getAdminLogs(limit = 100) {
    const response = await fetch(`${API_BASE}/api/admin/logs?limit=${limit}`, {
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to load activity logs (Admin required)');
    return await response.json();
  },

  // Admin User Management Roster
  async getAdminUsers() {
    const response = await fetch(`${API_BASE}/api/admin/users`, {
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to load users (Admin required)');
    return await response.json();
  },

  // Admin Toggle User Status
  async toggleUserStatus(userId) {
    const response = await fetch(`${API_BASE}/api/admin/users/${userId}/toggle-status`, {
      method: 'POST',
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Failed to update user' }));
      throw new Error(err.error || 'Failed to update user status');
    }
    return await response.json();
  },

  // Admin Add Job Opening
  async addAdminJob(jobData) {
    const response = await fetch(`${API_BASE}/api/admin/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders()
      },
      body: JSON.stringify(jobData)
    });
    if (!response.ok) throw new Error('Failed to create job');
    return await response.json();
  },

  // Admin Delete Job
  async deleteAdminJob(jobId) {
    const response = await fetch(`${API_BASE}/api/admin/jobs/${jobId}`, {
      method: 'DELETE',
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to delete job');
    return await response.json();
  },

  // Admin Rank Candidates for specific job
  async rankCandidatesForJob(jobId) {
    const response = await fetch(`${API_BASE}/api/admin/rank/${jobId}`, {
      headers: { ...this.getAuthHeaders() }
    });
    if (!response.ok) throw new Error('Failed to rank candidates');
    return await response.json();
  }
};
