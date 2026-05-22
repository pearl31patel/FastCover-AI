from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import fitz
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import re
from google import genai
from dotenv import load_dotenv
import os
import resend

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY is missing. Add it in backend/.env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="FastCover AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_resume_text(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:5000]

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def generate_cover_letter(name, company, role, resume_text, job_description):
    prompt = f"""
You are an expert cover letter writer.

Write a personalized cover letter for this candidate.

Important rules:
- Use only the resume and job description.
- Match the correct job field.
- If this is an accounting job, write an accounting-focused letter.
- If this is a software job, write a software-focused letter.
- Do not mention skills that are not in the resume.
- (important)Do not write things from job description if those things are not present in uploaded resume.
- Do not write generic text.
- Keep it professional, natural, and concise.
- Use simple grammar.
- End with the candidate name.

Candidate Name:
{name}

Company:
{company}

Role:
{role}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    try:
        print("Calling Gemini with new google-genai package...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        print("Gemini response received")

        if response and response.text:
            return response.text.strip()

        raise Exception("Empty Gemini response")

    except Exception as e:
        print("Gemini failed:", e)
        return f"""
Dear Hiring Manager,

I am excited to apply for the {role} position at {company}. I believe my background matches the needs of this role.

I have reviewed the job description and understand that this position requires attention to detail, communication, organization, and the ability to support business needs. I am confident that my experience and willingness to learn can help me contribute to your team.

Thank you for your time and consideration. I would be grateful for the opportunity to discuss my application.

Sincerely,
{name}
""".strip()

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    for paragraph in text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), styles["Normal"]))
            story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

@app.post("/generate-cover-letter")
async def generate_cover_letter_pdf(
    resume: UploadFile = File(...),
    name: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    job_description: str = Form(...)
):
    file_bytes = await resume.read()
    resume_text = extract_resume_text(file_bytes)

    cover_letter = generate_cover_letter(
        name=name,
        company=company,
        role=role,
        resume_text=clean_text(resume_text),
        job_description=clean_text(job_description)
    )

    pdf = create_pdf(cover_letter)

    filename = f"{company}_{role}_Cover_Letter.pdf".replace(" ", "_")

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/preview-cover-letter")
async def preview_cover_letter(
    resume: UploadFile = File(...),
    name: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    job_description: str = Form(...)
):
    file_bytes = await resume.read()
    resume_text = extract_resume_text(file_bytes)

    cover_letter = generate_cover_letter(
        name=name,
        company=company,
        role=role,
        resume_text=clean_text(resume_text),
        job_description=clean_text(job_description)
    )

    return {"cover_letter": cover_letter}

@app.post("/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    details: str = Form(...)
):
    try:
        resend.Emails.send({
            "from": "FastCover AI <onboarding@resend.dev>",
            "to": os.getenv("CONTACT_RECEIVER_EMAIL"),
            "subject": "New FastCover AI Contact Form Submission",
            "html": f"""
                <h2>New Contact Form Submission</h2>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Details:</b></p>
                <p>{details}</p>
            """
        })

        return {"message": "Message sent successfully"}

    except Exception as e:
        print("Contact form error:", e)
        return {"message": "Failed to send message"}