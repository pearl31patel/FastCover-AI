from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import fitz
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os
import re
from html import escape
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None

try:
    import resend
except ImportError:
    resend = None


load_dotenv()

if resend:
    resend.api_key = os.getenv("RESEND_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

client = genai.Client(api_key=GEMINI_API_KEY) if genai and GEMINI_API_KEY else None

app = FastAPI(title="FastCover AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


SKILL_KEYWORDS = [
    "react", "next.js", "nextjs", "javascript", "typescript", "html", "css",
    "tailwind", "frontend", "front-end", "backend", "back-end", "full-stack",
    "full stack", "node", "express", "python", "fastapi", "django", "flask",
    "java", "c++", "sql", "mysql", "postgresql", "mongodb", "redis", "aws",
    "docker", "git", "github", "api", "rest", "testing", "debugging",
    "responsive", "ui", "ux", "figma", "product design", "user research",
    "accessibility", "machine learning", "ai", "llm", "automation", "data",
    "pandas", "scikit-learn", "analytics", "seo", "marketing",
    "communication", "collaboration", "documentation", "project management",
]

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "you", "your", "our",
    "are", "will", "from", "have", "has", "job", "role", "position",
    "team", "company", "work", "working", "skills", "experience",
    "candidate", "requirements", "ability", "strong", "using", "use",
}

DISPLAY_NAMES = {
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "html": "HTML",
    "css": "CSS",
    "tailwind": "Tailwind CSS",
    "python": "Python",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "aws": "AWS",
    "api": "API development",
    "rest": "REST APIs",
    "frontend": "frontend development",
    "front-end": "frontend development",
    "backend": "backend development",
    "back-end": "backend development",
    "ui": "UI",
    "ux": "UX",
    "figma": "Figma",
    "llm": "LLMs",
    "ai": "AI",
    "seo": "SEO",
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def display_keyword(keyword: str) -> str:
    return DISPLAY_NAMES.get(keyword.lower(), keyword)


def extract_resume_text(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"

    return text[:9000]


def split_resume_points(resume_text: str) -> list[str]:
    raw_points = re.split(r"[\n•|]+|(?<=[.!?])\s+", resume_text or "")
    points = []

    for point in raw_points:
        point = re.sub(r"\s+", " ", point).strip(" -–—\t")

        if 35 <= len(point) <= 240:
            points.append(point)

    return points


def find_keyword_matches(resume_text: str, job_description: str, role: str) -> list[str]:
    resume_lower = resume_text.lower()
    job_lower = f"{job_description} {role}".lower()

    matches = []

    for keyword in SKILL_KEYWORDS:
        if keyword in resume_lower and keyword in job_lower:
            matches.append(keyword)

    resume_words = set(re.findall(r"[A-Za-z][A-Za-z+.#-]{2,}", resume_lower))
    job_words = re.findall(r"[A-Za-z][A-Za-z+.#-]{2,}", job_lower)

    for word in job_words:
        if word not in STOPWORDS and word in resume_words and word not in matches:
            matches.append(word)

        if len(matches) >= 10:
            break

    return matches[:10]


def select_resume_evidence(resume_text: str, matched_keywords: list[str]) -> list[str]:
    points = split_resume_points(resume_text)
    scored_points = []

    for point in points:
        point_lower = point.lower()

        score = sum(
            1 for keyword in matched_keywords
            if keyword.lower() in point_lower
        )

        if re.search(
            r"\b(project|developed|built|designed|implemented|created|optimized|improved|deployed|managed|integrated)\b",
            point_lower,
        ):
            score += 2

        if re.search(r"\b\d+%|\b\d+[Kk+]?\b", point):
            score += 1

        if score > 0:
            scored_points.append((score, point))

    scored_points.sort(key=lambda item: item[0], reverse=True)

    return [point for _, point in scored_points[:3]]


def format_list(items: list[str], fallback: str = "relevant hands-on experience") -> str:
    clean_items = [display_keyword(item) for item in items[:4]]

    if not clean_items:
        return fallback

    if len(clean_items) == 1:
        return clean_items[0]

    if len(clean_items) == 2:
        return f"{clean_items[0]} and {clean_items[1]}"

    return f"{', '.join(clean_items[:-1])}, and {clean_items[-1]}"


def infer_focus_area(role: str, job_description: str) -> str:
    text = f"{role} {job_description}".lower()

    if any(word in text for word in ["frontend", "front-end", "react", "ui", "product design", "figma", "ux"]):
        return "frontend and product-focused work"

    if any(word in text for word in ["backend", "api", "database", "server", "cloud"]):
        return "backend and systems-focused work"

    if any(word in text for word in ["ai", "machine learning", "automation", "data", "analytics"]):
        return "AI, automation, and data-focused work"

    if any(word in text for word in ["marketing", "seo", "sales", "business development"]):
        return "business growth and communication-focused work"

    return "the responsibilities of this role"


def clean_ai_output(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"^```[a-zA-Z]*", "", text).strip()
    text = text.replace("```", "").strip()

    text = re.sub(r"\[date\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(date\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"date:\s*", "", text, flags=re.IGNORECASE)

    lines = [line.rstrip() for line in text.splitlines()]

    dear_index = None
    for index, line in enumerate(lines):
        if re.match(r"^\s*Dear\b", line, re.IGNORECASE):
            dear_index = index
            break

    if dear_index is not None:
        lines = lines[dear_index:]

    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        if re.fullmatch(r"\[?date\]?", stripped, re.IGNORECASE):
            continue

        if "insert date" in stripped.lower():
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def is_bad_output(text: str) -> bool:
    if not text:
        return True

    lower = text.lower()

    bad_phrases = [
        "i believe my background matches the needs of this role",
        "attention to detail, communication, organization, and the ability to support business needs",
        "[date]",
        "insert date",
        "your generated cover letter will appear here",
    ]

    if any(phrase in lower for phrase in bad_phrases):
        return True

    if re.search(r"\[[^\]]+\]", text):
        return True

    if len(text.split()) < 90:
        return True

    return False


def generate_personalized_fallback(
    name: str,
    company: str,
    role: str,
    resume_text: str,
    job_description: str,
) -> str:
    matched_keywords = find_keyword_matches(resume_text, job_description, role)
    evidence_points = select_resume_evidence(resume_text, matched_keywords)

    skills_text = format_list(matched_keywords)
    focus_area = infer_focus_area(role, job_description)

    if evidence_points:
        evidence_sentence = " ".join(
            point.rstrip(".") + "." for point in evidence_points[:2]
        )
    else:
        evidence_sentence = (
            f"My background includes practical experience in {skills_text}. "
            "I have worked on projects where I needed to understand requirements, build useful solutions, and communicate clearly."
        )

    extra_sentence = ""
    if len(evidence_points) >= 3:
        extra_sentence = f" Another relevant point from my experience is {evidence_points[2].rstrip('.')}."

    return f"""Dear Hiring Manager,

I am excited to apply for the {role} position at {company}. This opportunity stood out to me because it connects closely with my background in {skills_text} and my interest in {focus_area}.

{evidence_sentence}

Based on the job description, I understand that this role needs someone who can learn quickly, contribute with relevant skills, and deliver reliable work. I would bring hands-on project experience, strong ownership, and a practical approach to solving problems.{extra_sentence}

Thank you for your time and consideration. I would appreciate the opportunity to discuss how my experience can support the {role} position at {company}.

Sincerely,
{name}""".strip()


def build_prompt(
    name: str,
    company: str,
    role: str,
    resume_text: str,
    job_description: str,
) -> str:
    return f"""
You are an expert cover letter writer.

Write a personalized cover letter using ONLY the resume and job description.

Strict rules:
- Return only the final cover letter.
- Start directly with: Dear Hiring Manager,
- Do NOT include candidate name, email, phone number, address, company address, or date at the top.
- Do NOT write [Date].
- Do NOT use any placeholders.
- Do NOT write generic content.
- Do NOT say: "I believe my background matches the needs of this role."
- Do NOT say: "attention to detail, communication, organization, and the ability to support business needs."
- Use specific skills, tools, projects, and experience from the resume.
- Match the letter to the exact company and role.
- Do not invent anything.
- Keep it professional, natural, and concise.
- Keep it around 180 to 240 words.
- Use simple grammar.
- End with:
Sincerely,
{name}

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


def build_retry_prompt(
    name: str,
    company: str,
    role: str,
    resume_text: str,
    job_description: str,
    bad_output: str,
) -> str:
    return f"""
The previous cover letter was not acceptable because it was generic or included placeholders/header formatting.

Rewrite it correctly.

Rules:
- Start directly with: Dear Hiring Manager,
- No name/email/phone header.
- No company address.
- No date.
- No [Date].
- No placeholders.
- Make it specific to {company} and the {role} role.
- Use resume evidence only.
- Keep it 180 to 240 words.
- End with:
Sincerely,
{name}

Bad previous output:
{bad_output}

Resume:
{resume_text}

Job Description:
{job_description}
"""


def call_gemini(model_name: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "temperature": 0.8,
            "top_p": 0.9,
        },
    )

    if response and getattr(response, "text", None):
        return response.text.strip()

    return ""


def generate_cover_letter(
    name: str,
    company: str,
    role: str,
    resume_text: str,
    job_description: str,
) -> str:
    if client:
        model_candidates = []

        if GEMINI_MODEL:
            model_candidates.append(GEMINI_MODEL)

        model_candidates.extend(
            [
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
            ]
        )

        used_models = set()
        main_prompt = build_prompt(name, company, role, resume_text, job_description)

        for model_name in model_candidates:
            if model_name in used_models:
                continue

            used_models.add(model_name)

            try:
                print(f"Calling Gemini model: {model_name}")

                first_output = call_gemini(model_name, main_prompt)
                cleaned_output = clean_ai_output(first_output)

                if not is_bad_output(cleaned_output):
                    return cleaned_output

                print("First Gemini output was generic or had placeholder. Retrying...")

                retry_prompt = build_retry_prompt(
                    name=name,
                    company=company,
                    role=role,
                    resume_text=resume_text,
                    job_description=job_description,
                    bad_output=cleaned_output,
                )

                second_output = call_gemini(model_name, retry_prompt)
                cleaned_retry_output = clean_ai_output(second_output)

                if not is_bad_output(cleaned_retry_output):
                    return cleaned_retry_output

                print("Retry output still not good. Trying next model...")

            except Exception as e:
                print(f"Gemini failed for {model_name}: {e}")

    return generate_personalized_fallback(
        name=name,
        company=company,
        role=role,
        resume_text=resume_text,
        job_description=job_description,
    )


def create_pdf(text: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    for paragraph in text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(escape(paragraph.strip()), styles["Normal"]))
            story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)

    return buffer


def safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value or "cover_letter")
    return value.strip("_") or "cover_letter"


@app.get("/")
async def root():
    return {
        "message": "FastCover AI backend is running"
    }


@app.post("/preview-cover-letter")
async def preview_cover_letter(
    resume: UploadFile = File(...),
    name: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    job_description: str = Form(...),
):
    file_bytes = await resume.read()
    resume_text = extract_resume_text(file_bytes)

    cover_letter = generate_cover_letter(
        name=clean_text(name),
        company=clean_text(company),
        role=clean_text(role),
        resume_text=clean_text(resume_text),
        job_description=clean_text(job_description),
    )

    return {
        "cover_letter": cover_letter
    }


@app.post("/generate-cover-letter")
async def generate_cover_letter_pdf(
    resume: UploadFile = File(...),
    name: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    job_description: str = Form(...),
):
    file_bytes = await resume.read()
    resume_text = extract_resume_text(file_bytes)

    cover_letter = generate_cover_letter(
        name=clean_text(name),
        company=clean_text(company),
        role=clean_text(role),
        resume_text=clean_text(resume_text),
        job_description=clean_text(job_description),
    )

    pdf = create_pdf(cover_letter)

    filename = f"{safe_filename(company)}_{safe_filename(role)}_Cover_Letter.pdf"

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


@app.post("/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    details: str = Form(...),
):
    try:
        if not resend:
            return {
                "message": "Email service is not installed on the server"
            }

        resend.Emails.send(
            {
                "from": "FastCover AI <onboarding@resend.dev>",
                "to": os.getenv("CONTACT_RECEIVER_EMAIL"),
                "subject": "New FastCover AI Contact Form Submission",
                "html": f"""
                    <h2>New Contact Form Submission</h2>
                    <p><b>Name:</b> {escape(name)}</p>
                    <p><b>Email:</b> {escape(email)}</p>
                    <p><b>Phone:</b> {escape(phone)}</p>
                    <p><b>Details:</b></p>
                    <p>{escape(details)}</p>
                """,
            }
        )

        return {
            "message": "Message sent successfully"
        }

    except Exception as e:
        print("Contact form error:", e)

        return {
            "message": "Failed to send message"
        }