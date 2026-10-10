/* ==========================================================================
   TalentLens — Candidate Portal Controller
   Clean, simple, human-crafted logic for resume parsing, radar charts,
   bullet optimization, and job applications.
   ========================================================================== */

let currentAnalysisData = null;
let radarChartInstance = null;
let selectedFile = null;
let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  await initAuth();
  initNavigation();
  initDropzone();
  initInputTabs();
  initBulletOptimizer();

  // Initialize Radar Chart canvas
  if (document.getElementById('skill-radar-canvas') && typeof RadarChart !== 'undefined') {
    radarChartInstance = new RadarChart('skill-radar-canvas');
  }

  // Hook analyze button
  const analyzeBtn = document.getElementById('analyze-resume-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', handleResumeAnalysis);
  }
});

/* ==========================================================================
   Theme & Appearance
   ========================================================================== */
function initTheme() {
  const themeBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('talentlens_theme');

  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    if (themeBtn) themeBtn.textContent = '🌙';
  } else {
    document.body.classList.remove('light-theme');
    if (themeBtn) themeBtn.textContent = '☀️';
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      themeBtn.textContent = isLight ? '🌙' : '☀️';
      localStorage.setItem('talentlens_theme', isLight ? 'light' : 'dark');
      
      // Re-render radar chart if visible to match theme
      if (currentAnalysisData && radarChartInstance) {
        radarChartInstance.render(currentAnalysisData.skill_gap_analysis.radar_scores);
      }
    });
  }
}

/* ==========================================================================
   Authentication & Session Handling
   ========================================================================== */
async function initAuth() {
  currentUser = await API.getMe();

  if (!currentUser) {
    // If not authenticated, redirect to clean login screen
    window.location.href = '/user/login';
    return;
  }

  // Update nav profile chip
  const userChipName = document.getElementById('user-chip-name');
  const userChipAvatar = document.getElementById('user-chip-avatar');
  if (userChipName) userChipName.textContent = currentUser.name.split(' ')[0];
  if (userChipAvatar) userChipAvatar.textContent = currentUser.name.charAt(0).toUpperCase();

  // Sign out button
  const logoutBtn = document.getElementById('user-logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await API.logout();
      window.location.href = '/user/login';
    });
  }
}

/* ==========================================================================
   Navigation
   ========================================================================== */
function initNavigation() {
  const navAnalyzer = document.getElementById('nav-analyzer');
  const navBullet = document.getElementById('nav-bullet-tool');
  const navJobs = document.getElementById('nav-jobs');

  const navItems = [navAnalyzer, navBullet, navJobs].filter(Boolean);

  function setActive(activeItem) {
    navItems.forEach(n => n.classList.remove('active'));
    if (activeItem) activeItem.classList.add('active');
  }

  if (navAnalyzer) {
    navAnalyzer.addEventListener('click', () => {
      setActive(navAnalyzer);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  if (navBullet) {
    navBullet.addEventListener('click', () => {
      setActive(navBullet);
      const bulletSection = document.getElementById('bullet-tool-section');
      if (bulletSection) {
        bulletSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  if (navJobs) {
    navJobs.addEventListener('click', () => {
      setActive(navJobs);
      const jobSection = document.getElementById('jobs-section');
      if (jobSection) {
        jobSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }
}

/* ==========================================================================
   Input Tabs (Upload / Paste / Sample Resumes)
   ========================================================================== */
function initInputTabs() {
  const tabBtns = document.querySelectorAll('.input-tab-btn');
  const panes = {
    'tab-upload': document.getElementById('tab-upload'),
    'tab-paste': document.getElementById('tab-paste'),
    'tab-presets': document.getElementById('tab-presets')
  };

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const target = btn.dataset.target;
      Object.keys(panes).forEach(k => {
        if (panes[k]) {
          panes[k].style.display = (k === target) ? 'block' : 'none';
        }
      });
    });
  });
}

/* ==========================================================================
   Dropzone File Handling
   ========================================================================== */
function initDropzone() {
  const dropzone = document.getElementById('dropzone-area');
  const fileInput = document.getElementById('resume-file-input');
  const filePreview = document.getElementById('file-preview-pill');
  const fileNameText = document.getElementById('file-name-text');
  const removeFileBtn = document.getElementById('remove-file-btn');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', (e) => {
    if (e.target !== removeFileBtn) {
      fileInput.click();
    }
  });

  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setUploadedFile(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      setUploadedFile(fileInput.files[0]);
    }
  });

  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedFile = null;
      fileInput.value = '';
      if (filePreview) filePreview.style.display = 'none';
    });
  }

  function setUploadedFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      showToast('Please select a valid PDF, DOCX, or TXT file.', 'error');
      return;
    }
    selectedFile = file;
    if (fileNameText) fileNameText.textContent = file.name;
    if (filePreview) filePreview.style.display = 'inline-flex';
    showToast(`Loaded "${file.name}"`, 'success');
  }
}

/* ==========================================================================
   Load Preset Candidate Resumes
   ========================================================================== */
window.loadSampleResume = function(presetKey) {
  if (typeof SAMPLE_RESUMES === 'undefined' || !SAMPLE_RESUMES[presetKey]) {
    showToast('Sample profile not found.', 'error');
    return;
  }

  const sample = SAMPLE_RESUMES[presetKey];
  const textarea = document.getElementById('resume-raw-textarea');
  const roleSelect = document.getElementById('target-role-select');

  if (textarea) textarea.value = sample.text.trim();
  if (roleSelect && sample.role) roleSelect.value = sample.role;

  // Clear any uploaded file to avoid confusion
  selectedFile = null;
  const filePreview = document.getElementById('file-preview-pill');
  if (filePreview) filePreview.style.display = 'none';

  // Switch tab to Paste so user can inspect or edit the text
  const pasteTabBtn = document.querySelector('.input-tab-btn[data-target="tab-paste"]');
  if (pasteTabBtn) pasteTabBtn.click();

  showToast(`Loaded sample resume: ${sample.name}`, 'info');
};

/* ==========================================================================
   Core Resume Analysis
   ========================================================================== */
async function handleResumeAnalysis() {
  const analyzeBtn = document.getElementById('analyze-resume-btn');
  const targetRole = document.getElementById('target-role-select').value;
  const rawTextarea = document.getElementById('resume-raw-textarea');
  const activeTab = document.querySelector('.input-tab-btn.active');
  const isUploadTab = activeTab && activeTab.dataset.target === 'tab-upload';

  let payload;
  let isFormData = false;

  if (isUploadTab && selectedFile) {
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('target_role', targetRole);
    payload = formData;
    isFormData = true;
  } else {
    const text = rawTextarea ? rawTextarea.value.trim() : '';
    if (!text) {
      showToast('Please upload a resume file or paste text to analyze.', 'error');
      return;
    }
    payload = {
      resume_text: text,
      target_role: targetRole,
      file_name: 'candidate_resume.txt'
    };
  }

  // Loading state
  analyzeBtn.disabled = true;
  const originalBtnText = analyzeBtn.innerHTML;
  analyzeBtn.innerHTML = `
    <span class="spinner-inline">⏳</span>
    <span>Analyzing resume...</span>
  `;

  try {
    const results = await API.analyzeResume(payload, isFormData);
    currentAnalysisData = results;
    renderAnalysisResults(results);

    showToast(`Analysis complete! Score: ${results.summary.overall_ats_score}/100`, 'success');

    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
      resultsSection.style.display = 'block';
      resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
  } catch (err) {
    console.error(err);
    showToast(err.message || 'Failed to analyze resume. Please try again.', 'error');
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = originalBtnText;
  }
}

/* ==========================================================================
   Render Results Dashboard
   ========================================================================== */
function renderAnalysisResults(data) {
  // Candidate Profile Summary
  const nameEl = document.getElementById('result-candidate-name');
  if (nameEl) nameEl.textContent = data.summary.name || currentUser?.name || 'Candidate';

  const roleEl = document.getElementById('result-target-role');
  if (roleEl) roleEl.textContent = `Target Role: ${data.summary.target_role}`;

  const verdictEl = document.getElementById('result-readiness-verdict');
  if (verdictEl) {
    verdictEl.textContent = data.summary.verdict.level;
    const score = data.summary.overall_ats_score;
    verdictEl.className = `status-pill ${score >= 75 ? 'ready' : score >= 50 ? 'moderate' : 'needs-work'}`;
  }

  // Contacts
  const contactLinks = document.getElementById('result-contact-links');
  if (contactLinks) {
    contactLinks.innerHTML = '';
    const c = data.contacts || {};
    if (c.email) contactLinks.innerHTML += `<span>✉️ ${c.email}</span>`;
    if (c.phone) contactLinks.innerHTML += `<span>📞 ${c.phone}</span>`;
    if (c.linkedin) contactLinks.innerHTML += `<span>🔗 ${c.linkedin}</span>`;
    if (c.github) contactLinks.innerHTML += `<span>🐙 ${c.github}</span>`;
  }

  // Overall ATS Gauge & Sub-Scores
  const ats = data.ats_breakdown;
  animateNumber('gauge-ats-number', ats.overall);

  const gaugeFill = document.getElementById('gauge-fill-circle');
  if (gaugeFill) {
    const offset = 283 - (ats.overall / 100) * 283;
    gaugeFill.style.strokeDashoffset = offset;
  }

  animateNumber('score-val-structure', ats.structure);
  animateNumber('score-val-skills', ats.skills);
  animateNumber('score-val-impact', ats.impact);
  animateNumber('score-val-brevity', ats.brevity);

  const setProgress = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.style.width = `${Math.min(100, Math.max(0, val))}%`;
  };
  setProgress('progress-fill-structure', ats.structure);
  setProgress('progress-fill-skills', ats.skills);
  setProgress('progress-fill-impact', ats.impact);
  setProgress('progress-fill-brevity', ats.brevity);

  // Strengths
  const strengthsList = document.getElementById('list-strengths');
  if (strengthsList) {
    strengthsList.innerHTML = '';
    (data.strengths || []).forEach(s => {
      strengthsList.innerHTML += `
        <div class="list-item-feedback">
          <span class="icon-strength">✓</span>
          <span>${s}</span>
        </div>
      `;
    });
  }

  // Fixes / Recommendations
  const fixesList = document.getElementById('list-fixes');
  if (fixesList) {
    fixesList.innerHTML = '';
    (data.improvements || []).forEach(f => {
      fixesList.innerHTML += `
        <div class="list-item-feedback">
          <span class="icon-fix">⚠️</span>
          <span>${f}</span>
        </div>
      `;
    });
  }

  // Categorized Skills
  const skillsContainer = document.getElementById('skills-categorized-container');
  if (skillsContainer) {
    skillsContainer.innerHTML = '';
    const categorized = data.skills?.categorized || {};
    for (const [catName, skillList] of Object.entries(categorized)) {
      if (skillList && skillList.length > 0) {
        const pillsHtml = skillList.map(s => `<span class="skill-pill">${s}</span>`).join('');
        skillsContainer.innerHTML += `
          <div class="skill-category-group">
            <div class="skill-category-name">${catName} (${skillList.length})</div>
            <div class="skill-pills-wrap">${pillsHtml}</div>
          </div>
        `;
      }
    }
  }

  // Skill Gaps & Radar
  const gap = data.skill_gap_analysis || {};
  const gapMatchPct = document.getElementById('gap-match-pct');
  if (gapMatchPct) gapMatchPct.textContent = `Match: ${gap.match_percentage || 0}%`;

  const missingCoreWrap = document.getElementById('missing-core-pills');
  if (missingCoreWrap) {
    missingCoreWrap.innerHTML = (gap.missing_core_skills && gap.missing_core_skills.length > 0)
      ? gap.missing_core_skills.map(s => `<span class="skill-pill pill-missing">✕ ${s}</span>`).join('')
      : '<span style="font-size: 0.85rem; color: var(--success-text);">No missing core skills. Full core coverage!</span>';
  }

  const missingRecWrap = document.getElementById('missing-rec-pills');
  if (missingRecWrap) {
    missingRecWrap.innerHTML = (gap.missing_recommended_skills && gap.missing_recommended_skills.length > 0)
      ? gap.missing_recommended_skills.map(s => `<span class="skill-pill pill-recommended">+ ${s}</span>`).join('')
      : '<span style="font-size: 0.85rem; color: var(--text-muted);">Recommended skills satisfied.</span>';
  }

  if (radarChartInstance && gap.radar_scores) {
    radarChartInstance.render(gap.radar_scores);
  }

  // 4-Week Roadmap
  const roadmapContainer = document.getElementById('roadmap-timeline-container');
  if (roadmapContainer) {
    roadmapContainer.innerHTML = '';
    (gap.learning_roadmap || []).forEach(item => {
      roadmapContainer.innerHTML += `
        <div class="roadmap-card">
          <div class="roadmap-week-badge">${item.week}</div>
          <div class="roadmap-focus">${item.focus}</div>
          <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="roadmap-resource-link">
            <span>📚 ${item.resource}</span>
            <span>↗</span>
          </a>
        </div>
      `;
    });
  }

  // Matched Jobs
  renderJobCards(data.matched_jobs || [], data.candidate_id);

  // ATS PDF Download Button
  const downloadPdfBtn = document.getElementById('download-ats-pdf-btn');
  if (downloadPdfBtn) {
    downloadPdfBtn.onclick = () => {
      showToast('Generating ATS-compliant PDF resume...', 'info');
      API.downloadAtsPdf({
        name: data.summary.name,
        target_role: data.summary.target_role,
        contacts: data.contacts,
        skills: data.skills
      });
    };
  }
}

/* ==========================================================================
   Job Cards & 1-Click Apply
   ========================================================================== */
function renderJobCards(jobs, candidateId) {
  const container = document.getElementById('job-cards-container');
  if (!container) return;
  container.innerHTML = '';

  if (jobs.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No direct job matches found at this time.</p>';
    return;
  }

  jobs.forEach(job => {
    const card = document.createElement('div');
    card.className = 'job-card';
    card.innerHTML = `
      <div>
        <div class="job-card-header">
          <div>
            <h4 class="job-title">${job.title}</h4>
            <div class="job-company">${job.company}</div>
          </div>
          <span class="job-match-badge">${job.match_score}% Match</span>
        </div>
        <div class="job-meta-row">
          <span>📍 ${job.location}</span>
          <span>💼 ${job.experience_level}</span>
          <span>💰 ${job.salary_range}</span>
        </div>
        <p class="job-desc">${job.description}</p>
      </div>
      <div class="job-card-footer">
        <button type="button" class="btn btn-primary btn-sm btn-block apply-job-btn" data-job-id="${job.id}" data-match="${job.match_score}">
          Apply Now
        </button>
        <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm">
          Details ↗
        </a>
      </div>
    `;

    container.appendChild(card);
  });

  // Attach apply button click handlers
  document.querySelectorAll('.apply-job-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const jobId = btn.dataset.jobId;
      const matchScore = btn.dataset.match;

      btn.disabled = true;
      btn.textContent = 'Applying...';

      try {
        await API.applyJob(candidateId, jobId, matchScore);
        btn.textContent = '✓ Applied';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
        showToast('Application submitted successfully!', 'success');
      } catch (err) {
        btn.disabled = false;
        btn.textContent = 'Apply Now';
        showToast(err.message || 'Application failed', 'error');
      }
    });
  });
}

/* ==========================================================================
   AI Bullet Point Rewriter
   ========================================================================== */
function initBulletOptimizer() {
  const input = document.getElementById('bullet-input-text');
  const btn = document.getElementById('enhance-bullet-btn');
  const wrap = document.getElementById('bullet-alternatives-wrap');

  if (!btn || !input || !wrap) return;

  btn.addEventListener('click', async () => {
    const bullet = input.value.trim();
    if (!bullet) {
      showToast('Please enter a bullet point to rewrite.', 'error');
      return;
    }

    const roleSelect = document.getElementById('target-role-select');
    const role = roleSelect ? roleSelect.value : 'Software Engineer';

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-inline">⏳</span> Rewriting...`;

    try {
      const res = await API.enhanceBullet(bullet, role);
      wrap.innerHTML = '';

      res.alternatives.forEach(alt => {
        const altCard = document.createElement('div');
        altCard.className = 'bullet-alt-card';
        altCard.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
            <div class="bullet-alt-tag">${alt.tag}</div>
            <button type="button" class="bullet-copy-btn">Copy</button>
          </div>
          <div class="bullet-alt-text">${alt.text}</div>
        `;

        const copyBtn = altCard.querySelector('.bullet-copy-btn');
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(alt.text);
          copyBtn.textContent = '✓ Copied';
          setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1800);
          showToast('Copied to clipboard!', 'info');
        });

        wrap.appendChild(altCard);
      });

      showToast('Generated 3 improved bullets.', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to rewrite bullet', 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Rewrite Bullet';
    }
  });
}

/* ==========================================================================
   Helpers: Number Animation & Toast Notifications
   ========================================================================== */
function animateNumber(elementId, targetValue, duration = 800) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const startValue = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(startValue + (targetValue - startValue) * ease);
    el.textContent = current;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = targetValue;
    }
  }

  requestAnimationFrame(update);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}
