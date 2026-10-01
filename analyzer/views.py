from django.shortcuts import render, get_object_or_404

from .models import Resume
from .pdf_utils import extract_text_from_pdf
from .skills import detect_skills, SKILLS
from .matcher import match_skills
from .nlp_matcher import calculate_text_similarity


def home(request):

    message = ""
    message_type = ""
    extracted_text = ""
    detected_skills = []
    analysis = None

    if request.method == "POST":

        resume_file = request.FILES.get("resume")

        job_description = request.POST.get(
            "job_description",
            ""
        ).strip()

        # --------------------------------
        # CHECK RESUME FILE
        # --------------------------------

        if not resume_file:

            message = "ERROR: Resume file not selected."
            message_type = "error"

        # --------------------------------
        # CHECK PDF
        # --------------------------------

        elif not resume_file.name.lower().endswith(".pdf"):

            message = "ERROR: Only PDF files are allowed."
            message_type = "error"

        # --------------------------------
        # CHECK JOB DESCRIPTION
        # --------------------------------

        elif not job_description:

            message = "ERROR: Job description is empty."
            message_type = "error"

        else:

            try:

                # ====================================
                # STEP 1 - CREATE DATABASE RECORD
                # ====================================

                print("\n==============================")
                print("STEP 1: Creating database record")
                print("==============================")

                resume = Resume.objects.create(
                    file=resume_file,
                    job_description=job_description
                )

                print("SUCCESS: Database record created")
                print("Resume ID:", resume.id)

                # ====================================
                # STEP 2 - EXTRACT PDF TEXT
                # ====================================

                print("\n==============================")
                print("STEP 2: Extracting PDF text")
                print("==============================")

                extracted_text = extract_text_from_pdf(
                    resume.file.path
                )

                print(
                    "Extracted text length:",
                    len(extracted_text)
                )

                # --------------------------------
                # CHECK EXTRACTED TEXT
                # --------------------------------

                if not extracted_text.strip():

                    print("ERROR: No text extracted from PDF.")

                    message = (
                        "ERROR: PDF text could not be extracted."
                    )

                    message_type = "error"

                    resume.delete()

                else:

                    print("SUCCESS: PDF text extracted")

                    # ====================================
                    # STEP 3 - DETECT SKILLS
                    # ====================================

                    print("\n==============================")
                    print("STEP 3: Detecting skills")
                    print("==============================")

                    detected_skills = detect_skills(
                        extracted_text
                    )

                    print(
                        "Detected skills:",
                        detected_skills
                    )

                    # ====================================
                    # STEP 4 - MATCH SKILLS
                    # ====================================

                    print("\n==============================")
                    print("STEP 4: Matching skills")
                    print("==============================")

                    analysis = match_skills(
                        detected_skills,
                        job_description,
                        SKILLS
                    )

                    print(
                        "Required skills:",
                        analysis["required_skills"]
                    )

                    print(
                        "Matched skills:",
                        analysis["matched_skills"]
                    )

                    print(
                        "Missing skills:",
                        analysis["missing_skills"]
                    )

                    print(
                        "Skill score:",
                        analysis["match_percentage"]
                    )

                    # ====================================
                    # STEP 5 - NLP SIMILARITY
                    # ====================================

                    print("\n==============================")
                    print("STEP 5: NLP similarity")
                    print("==============================")

                    try:

                        nlp_score = calculate_text_similarity(
                            extracted_text,
                            job_description
                        )

                    except ValueError:

                        print(
                            "WARNING: NLP similarity "
                            "could not be calculated."
                        )

                        nlp_score = 0

                    print(
                        "NLP score:",
                        nlp_score
                    )

                    # ====================================
                    # STEP 6 - CALCULATE FINAL SCORE
                    # ====================================

                    print("\n==============================")
                    print("STEP 6: Calculating final score")
                    print("==============================")

                    skill_score = analysis[
                        "match_percentage"
                    ]

                    final_score = (
                        skill_score * 0.60
                        + nlp_score * 0.40
                    )

                    print(
                        "Skill score:",
                        skill_score
                    )

                    print(
                        "NLP score:",
                        nlp_score
                    )

                    print(
                        "Final score:",
                        final_score
                    )

                    # ====================================
                    # STORE ANALYSIS RESULTS
                    # ====================================

                    analysis["nlp_score"] = round(
                        nlp_score,
                        2
                    )

                    analysis["skill_score"] = round(
                        skill_score,
                        2
                    )

                    analysis["match_percentage"] = round(
                        final_score,
                        2
                    )

                    # ====================================
                    # STEP 7 - SAVE ANALYSIS
                    # ====================================

                    print("\n==============================")
                    print("STEP 7: Saving analysis")
                    print("==============================")

                    resume.extracted_text = (
                        extracted_text
                    )

                    resume.detected_skills = ", ".join(
                        detected_skills
                    )

                    resume.match_percentage = (
                        analysis["match_percentage"]
                    )

                    resume.nlp_score = (
                        analysis["nlp_score"]
                    )

                    resume.skill_score = (
                        analysis["skill_score"]
                    )

                    resume.matched_skills = ", ".join(
                        analysis["matched_skills"]
                    )

                    resume.missing_skills = ", ".join(
                        analysis["missing_skills"]
                    )

                    resume.save()

                    print("SUCCESS: Analysis saved")

                    print("\n==============================")
                    print("ANALYSIS COMPLETED SUCCESSFULLY")
                    print("==============================\n")

                    message = (
                        "Resume analyzed and saved successfully!"
                    )

                    message_type = "success"

            # ====================================
            # ERROR HANDLING
            # ====================================

            except Exception as e:

                print("\n")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("ANALYSIS FAILED")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                print(
                    "ERROR TYPE:",
                    type(e).__name__
                )

                print(
                    "ERROR:",
                    str(e)
                )

                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("\n")

                message = (
                    "Analysis failed: "
                    + type(e).__name__
                    + " - "
                    + str(e)
                )

                message_type = "error"

    # ====================================
    # RENDER HOME PAGE
    # ====================================

    return render(
        request,
        "analyzer/home.html",
        {
            "message": message,
            "message_type": message_type,
            "extracted_text": extracted_text,
            "detected_skills": detected_skills,
            "analysis": analysis,
        }
    )


# ========================================
# RESUME HISTORY
# ========================================

def history(request):

    resumes = Resume.objects.all().order_by(
        "-uploaded_at"
    )

    return render(
        request,
        "analyzer/history.html",
        {
            "resumes": resumes,
        }
    )


# ========================================
# RESUME DETAIL
# ========================================

def resume_detail(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id
    )

    # --------------------------------
    # MATCHED SKILLS
    # --------------------------------

    matched_skills = []

    if resume.matched_skills:

        matched_skills = [
            skill.strip()
            for skill in resume.matched_skills.split(",")
        ]

    # --------------------------------
    # MISSING SKILLS
    # --------------------------------

    missing_skills = []

    if resume.missing_skills:

        missing_skills = [
            skill.strip()
            for skill in resume.missing_skills.split(",")
        ]

    # --------------------------------
    # DETECTED SKILLS
    # --------------------------------

    detected_skills = []

    if resume.detected_skills:

        detected_skills = [
            skill.strip()
            for skill in resume.detected_skills.split(",")
        ]

    # --------------------------------
    # RENDER DETAIL PAGE
    # --------------------------------

    return render(
        request,
        "analyzer/resume_detail.html",
        {
            "resume": resume,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "detected_skills": detected_skills,
        }
    )