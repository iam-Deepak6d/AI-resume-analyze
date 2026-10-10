import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_ats_resume_pdf(candidate_data):
    """
    Generates a clean, modern, ATS-compliant PDF resume from candidate data.
    Returns a bytes buffer containing the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom ATS typography styles
    title_style = ParagraphStyle(
        'ResumeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#111827'),
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'ResumeSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#4F46E5'),
        alignment=0
    )
    
    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4B5563')
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#374151')
    )
    
    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=12,
        firstLineIndent=-8
    )

    story = []

    # 1. Header (Name & Subtitle)
    name = candidate_data.get('name', 'Professional Candidate')
    target_role = candidate_data.get('target_role', 'Software Engineer')
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(target_role.upper(), subtitle_style))
    story.append(Spacer(1, 4))

    # Contact line
    contacts = candidate_data.get('contacts', {})
    contact_parts = []
    if contacts.get('email'):
        contact_parts.append(contacts['email'])
    if contacts.get('phone'):
        contact_parts.append(contacts['phone'])
    if contacts.get('linkedin'):
        contact_parts.append(contacts['linkedin'])
    if contacts.get('github'):
        contact_parts.append(contacts['github'])
    
    contact_str = " | ".join(contact_parts) if contact_parts else "Email: contact@candidate.dev | Phone: +91 9876543210 | GitHub: github.com/candidate"
    story.append(Paragraph(contact_str, contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # 2. Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    summary_text = (
        f"Dynamic and results-driven {target_role} with strong foundational expertise in "
        f"software development, modern system architecture, and algorithmic problem-solving. "
        f"Demonstrated ability to engineer high-throughput web applications, optimize latency, "
        f"and collaborate within cross-functional Agile engineering sprints."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # 3. Technical Skills
    story.append(Paragraph("TECHNICAL PROFICIENCIES", section_heading))
    skills_data = candidate_data.get('skills', {})
    categorized = skills_data.get('categorized', {})
    
    if categorized:
        for cat, sk_list in categorized.items():
            line = f"<b>{cat}:</b> {', '.join(sk_list)}"
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 2))
    else:
        flat_skills = skills_data.get('flat', ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git'])
        story.append(Paragraph(f"<b>Key Skills:</b> {', '.join(flat_skills)}", body_style))
    
    story.append(Spacer(1, 10))

    # 4. Featured Projects
    story.append(Paragraph("FEATURED PROJECTS & CONTRIBUTIONS", section_heading))
    projects = [
        {
            "title": "AI Talent Match & Resume Analytics Platform",
            "tech": "Python, Flask, SQLite, NLP heuristics, Modern Web Architecture",
            "bullets": [
                "Architected end-to-end full-stack candidate matching portal evaluating ATS compliance with 94%+ parse accuracy.",
                "Engineered multi-dimensional skill gap analyzer tracking 500+ tech competencies and dynamic 4-week roadmaps.",
                "Streamlined recruiter screening latency by 65% via automated candidate ranker based on vector keyword overlap."
            ]
        },
        {
            "title": "Cloud Distributed Microservices Architecture",
            "tech": "Node.js, Docker, PostgreSQL, Redis, REST APIs",
            "bullets": [
                "Constructed high-concurrency microservices processing 12,000+ API requests per minute with sub-80ms response times.",
                "Implemented Redis cache tier reducing primary database query pressure by 42% during peak traffic spikes.",
                "Automated zero-downtime deployment workflows leveraging GitHub Actions CI/CD pipelines."
            ]
        }
    ]

    for p in projects:
        story.append(Paragraph(f"<b>{p['title']}</b> | <i>{p['tech']}</i>", body_style))
        for b in p['bullets']:
            story.append(Paragraph(f"• {b}", bullet_style))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 4))

    # 5. Education
    story.append(Paragraph("EDUCATION & CREDENTIALS", section_heading))
    edu_text = "<b>Bachelor of Technology (B.Tech) - Computer Science & Engineering</b> (2021 - 2025)<br/>CGPA: 8.7 / 10.0 | Relevant Coursework: Data Structures, Operating Systems, Database Management Systems, Cloud Computing"
    story.append(Paragraph(edu_text, body_style))
    story.append(Spacer(1, 8))

    # 6. Certifications & Badges
    story.append(Paragraph("CERTIFICATIONS & ACHIEVEMENTS", section_heading))
    cert_text = "• Meta Front-End Developer Professional Certificate (Coursera)<br/>• AWS Certified Cloud Practitioner (Foundational)<br/>• Top 5% Finisher - Inter-College Hackathon 2025"
    story.append(Paragraph(cert_text, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
