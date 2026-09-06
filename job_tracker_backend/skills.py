import re

"""
A curated list of common technical and professional skills used for
keyword-based skill gap analysis between a resume and a job description.
"""

SKILL_KEYWORDS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "html", "css", "php", "kotlin", "swift", "r",

    # Backend / frameworks
    "fastapi", "django", "flask", "node.js", "express", "spring boot",
    "rest api", "graphql", "microservices",

    # Frontend
    "react", "angular", "vue", "next.js", "redux", "tailwind",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "git", "github", "linux",

    # Data / ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "data analysis", "data visualization", "tableau", "power bi", "excel",
    "spark", "airflow", "etl",

    # Product / design
    "figma", "wireframing", "prototyping", "user research", "agile", "scrum",
    "jira", "product roadmap",

    # Soft/professional
    "communication", "leadership", "problem solving", "teamwork",
    "project management", "stakeholder management",
]





def extract_skills(text: str) -> set:
    """
    Returns the set of known skill keywords found in the given text,
    using word-boundary matching to avoid false positives on short
    keywords (e.g. "r" matching inside "your").
    """
    if not text:
        return set()

    text_lower = text.lower()
    found = set()

    for skill in SKILL_KEYWORDS:
        # Escape special regex characters in skill names (e.g. "c++", "node.js")
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    return found
import re


def extract_required_experience(job_description: str) -> int:
    """
    Extracts the minimum years of experience required from a job description,
    if mentioned (e.g. "2+ years", "3-5 years experience", "at least 4 years").
    Returns 0 if no experience requirement is found.
    """
    if not job_description:
        return 0

    # Matches patterns like: "2+ years", "3 years", "2-4 years", "at least 5 years"
    pattern = r'(\d+)\+?\s*(?:-\s*\d+\s*)?\s*years?'
    matches = re.findall(pattern, job_description.lower())

    if not matches:
        return 0

    # If multiple numbers mentioned, take the minimum required (the entry threshold)
    return min(int(m) for m in matches)

def compute_skill_gap(resume_text: str, job_description: str, user_years_experience: int = 0) -> dict:
    """
    Compares skills mentioned in the resume vs. the job description,
    and checks whether the user meets the experience requirement.
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    required_years = extract_required_experience(job_description)
    experience_gap = required_years > (user_years_experience or 0)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "required_years_experience": required_years,
        "user_years_experience": user_years_experience or 0,
        "experience_gap": experience_gap,
    }