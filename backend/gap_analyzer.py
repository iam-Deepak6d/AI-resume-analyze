import json

ROLE_BENCHMARKS = {
    "Frontend Developer": {
        "core_skills": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Git", "REST APIs"],
        "recommended_skills": ["Next.js", "Redux", "Tailwind CSS", "Jest", "Webpack", "UI/UX", "Responsive Design"],
        "radar_weights": {"Frontend": 95, "Backend": 40, "Databases": 30, "Cloud & DevOps": 35, "Problem Solving": 75},
        "roadmap": [
            {
                "week": "Week 1: Modern JavaScript & TypeScript Strictness",
                "focus": "Async/Await, Closures, DOM, TypeScript Generics & Interfaces",
                "resource": "TypeScript Handbook & freeCodeCamp TypeScript Course",
                "url": "https://www.typescriptlang.org/docs/"
            },
            {
                "week": "Week 2: Advanced React & State Architecture",
                "focus": "Custom Hooks, Context API vs Redux Toolkit, React Server Components",
                "resource": "Official React Docs (react.dev) & FullStackOpen",
                "url": "https://react.dev/learn"
            },
            {
                "week": "Week 3: Portfolio Capstone Project",
                "focus": "Build a responsive Next.js 14 SaaS dashboard with Tailwind CSS & API caching",
                "resource": "Next.js Official Learn Tutorial",
                "url": "https://nextjs.org/learn"
            },
            {
                "week": "Week 4: Performance, SEO & Testing",
                "focus": "Lighthouse CWV audit, Unit testing with Jest & React Testing Library",
                "resource": "web.dev Performance Guide",
                "url": "https://web.dev/learn/performance"
            }
        ]
    },
    "Backend Engineer": {
        "core_skills": ["Python", "Node.js", "Java", "SQL", "PostgreSQL", "REST APIs", "Git", "OOP"],
        "recommended_skills": ["Docker", "Redis", "FastAPI", "MongoDB", "Microservices", "CI/CD", "AWS"],
        "radar_weights": {"Frontend": 25, "Backend": 95, "Databases": 90, "Cloud & DevOps": 70, "Problem Solving": 85},
        "roadmap": [
            {
                "week": "Week 1: Deep Dive into API Architecture & DB Schema",
                "focus": "Relational DB Normalization, Indexing, ACID transactions in PostgreSQL",
                "resource": "PostgreSQL Tutorial & High-Performance SQL Guide",
                "url": "https://www.postgresqltutorial.com/"
            },
            {
                "week": "Week 2: Caching, Queues & Concurrency",
                "focus": "Redis in-memory caching, Rate limiting, Message Queues (RabbitMQ/Kafka basics)",
                "resource": "Redis University - RU101",
                "url": "https://university.redis.io/"
            },
            {
                "week": "Week 3: Containerization & Cloud Deployment",
                "focus": "Dockerizing backend microservices, Multi-stage builds, Deploying on AWS EC2/ECS",
                "resource": "Docker Docs Getting Started",
                "url": "https://docs.docker.com/get-started/"
            },
            {
                "week": "Week 4: System Design & Security Best Practices",
                "focus": "JWT Auth, OAuth2, API Rate-limiting, SQL Injection prevention, Horizontal Scaling",
                "resource": "System Design Primer by Donne Martin",
                "url": "https://github.com/donnemartin/system-design-primer"
            }
        ]
    },
    "Full Stack Developer": {
        "core_skills": ["JavaScript", "React", "Node.js", "SQL", "HTML5", "CSS3", "Git", "REST APIs"],
        "recommended_skills": ["TypeScript", "MongoDB", "PostgreSQL", "Docker", "Express", "Next.js", "AWS"],
        "radar_weights": {"Frontend": 85, "Backend": 85, "Databases": 80, "Cloud & DevOps": 65, "Problem Solving": 80},
        "roadmap": [
            {
                "week": "Week 1: TypeScript End-to-End Type Safety",
                "focus": "Shared types between Frontend (React) and Backend (Node/Express)",
                "resource": "Full Stack Open - University of Helsinki",
                "url": "https://fullstackopen.com/en/"
            },
            {
                "week": "Week 2: Database Modeling & ORM Mastery",
                "focus": "Prisma ORM or SQLAlchemy, Migrations, Seeders, Real-time WebSockets",
                "resource": "Prisma Official Docs & Quickstart",
                "url": "https://www.prisma.io/docs"
            },
            {
                "week": "Week 3: End-to-End SaaS Project",
                "focus": "Build an AI Job Match portal with Auth, Stripe checkout, and SQLite/PostgreSQL",
                "resource": "freeCodeCamp Full Stack Projects",
                "url": "https://www.freecodecamp.org/"
            },
            {
                "week": "Week 4: CI/CD Pipeline & Automated Tests",
                "focus": "GitHub Actions workflow for linting, testing, and Vercel/Render automatic deploy",
                "resource": "GitHub Actions Documentation",
                "url": "https://docs.github.com/en/actions"
            }
        ]
    },
    "Data Scientist / AI Engineer": {
        "core_skills": ["Python", "SQL", "Pandas", "NumPy", "Machine Learning", "Scikit-Learn", "Data Analysis"],
        "recommended_skills": ["PyTorch", "TensorFlow", "Deep Learning", "NLP", "Generative AI", "Tableau", "Power BI", "Docker"],
        "radar_weights": {"Frontend": 20, "Backend": 60, "Databases": 75, "Cloud & DevOps": 45, "Problem Solving": 95},
        "roadmap": [
            {
                "week": "Week 1: Advanced Data Wrangling & Feature Engineering",
                "focus": "Pandas vectorization, Outlier handling, Imbalanced datasets, Matplotlib/Seaborn",
                "resource": "Kaggle Feature Engineering & Micro-courses",
                "url": "https://www.kaggle.com/learn"
            },
            {
                "week": "Week 2: Supervised & Unsupervised ML Pipeline",
                "focus": "Cross-validation, Hyperparameter tuning (Optuna), Ensemble models (XGBoost, LightGBM)",
                "resource": "Scikit-Learn User Guide & StatQuest with Josh Starmer",
                "url": "https://scikit-learn.org/stable/user_guide.html"
            },
            {
                "week": "Week 3: Deep Learning & Generative AI Prototyping",
                "focus": "PyTorch tensors, Transformers architecture, Fine-tuning HuggingFace models, RAG pipelines",
                "resource": "DeepLearning.AI Hugging Face & LLM courses",
                "url": "https://www.deeplearning.ai/"
            },
            {
                "week": "Week 4: Model Deployment & Portfolio Showcase",
                "focus": "Packaging ML model as FastAPI REST API, Deploying Streamlit/Gradio app on HuggingFace Spaces",
                "resource": "FastAPI Machine Learning Deployment Guide",
                "url": "https://fastapi.tiangolo.com/"
            }
        ]
    },
    "DevOps & Cloud Engineer": {
        "core_skills": ["Linux", "Git", "Docker", "AWS", "Bash", "CI/CD", "Python"],
        "recommended_skills": ["Kubernetes", "Terraform", "GitHub Actions", "Nginx", "Prometheus", "Grafana", "Ansible"],
        "radar_weights": {"Frontend": 15, "Backend": 65, "Databases": 50, "Cloud & DevOps": 95, "Problem Solving": 75},
        "roadmap": [
            {
                "week": "Week 1: Linux Administration & Shell Scripting",
                "focus": "File permissions, Systemd services, Process monitoring, Cron jobs, Bash automation",
                "resource": "Linux Journey Tutorial",
                "url": "https://linuxjourney.com/"
            },
            {
                "week": "Week 2: Containerization & Docker Networking",
                "focus": "Dockerfiles optimization, Multi-container Compose, Volume management, Container security",
                "resource": "Docker Official Deep Dive",
                "url": "https://docs.docker.com/"
            },
            {
                "week": "Week 3: Cloud Infrastructure (AWS / Azure) & Terraform",
                "focus": "VPC, EC2, S3, IAM policies, Infrastructure as Code using Terraform HCL",
                "resource": "HashiCorp Learn Terraform",
                "url": "https://developer.hashicorp.com/terraform/tutorials"
            },
            {
                "week": "Week 4: Kubernetes Orchestration & Monitoring",
                "focus": "Pods, Deployments, Services, Ingress, Prometheus metrics, Grafana dashboards",
                "resource": "Kubernetes the Hard Way by Kelsey Hightower",
                "url": "https://kubernetes.io/docs/tutorials/"
            }
        ]
    }
}

class SkillGapAnalyzer:
    def __init__(self, candidate_skills_flat, candidate_skills_categorized, target_role="Software Engineer"):
        self.candidate_skills = [s.strip().lower() for s in candidate_skills_flat]
        self.candidate_skills_raw = candidate_skills_flat
        self.categorized = candidate_skills_categorized
        self.target_role = target_role if target_role in ROLE_BENCHMARKS else self._auto_detect_role()

    def _auto_detect_role(self):
        # Best guess target role based on existing skills
        scores = {}
        for role, data in ROLE_BENCHMARKS.items():
            core_reqs = [s.lower() for s in data["core_skills"]]
            matches = sum(1 for s in self.candidate_skills if any(req in s or s in req for req in core_reqs))
            scores[role] = matches
            
        best_role = max(scores.items(), key=lambda x: x[1])[0] if scores else "Full Stack Developer"
        return best_role

    def analyze_gaps(self):
        benchmark = ROLE_BENCHMARKS.get(self.target_role, ROLE_BENCHMARKS["Full Stack Developer"])
        core_skills = benchmark["core_skills"]
        recommended_skills = benchmark["recommended_skills"]

        matched_core = []
        missing_core = []
        for skill in core_skills:
            if any(skill.lower() in cs or cs in skill.lower() for cs in self.candidate_skills):
                matched_core.append(skill)
            else:
                missing_core.append(skill)

        matched_recommended = []
        missing_recommended = []
        for skill in recommended_skills:
            if any(skill.lower() in cs or cs in skill.lower() for cs in self.candidate_skills):
                matched_recommended.append(skill)
            else:
                missing_recommended.append(skill)

        total_tracked = len(core_skills) + len(recommended_skills)
        total_matched = len(matched_core) + len(matched_recommended)
        match_percentage = int(round((total_matched / total_tracked) * 100)) if total_tracked > 0 else 0

        # Radar score calculation (Frontend, Backend, Databases, Cloud & DevOps, Problem Solving)
        radar_scores = self._calculate_radar_scores()

        return {
            "target_role": self.target_role,
            "match_percentage": match_percentage,
            "matched_core_skills": matched_core,
            "missing_core_skills": missing_core,
            "matched_recommended_skills": matched_recommended,
            "missing_recommended_skills": missing_recommended,
            "radar_scores": radar_scores,
            "learning_roadmap": benchmark["roadmap"],
            "total_missing_count": len(missing_core) + len(missing_recommended),
            "readiness_verdict": self._get_readiness_verdict(match_percentage)
        }

    def _calculate_radar_scores(self):
        # Scale each axis from 20 to 95 based on candidate extracted skills in each category
        def count_cat(cat_name):
            skills = self.categorized.get(cat_name, [])
            return len(skills)

        fe_count = count_cat("Frontend & UI")
        be_count = count_cat("Backend & APIs")
        db_count = count_cat("Databases & Caching")
        cloud_count = count_cat("Cloud & DevOps")
        ai_dsa_count = count_cat("AI, ML & Data Science") + count_cat("Core CS & Architecture")

        return {
            "Frontend": min(25 + fe_count * 16, 95),
            "Backend": min(25 + be_count * 16, 95),
            "Databases": min(25 + db_count * 20, 95),
            "Cloud & DevOps": min(20 + cloud_count * 18, 95),
            "Algorithms & AI": min(30 + ai_dsa_count * 15, 95)
        }

    def _get_readiness_verdict(self, match_pct):
        if match_pct >= 80:
            return {
                "level": "Job Ready! 🚀",
                "badge_class": "badge-emerald",
                "summary": "Outstanding skill alignment. You possess the essential and high-demand skills for this role."
            }
        elif match_pct >= 55:
            return {
                "level": "Near Ready (2-3 Weeks Gap) ⚡",
                "badge_class": "badge-amber",
                "summary": "Solid foundation! Bridging 2 or 3 missing core tools will dramatically boost your shortlist rate."
            }
        else:
            return {
                "level": "Emerging Fresher (Roadmap Recommended) 📚",
                "badge_class": "badge-indigo",
                "summary": "Great starting point. Follow the personalized 4-week roadmap to build industry-standard competencies."
            }
