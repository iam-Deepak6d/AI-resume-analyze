#!/usr/bin/env python3
import sys
import os
import subprocess
import webbrowser
import time

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, '.venv')
    venv_python = os.path.join(venv_dir, 'bin', 'python3')
    
    # If not running inside .venv, re-execute with .venv python
    if os.path.exists(venv_python) and sys.executable != venv_python:
        print(f"🔄 Switching to project virtual environment: {venv_python}")
        os.execv(venv_python, [venv_python, __file__] + sys.argv[1:])

    print("=" * 65)
    print("🚀 TALENTLENS AI — RESUME ANALYZER & SKILL GAP ENGINE")
    print("=" * 65)

    # 1. Initialize Database & Seed Sample Resumes
    print("📦 Initializing database & pre-populating sample profiles...")
    from backend.database import init_db
    from backend.seed_data import seed_sample_candidates
    init_db()
    seed_sample_candidates()

    port = int(os.environ.get('PORT', 5050))
    url = f"http://localhost:{port}"

    print(f"\n🌐 Dual-Module System Active on: {url}")
    print("=" * 65)
    print("🎓 CANDIDATE / USER MODULE (Folder: user_module/)")
    print(f"   • Direct URL:  {url}/user/ (or {url}/user/login)")
    print("   • Demo Login:  student@demo.com  |  Password: student123")
    print("   • Sign Out:    Dedicated '🚪 Sign Out' button in top nav")
    print("   • Highlights:  ATS Parser, Skill Radar, 4-Wk Plan, STAR Tool, Jobs")
    print("-" * 65)
    print("🛡️ RECRUITER / ADMIN MODULE (Folder: admin_module/)")
    print(f"   • Direct URL:  {url}/admin/ (or {url}/admin/login)")
    print("   • Demo Login:  admin@talentlens.ai  |  Password: admin123")
    print("   • Sign Out:    Dedicated red '🚪 Admin Sign Out' button in top nav")
    print("   • Highlights:  Live Audit Stream, User Control, AI Candidate Ranker")
    print("-" * 65)
    print(f"🚀 Dual-Module Gateway Portal: {url}/")
    print("=" * 65)

    # Open browser automatically after a brief delay
    def open_browser():
        time.sleep(1.2)
        print(f"🚀 Opening {url} in your default browser...")
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask App
    from backend.app import app
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
