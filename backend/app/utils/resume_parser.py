"""
Resume Parser
=============
Extracts structured data (name, email, phone, skills, education,
experience, projects) from resume text using regex and heuristics.
"""

import re
from typing import List

from app.schemas.resume import ParsedResumeData


# ── Common skill keywords for matching ────────────────────────
COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "react", "angular", "vue", "node.js", "express", "django", "flask",
    "fastapi", "spring", "ruby", "rails", "php", "laravel", "go", "rust",
    "swift", "kotlin", "dart", "flutter", "react native",
    "html", "css", "sass", "tailwind", "bootstrap",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "github", "gitlab", "ci/cd", "jenkins",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "data science", "data analysis", "data engineering",
    "rest", "graphql", "microservices", "api",
    "linux", "unix", "windows", "bash",
    "agile", "scrum", "jira", "confluence",
    "figma", "sketch", "adobe", "photoshop",
    "excel", "power bi", "tableau",
    "blockchain", "solidity", "web3",
}


def parse_resume_text(text: str) -> ParsedResumeData:
    """
    Parse resume text and extract structured data.

    Uses regex patterns and heuristics for extraction.
    Not perfect — but provides a solid baseline for the research project.
    """
    return ParsedResumeData(
        name=_extract_name(text),
        email=_extract_email(text),
        phone=_extract_phone(text),
        skills=_extract_skills(text),
        education=_extract_education(text),
        experience=_extract_experience(text),
        projects=_extract_projects(text),
    )


def _extract_name(text: str) -> str:
    """Extract name from the first non-empty line (heuristic)."""
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        # Skip lines that look like headers, emails, or phones
        if line and not re.search(r'[@\d()+\-.]', line) and len(line) < 60:
            # Likely a name
            return line
    return ""


def _extract_email(text: str) -> str:
    """Extract email address using regex."""
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    """Extract phone number using regex."""
    match = re.search(
        r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}',
        text
    )
    return match.group(0).strip() if match else ""


def _extract_skills(text: str) -> List[str]:
    """Extract skills by matching against known skill keywords."""
    text_lower = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        # Use word boundaries for short skills
        if len(skill) <= 2:
            pattern = rf'\b{re.escape(skill)}\b'
        else:
            pattern = re.escape(skill)
        if re.search(pattern, text_lower):
            found.append(skill.title() if len(skill) > 2 else skill.upper())
    return sorted(set(found))


def _extract_section(text: str, headers: List[str]) -> List[str]:
    """Extract content under a section header."""
    lines = text.split("\n")
    capturing = False
    content = []

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        # Check if this line is one of our target headers
        if any(h in lower for h in headers):
            capturing = True
            continue

        # Check if this line is a different section header (stop capturing)
        if capturing and stripped and re.match(
            r'^[A-Z][A-Za-z\s&]+:?\s*$', stripped
        ):
            if not any(h in lower for h in headers):
                capturing = False
                continue

        if capturing and stripped:
            content.append(stripped)

    return content[:10]  # Limit to prevent overflow


def _extract_education(text: str) -> List[str]:
    """Extract education section."""
    return _extract_section(
        text, ["education", "academic", "qualification", "degree"]
    )


def _extract_experience(text: str) -> List[str]:
    """Extract work experience section."""
    return _extract_section(
        text, ["experience", "employment", "work history", "professional"]
    )


def _extract_projects(text: str) -> List[str]:
    """Extract projects section."""
    return _extract_section(
        text, ["project", "portfolio", "personal project"]
    )
