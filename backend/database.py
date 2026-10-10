import sqlite3
import json
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'resume_ai.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(stored_hash, stored_salt, provided_password):
    computed_hash, _ = hash_password(provided_password, stored_salt)
    return secrets.compare_digest(stored_hash, computed_hash)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            target_role TEXT DEFAULT 'Software Engineer',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 2. User Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 3. Activity & Login Audit Logs Table (Admin can track EVERYTHING)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            user_email TEXT,
            role TEXT,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Candidates Resumes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            phone TEXT,
            target_role TEXT,
            ats_score INTEGER,
            impact_score INTEGER,
            brevity_score INTEGER,
            structure_score INTEGER,
            skills_extracted TEXT,
            missing_skills TEXT,
            skill_gap_analysis TEXT,
            recommendations TEXT,
            resume_text TEXT,
            file_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Check if user_id column exists in candidates and applications table (for migrations)
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in columns:
        try:
            cursor.execute("ALTER TABLE candidates ADD COLUMN user_id INTEGER")
        except Exception:
            pass

    cursor.execute("PRAGMA table_info(applications)")
    app_cols = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in app_cols:
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN user_id INTEGER")
        except Exception:
            pass
    
    # 5. Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            type TEXT DEFAULT 'Full-time',
            experience_level TEXT DEFAULT 'Fresher / Entry Level',
            salary_range TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            description TEXT,
            apply_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. Applications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            candidate_id INTEGER,
            job_id INTEGER,
            match_score INTEGER,
            status TEXT DEFAULT 'Submitted',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    ''')
    
    conn.commit()
    seed_default_jobs(conn)
    seed_default_users(conn)
    conn.close()

def seed_default_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        # 1. Admin Account
        admin_hash, admin_salt = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, salt, role, target_role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Super Admin', 'admin@talentlens.ai', admin_hash, admin_salt, 'admin', 'System Administrator', 'active'))
        
        # 2. Student Demo Account
        student_hash, student_salt = hash_password('student123')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, salt, role, target_role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Demo Student', 'student@demo.com', student_hash, student_salt, 'user', 'Full Stack Developer', 'active'))
        
        conn.commit()

        # Seed initial log
        log_activity(
            user_id=1,
            user_name='System',
            user_email='system@talentlens.ai',
            role='system',
            action='SYSTEM_BOOT',
            details='Database initialized with Secure Authentication & Audit System.',
            ip_address='127.0.0.1'
        )

def seed_default_jobs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    if cursor.fetchone()['count'] == 0:
        default_jobs = [
            (
                "Junior Frontend Developer",
                "Stripe Labs",
                "Bengaluru / Hybrid",
                "Full-time",
                "Fresher / Entry-Level (0-1 yr)",
                "₹8 - 14 LPA",
                json.dumps(["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Git", "REST APIs"]),
                json.dumps(["Next.js", "Tailwind CSS", "Redux", "Jest"]),
                "Build modern, accessible financial interfaces. Ideal for fresh graduates with solid React & modern web fundamentals.",
                "https://careers.stripe.com"
            ),
            (
                "Software Development Engineer - Fresher",
                "Microsoft",
                "Hyderabad / Onsite",
                "Full-time",
                "Fresher (2025/2026 Batch)",
                "₹14 - 22 LPA",
                json.dumps(["Data Structures", "Algorithms", "Python", "Java", "C++", "SQL", "OOP"]),
                json.dumps(["Docker", "Azure", "System Design Basics", "Git"]),
                "Join Azure Core Engineering. Work on high-scale distributed systems and cloud microservices.",
                "https://careers.microsoft.com"
            ),
            (
                "Associate Data Scientist / AI Intern",
                "Google Cloud",
                "Bengaluru / Hybrid",
                "Full-time / Internship",
                "College Grad / Fresher",
                "₹12 - 18 LPA",
                json.dumps(["Python", "Pandas", "NumPy", "Machine Learning", "Scikit-Learn", "SQL"]),
                json.dumps(["PyTorch", "TensorFlow", "Generative AI", "NLP", "LLMs", "Tableau"]),
                "Analyze big data, train predictive models, and prototype next-gen Generative AI agent workflows.",
                "https://careers.google.com"
            ),
            (
                "Backend Engineer (Python / Node.js)",
                "Razorpay",
                "Remote / India",
                "Full-time",
                "Fresher / Junior (0-2 yrs)",
                "₹9 - 15 LPA",
                json.dumps(["Python", "Node.js", "REST APIs", "PostgreSQL", "MongoDB", "Git"]),
                json.dumps(["Docker", "Redis", "Kafka", "AWS", "FastAPI"]),
                "Scale payment gateway infrastructure handling 10,000+ TPS. Strong database & concurrency skills desired.",
                "https://razorpay.com/jobs"
            ),
            (
                "Junior DevOps & Cloud Associate",
                "Atlassian",
                "Bengaluru / Remote",
                "Full-time",
                "Fresher / Entry-Level",
                "₹11 - 16 LPA",
                json.dumps(["Linux", "Git", "Docker", "AWS", "Python", "Bash", "CI/CD"]),
                json.dumps(["Kubernetes", "Terraform", "GitHub Actions", "Prometheus"]),
                "Manage cloud infrastructure, deployment pipelines, and system reliability for Jira and Confluence.",
                "https://www.atlassian.com/company/careers"
            ),
            (
                "Associate Product Analyst",
                "Swiggy",
                "Bengaluru / Hybrid",
                "Full-time",
                "Fresher (Any B.Tech/BS)",
                "₹8 - 12 LPA",
                json.dumps(["SQL", "Excel", "Data Analysis", "Python", "Problem Solving", "Metrics Definition"]),
                json.dumps(["PowerBI", "Tableau", "A/B Testing", "Product Sense"]),
                "Drive growth, delivery optimization, and user retention through data-backed product insights.",
                "https://careers.swiggy.com"
            ),
            (
                "Full Stack Developer (MERN)",
                "Zepto Tech",
                "Mumbai / Bengaluru",
                "Full-time",
                "Fresher (0-1 yr)",
                "₹10 - 16 LPA",
                json.dumps(["React", "Node.js", "Express", "MongoDB", "JavaScript", "HTML5", "CSS3"]),
                json.dumps(["TypeScript", "Redis", "AWS", "Socket.io"]),
                "Build ultra-fast 10-minute grocery delivery apps and real-time inventory systems.",
                "https://www.zepto.com/careers"
            )
        ]
        
        cursor.executemany('''
            INSERT INTO jobs (title, company, location, type, experience_level, salary_range, required_skills, preferred_skills, description, apply_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_jobs)
        conn.commit()

# =========================================================================
# Authentication & User Management Helpers
# =========================================================================

def register_user(name, email, password, role='user', target_role='Software Engineer', ip_address='127.0.0.1'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower().strip(),))
    if cursor.fetchone():
        conn.close()
        return None, "An account with this email address already exists."

    pwd_hash, salt = hash_password(password)
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, salt, role, target_role, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name.strip(), email.lower().strip(), pwd_hash, salt, role, target_role, 'active'))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Log registration event
    log_activity(
        user_id=user_id,
        user_name=name,
        user_email=email,
        role=role,
        action='USER_REGISTERED',
        details=f"New {role} account registered. Target role: {target_role}",
        ip_address=ip_address
    )

    return get_user_by_id(user_id), None

def authenticate_user(email, password, ip_address='127.0.0.1', user_agent=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        log_activity(
            user_id=None,
            user_name='Anonymous',
            user_email=email,
            role='guest',
            action='LOGIN_FAILED',
            details=f"Failed login attempt: Email not found ({email})",
            ip_address=ip_address
        )
        return None, "Invalid email or password."

    user = dict(user_row)
    if user['status'] == 'suspended':
        conn.close()
        log_activity(
            user_id=user['id'],
            user_name=user['name'],
            user_email=user['email'],
            role=user['role'],
            action='LOGIN_BLOCKED',
            details="Login blocked: Account is suspended by administrator.",
            ip_address=ip_address
        )
        return None, "This account has been suspended by an administrator."

    if not verify_password(user['password_hash'], user['salt'], password):
        conn.close()
        log_activity(
            user_id=user['id'],
            user_name=user['name'],
            user_email=user['email'],
            role=user['role'],
            action='LOGIN_FAILED',
            details="Failed login attempt: Incorrect password",
            ip_address=ip_address
        )
        return None, "Invalid email or password."

    # Generate session token
    token = secrets.token_hex(32)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO user_sessions (token, user_id, ip_address, user_agent)
        VALUES (?, ?, ?, ?)
    ''', (token, user['id'], ip_address, user_agent[:250]))

    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user['id']))
    conn.commit()
    conn.close()

    # Log successful login
    log_activity(
        user_id=user['id'],
        user_name=user['name'],
        user_email=user['email'],
        role=user['role'],
        action='USER_LOGIN',
        details=f"User logged in successfully (Role: {user['role']})",
        ip_address=ip_address
    )

    clean_user = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'target_role': user['target_role'],
        'status': user['status'],
        'created_at': user['created_at'],
        'last_login': now_str
    }
    return {"token": token, "user": clean_user}, None

def get_user_by_token(token):
    if not token:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.email, u.role, u.target_role, u.status, u.created_at, u.last_login
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ?
    ''', (token,))
    row = cursor.fetchone()
    conn.close()
    if row and row['status'] == 'active':
        return dict(row)
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, role, target_role, status, created_at, last_login 
        FROM users WHERE id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_session(token, user=None, ip_address='127.0.0.1'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    if user:
        log_activity(
            user_id=user['id'],
            user_name=user['name'],
            user_email=user['email'],
            role=user['role'],
            action='USER_LOGOUT',
            details="User signed out",
            ip_address=ip_address
        )
    return True

def log_activity(user_id, user_name, user_email, role, action, details, ip_address='127.0.0.1'):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_logs (user_id, user_name, user_email, role, action, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, user_email, role, action, details, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

def get_activity_logs(limit=100):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, user_name, user_email, role, action, details, ip_address, created_at
        FROM activity_logs
        ORDER BY created_at DESC, id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.email, u.role, u.target_role, u.status, u.created_at, u.last_login,
               (SELECT COUNT(*) FROM candidates c WHERE c.user_id = u.id) as resumes_analyzed,
               (SELECT COUNT(*) FROM applications a WHERE a.user_id = u.id) as jobs_applied
        FROM users u
        ORDER BY u.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_user_status(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    new_status = 'suspended' if row['status'] == 'active' else 'active'
    cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
    # If suspended, kill their sessions
    if new_status == 'suspended':
        cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return new_status

# =========================================================================
# Candidate Resumes & Applications Helpers
# =========================================================================

def save_candidate_analysis(data, user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO candidates (
            user_id, name, email, phone, target_role, ats_score, impact_score, 
            brevity_score, structure_score, skills_extracted, missing_skills, 
            skill_gap_analysis, recommendations, resume_text, file_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('name', 'Anonymous Candidate'),
        data.get('email', ''),
        data.get('phone', ''),
        data.get('target_role', 'Software Engineer'),
        data.get('ats_score', 0),
        data.get('impact_score', 0),
        data.get('brevity_score', 0),
        data.get('structure_score', 0),
        json.dumps(data.get('skills_extracted', [])),
        json.dumps(data.get('missing_skills', [])),
        json.dumps(data.get('skill_gap_analysis', {})),
        json.dumps(data.get('recommendations', [])),
        data.get('resume_text', '')[:10000],
        data.get('file_name', 'resume.txt')
    ))
    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id

def get_candidate_by_id(candidate_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        c = dict(row)
        c['skills_extracted'] = json.loads(c['skills_extracted'] or '[]')
        c['missing_skills'] = json.loads(c['missing_skills'] or '[]')
        c['skill_gap_analysis'] = json.loads(c['skill_gap_analysis'] or '{}')
        c['recommendations'] = json.loads(c['recommendations'] or '[]')
        return c
    return None

def get_all_candidates(limit=50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.name as account_owner_name, u.email as account_owner_email
        FROM candidates c
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    candidates = []
    for row in rows:
        c = dict(row)
        c['skills_extracted'] = json.loads(c['skills_extracted'] or '[]')
        c['missing_skills'] = json.loads(c['missing_skills'] or '[]')
        c['skill_gap_analysis'] = json.loads(c['skill_gap_analysis'] or '{}')
        c['recommendations'] = json.loads(c['recommendations'] or '[]')
        candidates.append(c)
    return candidates

def get_user_resumes(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, target_role, ats_score, created_at, file_name
        FROM candidates WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    jobs = []
    for row in rows:
        j = dict(row)
        j['required_skills'] = json.loads(j['required_skills'] or '[]')
        j['preferred_skills'] = json.loads(j['preferred_skills'] or '[]')
        jobs.append(j)
    return jobs

def add_job(job_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, location, type, experience_level, salary_range, required_skills, preferred_skills, description, apply_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_data.get('title'),
        job_data.get('company'),
        job_data.get('location', 'Remote'),
        job_data.get('type', 'Full-time'),
        job_data.get('experience_level', 'Fresher / Entry Level'),
        job_data.get('salary_range', 'Negotiable'),
        json.dumps(job_data.get('required_skills', [])),
        json.dumps(job_data.get('preferred_skills', [])),
        job_data.get('description', ''),
        job_data.get('apply_url', '#')
    ))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def delete_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True

def save_application(candidate_id, job_id, match_score, user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (user_id, candidate_id, job_id, match_score)
        VALUES (?, ?, ?, ?)
    ''', (user_id, candidate_id, job_id, match_score))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id

def get_admin_metrics():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute("SELECT COUNT(*) as total_candidates FROM candidates")
    total_candidates = cursor.fetchone()['total_candidates']
    
    cursor.execute("SELECT AVG(ats_score) as avg_ats FROM candidates")
    avg_ats_row = cursor.fetchone()['avg_ats']
    avg_ats = round(avg_ats_row, 1) if avg_ats_row else 74.2
    
    cursor.execute("SELECT COUNT(*) as total_jobs FROM jobs")
    total_jobs = cursor.fetchone()['total_jobs']
    
    cursor.execute("SELECT COUNT(*) as total_apps FROM applications")
    total_apps = cursor.fetchone()['total_apps']
    
    cursor.execute("SELECT COUNT(*) as total_logs FROM activity_logs")
    total_logs = cursor.fetchone()['total_logs']
    
    cursor.execute("SELECT skills_extracted, missing_skills FROM candidates")
    rows = cursor.fetchall()
    
    skill_freq = {}
    missing_freq = {}
    for r in rows:
        extracted = json.loads(r['skills_extracted'] or '[]')
        for s in extracted:
            skill_freq[s] = skill_freq.get(s, 0) + 1
        missing = json.loads(r['missing_skills'] or '[]')
        for m in missing:
            missing_freq[m] = missing_freq.get(m, 0) + 1
            
    top_extracted = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:8]
    top_missing = sorted(missing_freq.items(), key=lambda x: x[1], reverse=True)[:8]
    conn.close()
    
    return {
        'total_users': total_users,
        'total_candidates': total_candidates,
        'avg_ats_score': avg_ats,
        'total_jobs_active': total_jobs,
        'total_applications': total_apps,
        'total_logs': total_logs,
        'top_in_demand_skills': top_extracted if top_extracted else [
            ("Python", 18), ("React", 15), ("JavaScript", 14), ("SQL", 12), 
            ("Docker", 9), ("Machine Learning", 8), ("Node.js", 7), ("Git", 16)
        ],
        'top_skill_gaps_fresher': top_missing if top_missing else [
            ("Docker / Containerization", 16),
            ("Cloud (AWS / Azure)", 14),
            ("Unit Testing / CI/CD", 13),
            ("System Design Basics", 11),
            ("TypeScript", 10),
            ("Redis Caching", 9)
        ]
    }
