import os
import glob
from .database import init_db, save_candidate_analysis, get_db
from .analyzer import ResumeAnalyzer
from .gap_analyzer import SkillGapAnalyzer

def seed_sample_candidates():
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM candidates")
    count = cursor.fetchone()['count']
    conn.close()

    if count > 0:
        return

    sample_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_resumes')
    sample_files = [
        ("data_science_intern.txt", "Data Scientist / AI Engineer"),
        ("backend_engineer_fresher.txt", "Backend Engineer")
    ]

    for fname, target_role in sample_files:
        fpath = os.path.join(sample_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            analyzer = ResumeAnalyzer(text, file_name=fname)
            ats = analyzer.compute_ats_score()
            gap = SkillGapAnalyzer(
                ats['skills']['flat'], 
                ats['skills']['categorized'], 
                target_role=target_role
            ).analyze_gaps()

            data = {
                'name': ats['contacts']['name'],
                'email': ats['contacts']['email'],
                'phone': ats['contacts']['phone'],
                'target_role': target_role,
                'ats_score': ats['overall_ats_score'],
                'impact_score': ats['impact_score'],
                'brevity_score': ats['brevity_score'],
                'structure_score': ats['structure_score'],
                'skills_extracted': ats['skills']['flat'],
                'missing_skills': gap['missing_core_skills'] + gap['missing_recommended_skills'],
                'skill_gap_analysis': gap,
                'recommendations': ats['improvements'],
                'resume_text': text,
                'file_name': fname
            }
            save_candidate_analysis(data)
            print(f"Seeded candidate: {data['name']} ({target_role}) - ATS: {data['ats_score']}")

if __name__ == '__main__':
    seed_sample_candidates()
