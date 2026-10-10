import re
import json

# Comprehensive skill taxonomy categorized for detailed breakdown
SKILL_TAXONOMY = {
    "Languages": [
        "python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "golang", 
        "rust", "ruby", "php", "swift", "kotlin", "dart", "sql", "r", "html", "html5", "css", "css3", "bash", "shell"
    ],
    "Frontend & UI": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte", "redux", 
        "tailwind css", "tailwind", "bootstrap", "material ui", "sass", "webpack", "vite", 
        "responsive design", "graphql", "rest api", "figma", "ui/ux"
    ],
    "Backend & APIs": [
        "node.js", "nodejs", "express", "express.js", "django", "flask", "fastapi", 
        "spring boot", "spring", "asp.net", "nest.js", "restful apis", "microservices", 
        "graphql", "grpc", "websockets", "jwt", "oauth"
    ],
    "Databases & Caching": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "cassandra", 
        "dynamodb", "elasticsearch", "firebase", "supabase", "prisma", "sqlalchemy"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", 
        "kubernetes", "k8s", "ci/cd", "github actions", "jenkins", "terraform", 
        "linux", "nginx", "ansible", "prometheus", "grafana", "git", "github", "gitlab"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "artificial intelligence", "nlp", 
        "natural language processing", "computer vision", "pytorch", "tensorflow", 
        "keras", "scikit-learn", "pandas", "numpy", "opencv", "huggingface", 
        "langchain", "llm", "generative ai", "rag", "transformers", "data analysis", 
        "data visualization", "power bi", "tableau", "bigquery", "spark"
    ],
    "Core CS & Architecture": [
        "data structures", "algorithms", "dsa", "object oriented programming", "oop", 
        "system design", "operating systems", "dbms", "computer networks", "agile", "scrum", "unit testing"
    ],
    "Soft Skills": [
        "problem solving", "leadership", "communication", "team collaboration", 
        "critical thinking", "time management", "adaptability", "mentoring", "ownership"
    ]
}

# Strong action verbs favored by ATS scanners and hiring managers
POWER_VERBS = [
    "accelerated", "achieved", "architected", "automated", "built", "spearheaded",
    "collaborated", "conceived", "constructed", "created", "decreased", "delivered",
    "deployed", "designed", "developed", "devised", "engineered", "enhanced",
    "established", "executed", "expanded", "formulated", "generated", "implemented",
    "improved", "increased", "initiated", "integrated", "launched", "maximized",
    "minimized", "modeled", "modernized", "optimized", "orchestrated", "overhauled",
    "pioneered", "reduced", "refactored", "resolved", "scaled", "streamlined", "transformed"
]

WEAK_VERBS = [
    "helped", "assisted", "worked on", "handled", "participated in", "was responsible for",
    "did", "tried", "supported", "contributed to", "involved in"
]

class ResumeAnalyzer:
    def __init__(self, raw_text, file_name="resume.txt"):
        self.text = raw_text or ""
        self.cleaned_text = self._clean_text(raw_text)
        self.file_name = file_name
        self.lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    def _clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def extract_contact_info(self):
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, self.text)
        
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}'
        phones = re.findall(phone_pattern, self.text)
        # fallback cleaner for phone
        phone_matches = [p.strip() for p in re.findall(r'(\+?\d[\d -]{8,}\d)', self.text) if len(re.sub(r'\D', '', p)) >= 10]
        
        linkedin_pattern = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/([a-zA-Z0-9_-]+)'
        linkedin = re.findall(linkedin_pattern, self.text, re.IGNORECASE)
        
        github_pattern = r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)'
        github = re.findall(github_pattern, self.text, re.IGNORECASE)

        # Name extraction heuristic: First prominent non-email/non-phone heading line
        name = "Candidate"
        for line in self.lines[:5]:
            clean_line = line.strip()
            # If line has no email, no digits, 2 to 4 words, title-case or uppercase
            if not re.search(r'[@\d\/:|]', clean_line) and 2 <= len(clean_line.split()) <= 4:
                if len(clean_line) < 40 and not any(kw in clean_line.lower() for kw in ['resume', 'curriculum', 'vitae', 'profile']):
                    name = clean_line.title()
                    break

        return {
            "name": name,
            "email": emails[0] if emails else "",
            "phone": phone_matches[0] if phone_matches else (phones[0] if phones else ""),
            "linkedin": f"linkedin.com/in/{linkedin[0]}" if linkedin else "",
            "github": f"github.com/{github[0]}" if github else "",
            "portfolio": bool(re.search(r'(portfolio|github\.io|vercel\.app|netlify\.app)', self.text, re.IGNORECASE))
        }

    def extract_skills(self):
        text_lower = self.text.lower()
        extracted_categorized = {}
        all_extracted_flat = []

        for category, skills in SKILL_TAXONOMY.items():
            found_in_category = []
            for skill in skills:
                # Use word boundary or exact match
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, text_lower):
                    formatted_name = skill.title()
                    # Custom capitalization fixes
                    caps = {
                        "Sql": "SQL", "Html": "HTML5", "Html5": "HTML5", "Css": "CSS3", "Css3": "CSS3",
                        "Js": "JavaScript", "Aws": "AWS", "Gcp": "GCP", "Ui/Ux": "UI/UX", "Dsa": "DSA",
                        "Nlp": "NLP", "Llm": "LLM", "Oop": "OOP", "Dbms": "DBMS", "Ci/Cd": "CI/CD",
                        "Rest Api": "REST APIs", "Restful Apis": "RESTful APIs", "Ai": "AI",
                        "React.Js": "React", "Nodejs": "Node.js", "Express.Js": "Express.js",
                        "K8S": "Kubernetes", "Power Bi": "Power BI"
                    }
                    formatted_name = caps.get(formatted_name, formatted_name)
                    if formatted_name not in found_in_category:
                        found_in_category.append(formatted_name)
                        if formatted_name not in all_extracted_flat:
                            all_extracted_flat.append(formatted_name)
            if found_in_category:
                extracted_categorized[category] = found_in_category

        return {
            "categorized": extracted_categorized,
            "flat": all_extracted_flat,
            "total_count": len(all_extracted_flat)
        }

    def detect_sections(self):
        text_lower = self.text.lower()
        sections_found = {
            "Contact Info": False,
            "Education": bool(re.search(r'\b(education|academics|academic background|degree|university|college|b\.?tech|b\.?e|bachelor)\b', text_lower)),
            "Experience / Internships": bool(re.search(r'\b(experience|internship|internships|work experience|employment|work history)\b', text_lower)),
            "Projects": bool(re.search(r'\b(projects|academic projects|key projects|personal projects)\b', text_lower)),
            "Skills": bool(re.search(r'\b(skills|technical skills|technologies|proficiencies|tech stack)\b', text_lower)),
            "Certifications / Awards": bool(re.search(r'\b(certifications|certificates|achievements|awards|publications|hackathons)\b', text_lower)),
            "Summary / Objective": bool(re.search(r'\b(summary|professional summary|profile summary|objective|career objective)\b', text_lower))
        }
        
        contacts = self.extract_contact_info()
        sections_found["Contact Info"] = bool(contacts["email"] or contacts["phone"])
        return sections_found

    def analyze_impact_and_metrics(self):
        text_lower = self.text.lower()
        
        # Detect metrics like: 40%, $5k, 10,000 users, 2x, 50ms, 99.9%
        metric_matches = re.findall(
            r'(\b\d+(\.\d+)?%|\b\d+x\b|\b\d+[kKmMbB]\b|\b\d{2,}\+?\s+(users|clients|requests|downloads|stars|queries|tps|ms|seconds|minutes|hours|days|dollars)|\$\d+)',
            self.text,
            re.IGNORECASE
        )
        metric_count = len(metric_matches)
        
        # Count power verbs
        found_power_verbs = []
        for verb in POWER_VERBS:
            if re.search(r'\b' + verb + r'\b', text_lower):
                found_power_verbs.append(verb)
                
        # Count weak verbs
        found_weak_verbs = []
        for verb in WEAK_VERBS:
            if re.search(r'\b' + verb + r'\b', text_lower):
                found_weak_verbs.append(verb)

        # Calculate impact score (0 to 100)
        # Metric count (up to 40 pts), power verbs (up to 40 pts), penalty for weak verbs (-10 pts)
        metric_score = min(metric_count * 10, 40)
        power_verb_score = min(len(found_power_verbs) * 5, 40)
        weak_penalty = min(len(found_weak_verbs) * 4, 15)
        
        impact_score = max(min(20 + metric_score + power_verb_score - weak_penalty, 100), 15)
        
        return {
            "impact_score": int(impact_score),
            "quantifiable_metrics_count": metric_count,
            "metrics_sample": [m[0] for m in metric_matches[:5]],
            "power_verbs_count": len(found_power_verbs),
            "power_verbs": found_power_verbs[:10],
            "weak_verbs": found_weak_verbs[:5]
        }

    def analyze_brevity_and_formatting(self):
        words = self.cleaned_text.split()
        word_count = len(words)
        bullet_points = [line for line in self.lines if line.strip().startswith(('•', '-', '*', '–')) or re.match(r'^\d+[\.\)]', line.strip())]
        
        # Ideal word count for freshers is between 350 and 650 words
        brevity_score = 100
        if word_count < 250:
            brevity_score -= 30  # Too brief
        elif word_count < 350:
            brevity_score -= 15
        elif word_count > 900:
            brevity_score -= 25  # Too verbose for fresher
        elif word_count > 700:
            brevity_score -= 10
            
        # Bullet point density
        if len(bullet_points) >= 6:
            brevity_score = min(brevity_score + 10, 100)
        elif len(bullet_points) == 0:
            brevity_score -= 20 # Walls of text are ATS nightmares

        return {
            "brevity_score": max(int(brevity_score), 20),
            "word_count": word_count,
            "reading_time_minutes": round(word_count / 200, 1),
            "bullet_point_count": len(bullet_points)
        }

    def compute_ats_score(self):
        sections = self.detect_sections()
        skills = self.extract_skills()
        impact = self.analyze_impact_and_metrics()
        brevity = self.analyze_brevity_and_formatting()
        contacts = self.extract_contact_info()
        
        # Section structure score (out of 100)
        essential_sections = ["Education", "Experience / Internships", "Projects", "Skills"]
        structure_score = 40
        for s in essential_sections:
            if sections[s]:
                structure_score += 15
        if sections["Summary / Objective"]:
            structure_score += 5
        if sections["Certifications / Awards"]:
            structure_score += 5
        structure_score = min(structure_score, 100)

        # Skills score (out of 100)
        # Freshers with 10-18 varied relevant skills score highest
        skill_count = skills["total_count"]
        if skill_count >= 14:
            skills_score = 95
        elif skill_count >= 10:
            skills_score = 85
        elif skill_count >= 6:
            skills_score = 70
        elif skill_count >= 3:
            skills_score = 50
        else:
            skills_score = 30

        # Weighted ATS formula
        overall_ats = (
            structure_score * 0.25 +
            skills_score * 0.35 +
            impact["impact_score"] * 0.25 +
            brevity["brevity_score"] * 0.15
        )
        
        # Critical deductions/bonuses
        if not contacts["email"] or not contacts["phone"]:
            overall_ats -= 12 # Severe ATS failure
        if contacts["linkedin"]:
            overall_ats += 3
        if contacts["github"]:
            overall_ats += 3

        overall_ats = max(min(int(round(overall_ats)), 98), 25)

        # Generate strengths, critical issues, and recommendations
        strengths = []
        improvements = []
        
        if skills_score >= 80:
            strengths.append(f"Impressive technical skill repertoire ({skill_count} detected industry keywords).")
        if impact["quantifiable_metrics_count"] >= 3:
            strengths.append(f"Excellent evidence of impact ({impact['quantifiable_metrics_count']} quantifiable metrics and stats).")
        if structure_score >= 85:
            strengths.append("Standard ATS section headers and hierarchical formatting detected.")
        if contacts["github"]:
            strengths.append("GitHub profile linked for automated portfolio code review.")
            
        if not contacts["email"]:
            improvements.append("CRITICAL: Missing email address in header.")
        if not contacts["phone"]:
            improvements.append("CRITICAL: Missing phone contact in header.")
        if not contacts["github"]:
            improvements.append("Add your GitHub profile URL to showcase open-source work and coding proof.")
        if not contacts["linkedin"]:
            improvements.append("Add a customized LinkedIn profile URL.")
        if impact["quantifiable_metrics_count"] < 2:
            improvements.append("Low quantifiable proof: Include numbers like 'optimized latency by 35%' or 'scaled to 500+ users'.")
        if brevity["word_count"] < 350:
            improvements.append(f"Resume is relatively brief ({brevity['word_count']} words). Elaborate on project architectures.")
        elif brevity["word_count"] > 800:
            improvements.append("Resume is too verbose for a fresher. Aim for a concise, high-impact 1-page layout.")
        if impact["weak_verbs"]:
            improvements.append(f"Replace passive verbs ({', '.join(impact['weak_verbs'][:3])}) with strong power action verbs.")

        return {
            "overall_ats_score": overall_ats,
            "structure_score": structure_score,
            "skills_score": skills_score,
            "impact_score": impact["impact_score"],
            "brevity_score": brevity["brevity_score"],
            "contacts": contacts,
            "sections": sections,
            "skills": skills,
            "impact": impact,
            "brevity": brevity,
            "strengths": strengths,
            "improvements": improvements
        }
