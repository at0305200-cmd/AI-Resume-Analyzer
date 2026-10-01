import re


SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "HTML",
    "CSS",
    "Django",
    "Flask",
    "React",
    "Node.js",
    "Express",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "SQL",
    "Git",
    "GitHub",
    "C",
    "C++",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Pandas",
    "NumPy",
    "scikit-learn",
]


def skill_exists(skill, text):
    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

    return re.search(
        pattern,
        text,
        re.IGNORECASE
    ) is not None


def detect_skills(text):

    detected_skills = []

    for skill in SKILLS:

        if skill_exists(skill, text):
            detected_skills.append(skill)

    return detected_skills