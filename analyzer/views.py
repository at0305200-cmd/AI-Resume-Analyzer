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


        # Check resume file

        if not resume_file:

            message = "Please select a resume PDF file."
            message_type = "error"


        # Check PDF extension

        elif not resume_file.name.lower().endswith(".pdf"):

            message = "Only PDF files are allowed."
            message_type = "error"


        # Check job description

        elif not job_description:

            message = "Please enter a job description."
            message_type = "error"


        else:

            try:

                # Save uploaded resume

                resume = Resume.objects.create(
                    file=resume_file,
                    job_description=job_description
                )


                # Extract text from PDF

                extracted_text = extract_text_from_pdf(
                    resume.file.path
                )


                # Check extracted text

                if not extracted_text.strip():

                    message = (
                        "Could not extract readable text "
                        "from this PDF."
                    )

                    message_type = "error"

                    resume.delete()


                else:

                    # Detect skills

                    detected_skills = detect_skills(
                        extracted_text
                    )


                    # Match skills

                    analysis = match_skills(
                        detected_skills,
                        job_description,
                        SKILLS
                    )


                    # Calculate NLP similarity

                    try:

                        nlp_score = calculate_text_similarity(
                            extracted_text,
                            job_description
                        )

                    except ValueError:

                        nlp_score = 0


                    # Skill score

                    skill_score = analysis[
                        "match_percentage"
                    ]


                    # Final score

                    final_score = (
                        skill_score * 0.60
                        + nlp_score * 0.40
                    )


                    # Store scores

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


                    # Save extracted text

                    resume.extracted_text = (
                        extracted_text
                    )


                    # Save detected skills

                    resume.detected_skills = ", ".join(
                        detected_skills
                    )


                    # Save final score

                    resume.match_percentage = (
                        analysis["match_percentage"]
                    )


                    # Save NLP score

                    resume.nlp_score = (
                        analysis["nlp_score"]
                    )


                    # Save skill score

                    resume.skill_score = (
                        analysis["skill_score"]
                    )


                    # Save matched skills

                    resume.matched_skills = ", ".join(
                        analysis["matched_skills"]
                    )


                    # Save missing skills

                    resume.missing_skills = ", ".join(
                        analysis["missing_skills"]
                    )


                    # Save database record

                    resume.save()


                    message = (
                        "Resume analyzed and saved successfully!"
                    )

                    message_type = "success"


            except Exception:

                message = (
                    "Something went wrong while "
                    "analyzing the resume. "
                    "Please try another PDF."
                )

                message_type = "error"


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


def resume_detail(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id
    )


    matched_skills = []

    if resume.matched_skills:

        matched_skills = [
            skill.strip()
            for skill in resume.matched_skills.split(",")
        ]


    missing_skills = []

    if resume.missing_skills:

        missing_skills = [
            skill.strip()
            for skill in resume.missing_skills.split(",")
        ]


    detected_skills = []

    if resume.detected_skills:

        detected_skills = [
            skill.strip()
            for skill in resume.detected_skills.split(",")
        ]


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