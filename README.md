# FastCover AI

AI-powered cover letter generator that creates personalized and downloadable PDF cover letters using your resume and job description.

Built with React, FastAPI, Tailwind CSS, Framer Motion, and Google Gemini AI.

---

## Features

- AI-generated personalized cover letters
- Resume PDF upload
- Job description matching
- Download cover letter as PDF
- Real-time preview
- Responsive modern UI
- Loading animations
- Contact Us popup form
- ATS-friendly writing style
- Fast and simple user experience

---

# Tech Stack

## Frontend
- React + Vite
- Tailwind CSS
- Framer Motion
- Axios
- Lucide React

## Backend
- FastAPI
- Google Gemini AI
- PyMuPDF
- ReportLab
- Resend Email API

---

# Project Structure

```bash
FASTCOVER-AI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/pearl31patel/FastCover-AI.git
cd FastCover-AI
```

---

# Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```bash
http://localhost:5173
```

---

# Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on:

```bash
http://127.0.0.1:8000
```

---

# Environment Variables

Create:

```bash
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
CONTACT_RECEIVER_EMAIL=your_email@gmail.com
```

---

# API Endpoints

## Preview Cover Letter

```http
POST /preview-cover-letter
```

## Download PDF Cover Letter

```http
POST /generate-cover-letter
```

## Contact Form

```http
POST /contact
```

---

# How It Works

1. Upload your resume PDF
2. Enter company name and role
3. Paste job description
4. AI generates personalized cover letter
5. Preview instantly
6. Download as professional PDF

---

# Upcoming Features

- Better cover letter templates
- Tone customization
- User login system
- Saved cover letters
- ATS keyword score
- Missing keyword detection
- Resume improvement suggestions
- Chrome extension auto-fill
- Premium AI rewrite mode
- Job application tracker

---

# Screenshots

Add screenshots here later.

---

# Author

## Pearl Patel

GitHub:
https://github.com/pearl31patel

---

# License

This project is open-source and free to use.
