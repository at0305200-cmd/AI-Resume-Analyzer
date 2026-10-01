from .skills import skill_exists


def match_skills(resume_skills, job_description, all_skills):

    required_skills = []

    for skill in all_skills:

        if skill_exists(skill, job_description):
            required_skills.append(skill)


    matched_skills = []

    for skill in required_skills:

        if skill in resume_skills:
            matched_skills.append(skill)


    missing_skills = []

    for skill in required_skills:

        if skill not in resume_skills:
            missing_skills.append(skill)


    if required_skills:

        match_percentage = (
            len(matched_skills) /
            len(required_skills)
        ) * 100

    else:

        match_percentage = 0


    return {
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 2),
    }