import os
import io
import json
import re
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory, redirect
from flask_cors import CORS
from pypdf import PdfReader
import docx

from .database import (
    init_db, register_user, authenticate_user, get_user_by_token, delete_session,
    log_activity, get_activity_logs, get_all_users, toggle_user_status,
    save_candidate_analysis, get_all_candidates, get_candidate_by_id, get_user_resumes,
    get_all_jobs, add_job, delete_job, save_application, get_admin_metrics
)
from .analyzer import ResumeAnalyzer, POWER_VERBS
from .gap_analyzer import SkillGapAnalyzer, ROLE_BENCHMARKS
from .job_matcher import JobMatcher, rank_candidates_for_job
from .pdf_generator import generate_ats_resume_pdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_MODULE_DIR = os.path.join(BASE_DIR, 'user_module')
ADMIN_MODULE_DIR = os.path.join(BASE_DIR, 'admin_module')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Initialize database schema and seeds on startup
init_db()

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()

def get_current_user():
    """Extracts and verifies user from Authorization header or query param."""
    auth_header = request.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1].strip()
    elif 'X-Auth-Token' in request.headers:
        token = request.headers['X-Auth-Token'].strip()
    elif 'token' in request.args:
        token = request.args['token'].strip()

    if not token:
        return None
    return get_user_by_token(token)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "error": "Authentication required. Please sign in to access this feature.",
                "code": "AUTH_REQUIRED"
            }), 401
        return f(*args, user=user, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "error": "Authentication required. Please sign in as an Administrator.",
                "code": "AUTH_REQUIRED"
            }), 401
        if user['role'] != 'admin':
            # Log unauthorized admin attempt
            log_activity(
                user_id=user['id'],
                user_name=user['name'],
                user_email=user['email'],
                role=user['role'],
                action='UNAUTHORIZED_ACCESS_BLOCKED',
                details=f"Forbidden attempt to access admin endpoint: {request.path}",
                ip_address=get_client_ip()
            )
            return jsonify({
                "error": "Access denied. Administrator privileges required.",
                "code": "FORBIDDEN"
            }), 403
        return f(*args, user=user, **kwargs)
    return decorated_function

def extract_text_from_file(file_storage):
    """Safely extracts text from uploaded PDF, DOCX, or text files."""
    filename = file_storage.filename.lower()
    file_bytes = file_storage.read()
    
    if filename.endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
            
    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return text.strip()
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
            
    else:
        try:
            return file_bytes.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            return f"Error reading text: {str(e)}"

# =========================================================================
# Dual-Module Routing: Separate User & Admin Applications
# =========================================================================

@app.route('/')
def serve_index():
    portal_file = os.path.join(BASE_DIR, 'portal.html')
    if os.path.exists(portal_file):
        return send_file(portal_file)
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/portal')
def serve_portal():
    portal_file = os.path.join(BASE_DIR, 'portal.html')
    if os.path.exists(portal_file):
        return send_file(portal_file)
    return redirect('/user/')

# --- User Module Endpoints ---
@app.route('/user')
def user_root():
    return redirect('/user/')

@app.route('/user/')
def serve_user_index():
    return send_from_directory(USER_MODULE_DIR, 'index.html')

@app.route('/user/login')
def serve_user_login():
    return send_from_directory(USER_MODULE_DIR, 'login.html')

@app.route('/user/<path:filename>')
def serve_user_static(filename):
    if filename == 'login':
        return send_from_directory(USER_MODULE_DIR, 'login.html')
    target = os.path.join(USER_MODULE_DIR, filename)
    if os.path.isfile(target):
        return send_from_directory(USER_MODULE_DIR, filename)
    return send_from_directory(USER_MODULE_DIR, 'index.html')

@app.route('/user_module/<path:filename>')
def serve_user_module_direct(filename):
    return send_from_directory(USER_MODULE_DIR, filename)

# --- Admin Module Endpoints ---
@app.route('/admin')
def admin_root():
    return redirect('/admin/')

@app.route('/admin/')
def serve_admin_index():
    return send_from_directory(ADMIN_MODULE_DIR, 'index.html')

@app.route('/admin/login')
def serve_admin_login():
    return send_from_directory(ADMIN_MODULE_DIR, 'login.html')

@app.route('/admin/<path:filename>')
def serve_admin_static(filename):
    if filename == 'login':
        return send_from_directory(ADMIN_MODULE_DIR, 'login.html')
    target = os.path.join(ADMIN_MODULE_DIR, filename)
    if os.path.isfile(target):
        return send_from_directory(ADMIN_MODULE_DIR, filename)
    return send_from_directory(ADMIN_MODULE_DIR, 'index.html')

@app.route('/admin_module/<path:filename>')
def serve_admin_module_direct(filename):
    return send_from_directory(ADMIN_MODULE_DIR, filename)

# Fallback for root frontend assets
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    portal_file = os.path.join(BASE_DIR, 'portal.html')
    if os.path.exists(portal_file):
        return send_file(portal_file)
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "TalentLens AI Resume Analyzer",
        "version": "2.1.0",
        "security": "Enforced (Role-Based Access Control + Live Audit Stream)"
    })

# =========================================================================
# Authentication Endpoints
# =========================================================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    target_role = data.get('target_role', 'Software Engineer')

    if not name or not email or not password:
        return jsonify({"error": "Full Name, Email, and Password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    ip = get_client_ip()
    user, err = register_user(name, email, password, role='user', target_role=target_role, ip_address=ip)
    if err:
        return jsonify({"error": err}), 400

    # Auto-login after registration
    auth_res, login_err = authenticate_user(email, password, ip_address=ip, user_agent=request.user_agent.string)
    if login_err:
        return jsonify({"success": True, "message": "Registered successfully. Please log in."})

    return jsonify({
        "success": True,
        "token": auth_res['token'],
        "user": auth_res['user'],
        "message": f"Welcome, {name}! Your student account is ready."
    })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "Email and Password are required."}), 400

    ip = get_client_ip()
    ua = request.user_agent.string
    auth_res, err = authenticate_user(email, password, ip_address=ip, user_agent=ua)
    if err:
        return jsonify({"error": err}), 401

    return jsonify({
        "success": True,
        "token": auth_res['token'],
        "user": auth_res['user'],
        "message": f"Welcome back, {auth_res['user']['name']}!"
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    user = get_current_user()
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1].strip() if auth_header.startswith('Bearer ') else None
    if token:
        delete_session(token, user=user, ip_address=get_client_ip())
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def api_me(user):
    return jsonify({"authenticated": True, "user": user})

# =========================================================================
# Core Resume Analysis (Protected)
# =========================================================================

@app.route('/api/analyze-resume', methods=['POST'])
@login_required
def analyze_resume(user):
    raw_text = ""
    file_name = "pasted_resume.txt"
    target_role = user.get('target_role', 'Software Engineer')
    
    if request.content_type and 'multipart/form-data' in request.content_type:
        if 'file' in request.files:
            uploaded_file = request.files['file']
            file_name = uploaded_file.filename
            raw_text = extract_text_from_file(uploaded_file)
        elif 'resume_text' in request.form:
            raw_text = request.form['resume_text']
        target_role = request.form.get('target_role', target_role)
    else:
        data = request.get_json(silent=True) or {}
        raw_text = data.get('resume_text', '')
        file_name = data.get('file_name', 'resume_input.txt')
        target_role = data.get('target_role', target_role)

    if not raw_text or len(raw_text.strip()) < 30:
        return jsonify({
            "error": "The resume text is empty or too short. Please upload a valid resume file or paste the content."
        }), 400

    # 1. Run core NLP Resume Analysis
    analyzer = ResumeAnalyzer(raw_text, file_name=file_name)
    ats_results = analyzer.compute_ats_score()

    # 2. Run Skill Gap Analysis & 4-Week Roadmap
    skills_flat = ats_results['skills']['flat']
    skills_categorized = ats_results['skills']['categorized']
    gap_analyzer = SkillGapAnalyzer(skills_flat, skills_categorized, target_role=target_role)
    gap_results = gap_analyzer.analyze_gaps()

    # 3. Match against active job postings
    job_matcher = JobMatcher(skills_flat, candidate_ats_score=ats_results['overall_ats_score'])
    matched_jobs = job_matcher.match_jobs()

    # 4. Save to Database linked to current user
    candidate_record = {
        'name': ats_results['contacts']['name'] or user['name'],
        'email': ats_results['contacts']['email'] or user['email'],
        'phone': ats_results['contacts']['phone'],
        'target_role': gap_results['target_role'],
        'ats_score': ats_results['overall_ats_score'],
        'impact_score': ats_results['impact_score'],
        'brevity_score': ats_results['brevity_score'],
        'structure_score': ats_results['structure_score'],
        'skills_extracted': skills_flat,
        'missing_skills': gap_results['missing_core_skills'] + gap_results['missing_recommended_skills'],
        'skill_gap_analysis': gap_results,
        'recommendations': ats_results['improvements'],
        'resume_text': raw_text,
        'file_name': file_name
    }
    candidate_id = save_candidate_analysis(candidate_record, user_id=user['id'])

    # 5. Log Activity for Admin Audit
    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='RESUME_ANALYZED',
        details=f"Analyzed '{file_name}' for role '{gap_results['target_role']}'. ATS Score: {ats_results['overall_ats_score']}/100. Extracted {len(skills_flat)} skills.",
        ip_address=get_client_ip()
    )

    response_payload = {
        "candidate_id": candidate_id,
        "summary": {
            "name": candidate_record['name'],
            "target_role": gap_results['target_role'],
            "overall_ats_score": ats_results['overall_ats_score'],
            "verdict": gap_results['readiness_verdict']
        },
        "ats_breakdown": {
            "overall": ats_results['overall_ats_score'],
            "structure": ats_results['structure_score'],
            "skills": ats_results['skills_score'],
            "impact": ats_results['impact_score'],
            "brevity": ats_results['brevity_score']
        },
        "contacts": ats_results['contacts'],
        "sections_detected": ats_results['sections'],
        "skills": ats_results['skills'],
        "impact_analysis": ats_results['impact'],
        "brevity_analysis": ats_results['brevity'],
        "strengths": ats_results['strengths'],
        "improvements": ats_results['improvements'],
        "skill_gap_analysis": gap_results,
        "matched_jobs": matched_jobs,
        "meta": {
            "file_name": file_name,
            "word_count": ats_results['brevity']['word_count']
        }
    }

    return jsonify(response_payload)

@app.route('/api/enhance-bullet', methods=['POST'])
@login_required
def enhance_bullet(user):
    data = request.get_json(silent=True) or {}
    bullet = data.get('bullet', '').strip()
    role = data.get('role', 'Software Engineer')

    if not bullet:
        return jsonify({"error": "Please provide a resume bullet point to optimize."}), 400

    clean_bullet = re.sub(r'^[•\-\*\s]+', '', bullet).strip()
    alternatives = [
        {
            "tag": "High Impact & Scalability ⚡",
            "text": f"Architected high-throughput components for {clean_bullet.lower() if not clean_bullet.startswith(('Architected', 'Spearheaded')) else clean_bullet}, optimizing latency by 35% and supporting 10,000+ daily active transactions."
        },
        {
            "tag": "Engineering Leadership & Automation 🚀",
            "text": f"Spearheaded end-to-end design and automated testing for {clean_bullet.lower() if not clean_bullet.startswith('Spearheaded') else clean_bullet}, reducing operational overhead by 40% while ensuring 99.9% uptime."
        },
        {
            "tag": "Performance & Business Growth 📈",
            "text": f"Engineered robust, responsive features to {clean_bullet.lower()}, boosting end-user engagement metrics by 28% and slashing page load times by 450ms across devices."
        }
    ]

    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='BULLET_ENHANCED',
        details=f"Enhanced bullet point: '{bullet[:60]}...'",
        ip_address=get_client_ip()
    )

    return jsonify({
        "original": bullet,
        "alternatives": alternatives
    })

@app.route('/api/jobs', methods=['GET'])
def get_jobs_list():
    jobs = get_all_jobs()
    return jsonify({"jobs": jobs, "total": len(jobs)})

@app.route('/api/jobs/apply', methods=['POST'])
@login_required
def apply_for_job(user):
    data = request.get_json(silent=True) or {}
    candidate_id = data.get('candidate_id')
    job_id = data.get('job_id')
    match_score = data.get('match_score', 80)

    if not candidate_id or not job_id:
        return jsonify({"error": "Missing candidate_id or job_id"}), 400

    app_id = save_application(candidate_id, job_id, match_score, user_id=user['id'])
    
    # Fetch job title for log
    jobs = get_all_jobs()
    job_obj = next((j for j in jobs if j['id'] == int(job_id)), None)
    job_desc = f"{job_obj['title']} @ {job_obj['company']}" if job_obj else f"Job #{job_id}"

    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='JOB_APPLIED',
        details=f"Applied to '{job_desc}' (Match Score: {match_score}%)",
        ip_address=get_client_ip()
    )

    return jsonify({
        "success": True,
        "application_id": app_id,
        "message": "Application submitted successfully! Recruiter notified."
    })

@app.route('/api/download-ats-pdf', methods=['POST'])
@login_required
def download_ats_pdf(user):
    data = request.get_json(silent=True) or {}
    pdf_bytes = generate_ats_resume_pdf(data)
    
    candidate_name = data.get('name', user['name']).replace(' ', '_')
    filename = f"{candidate_name}_ATS_Optimized_Resume.pdf"
    
    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='PDF_DOWNLOADED',
        details=f"Downloaded ATS-optimized resume PDF for '{candidate_name}'",
        ip_address=get_client_ip()
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/user/my-resumes', methods=['GET'])
@login_required
def get_my_resumes(user):
    resumes = get_user_resumes(user['id'])
    return jsonify({"resumes": resumes, "total": len(resumes)})

# =========================================================================
# Admin & Recruiter Endpoints (Admin Privileges Enforced)
# =========================================================================

@app.route('/api/admin/metrics', methods=['GET'])
@admin_required
def admin_metrics(user):
    metrics = get_admin_metrics()
    return jsonify(metrics)

@app.route('/api/admin/candidates', methods=['GET'])
@admin_required
def admin_candidates(user):
    candidates = get_all_candidates()
    return jsonify({"candidates": candidates, "total": len(candidates)})

@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def admin_logs(user):
    """Admin endpoint to see EVERYTHING: who is logging in, who is using what, and when."""
    limit = int(request.args.get('limit', 150))
    logs = get_activity_logs(limit=limit)
    return jsonify({"logs": logs, "total": len(logs)})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_users_list(user):
    """Admin endpoint to manage all registered users."""
    users = get_all_users()
    return jsonify({"users": users, "total": len(users)})

@app.route('/api/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def admin_toggle_user(user, user_id):
    if user_id == user['id']:
        return jsonify({"error": "You cannot suspend your own administrator account."}), 400
    new_status = toggle_user_status(user_id)
    if not new_status:
        return jsonify({"error": "User not found."}), 404

    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='USER_STATUS_CHANGED',
        details=f"Admin changed status of User ID #{user_id} to '{new_status}'",
        ip_address=get_client_ip()
    )
    return jsonify({"success": True, "new_status": new_status})

@app.route('/api/admin/jobs', methods=['POST'])
@admin_required
def admin_add_job(user):
    data = request.get_json(silent=True) or {}
    if not data.get('title') or not data.get('company'):
        return jsonify({"error": "Title and Company are required"}), 400
    
    if isinstance(data.get('required_skills'), str):
        data['required_skills'] = [s.strip() for s in data['required_skills'].split(',') if s.strip()]
    if isinstance(data.get('preferred_skills'), str):
        data['preferred_skills'] = [s.strip() for s in data['preferred_skills'].split(',') if s.strip()]

    job_id = add_job(data)
    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='JOB_POSTED',
        details=f"Admin created job opening '{data['title']} @ {data['company']}'",
        ip_address=get_client_ip()
    )
    return jsonify({"success": True, "job_id": job_id, "message": "Job added successfully"})

@app.route('/api/admin/jobs/<int:job_id>', methods=['DELETE'])
@admin_required
def admin_delete_job(user, job_id):
    delete_job(job_id)
    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='JOB_DELETED',
        details=f"Admin deleted job opening ID #{job_id}",
        ip_address=get_client_ip()
    )
    return jsonify({"success": True, "message": f"Job {job_id} deleted successfully"})

@app.route('/api/admin/rank/<int:job_id>', methods=['GET'])
@admin_required
def admin_rank_candidates(user, job_id):
    ranked = rank_candidates_for_job(job_id)
    return jsonify({"ranked_candidates": ranked, "total": len(ranked)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"🚀 TalentLens AI Secure Server booting at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
