import json
from .database import get_all_jobs, get_all_candidates

class JobMatcher:
    def __init__(self, candidate_skills_flat, candidate_ats_score=75):
        self.candidate_skills = [s.strip().lower() for s in candidate_skills_flat]
        self.candidate_ats = candidate_ats_score

    def match_jobs(self):
        jobs = get_all_jobs()
        matched_jobs = []

        for job in jobs:
            required = job.get('required_skills', [])
            preferred = job.get('preferred_skills', [])

            matched_req = []
            missing_req = []
            for req in required:
                if any(req.lower() in cs or cs in req.lower() for cs in self.candidate_skills):
                    matched_req.append(req)
                else:
                    missing_req.append(req)

            matched_pref = []
            missing_pref = []
            for pref in preferred:
                if any(pref.lower() in cs or cs in pref.lower() for cs in self.candidate_skills):
                    matched_pref.append(pref)
                else:
                    missing_pref.append(pref)

            # Weight required skills 75%, preferred skills 25%
            req_ratio = len(matched_req) / len(required) if required else 1.0
            pref_ratio = len(matched_pref) / len(preferred) if preferred else 0.5
            raw_match = (req_ratio * 75) + (pref_ratio * 25)

            # Small bonus for high ATS score
            ats_bonus = (self.candidate_ats - 60) * 0.1 if self.candidate_ats > 60 else 0
            final_match = max(min(int(round(raw_match + ats_bonus)), 98), 28)

            fit_level = "Exceptional Match 🌟" if final_match >= 85 else \
                        "Strong Fit 🎯" if final_match >= 70 else \
                        "Moderate Match ⚖️" if final_match >= 50 else \
                        "Skill Gap Notice ⚠️"

            fit_badge = "badge-emerald" if final_match >= 85 else \
                        "badge-cyan" if final_match >= 70 else \
                        "badge-amber" if final_match >= 50 else \
                        "badge-rose"

            matched_jobs.append({
                "id": job['id'],
                "title": job['title'],
                "company": job['company'],
                "location": job['location'],
                "type": job['type'],
                "experience_level": job['experience_level'],
                "salary_range": job['salary_range'],
                "description": job['description'],
                "apply_url": job['apply_url'],
                "match_score": final_match,
                "fit_level": fit_level,
                "fit_badge": fit_badge,
                "matched_required": matched_req,
                "missing_required": missing_req,
                "matched_preferred": matched_pref,
                "missing_preferred": missing_pref,
                "overlap_count": len(matched_req) + len(matched_pref)
            })

        # Sort descending by match score
        matched_jobs.sort(key=lambda j: j['match_score'], reverse=True)
        return matched_jobs

def rank_candidates_for_job(job_id):
    jobs = get_all_jobs()
    target_job = next((j for j in jobs if j['id'] == int(job_id)), None)
    if not target_job:
        return []

    candidates = get_all_candidates(limit=100)
    required = target_job.get('required_skills', [])
    preferred = target_job.get('preferred_skills', [])

    ranked_results = []
    for cand in candidates:
        cand_skills = [s.lower() for s in cand.get('skills_extracted', [])]
        
        matched_req = [req for req in required if any(req.lower() in cs or cs in req.lower() for cs in cand_skills)]
        matched_pref = [pref for pref in preferred if any(pref.lower() in cs or cs in pref.lower() for cs in cand_skills)]
        
        req_ratio = len(matched_req) / len(required) if required else 1.0
        pref_ratio = len(matched_pref) / len(preferred) if preferred else 0.5
        match_score = int(round((req_ratio * 75) + (pref_ratio * 25)))

        ranked_results.append({
            "candidate_id": cand['id'],
            "name": cand['name'],
            "email": cand['email'],
            "phone": cand['phone'],
            "target_role": cand['target_role'],
            "ats_score": cand['ats_score'],
            "job_match_score": match_score,
            "matched_skills_count": len(matched_req) + len(matched_pref),
            "matched_skills": matched_req + matched_pref,
            "missing_required": [req for req in required if req not in matched_req],
            "created_at": cand['created_at']
        })

    ranked_results.sort(key=lambda c: (c['job_match_score'], c['ats_score']), reverse=True)
    return ranked_results
