# AI-Powered Resume Screening and Candidate Ranking System

> **Research Project**: Solving the gap of *Semantic Resume Matching vs. Traditional Keyword Matching* using Sentence Transformers and Explainable AI.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Semantic Matching** | Uses `all-MiniLM-L6-v2` sentence transformer for deep semantic similarity |
| **Explainable AI** | Hybrid explainability: exact skill matching + semantic skill analysis |
| **Candidate Ranking** | Automatic ranking by cosine similarity scores |
| **Resume Parsing** | Extracts structured data from PDF/DOCX using pdfplumber & python-docx |
| **Interview Scheduling** | Schedule with automatic email notifications |
| **Email Notifications** | Gmail SMTP with professional HTML templates |
| **HR Analytics** | Recharts-powered dashboard with insights |
| **JWT Authentication** | Secure recruiter-only access |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│   React Router • TailwindCSS • React Query • Recharts          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (Axios)
┌──────────────────────────┴──────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│   ┌─────────┐  ┌────────────┐  ┌──────────────┐               │
│   │ API     │→ │ Services   │→ │ Repositories │→ PostgreSQL   │
│   │ Layer   │  │ Layer      │  │ Layer        │               │
│   └─────────┘  └─────┬──────┘  └──────────────┘               │
│                       │                                        │
│              ┌────────┴────────┐                               │
│              │   AI Engine     │                               │
│              │ SentenceTransf. │                               │
│              │ Cosine Sim.     │                               │
│              │ Explainer       │                               │
│              └─────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Database queries
│   │   ├── ai/              # Embedding, Matcher, Explainer
│   │   ├── emails/          # SMTP + Templates
│   │   ├── core/            # Config, Security, Exceptions
│   │   ├── database/        # Session factory
│   │   └── utils/           # File & Resume parsers
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # 12 page components
│   │   ├── components/      # Layout + UI components
│   │   ├── services/        # Axios API layer
│   │   ├── contexts/        # Auth context
│   │   ├── routes/          # React Router setup
│   │   └── utils/           # Constants + formatters
│   └── package.json
└── docs/
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb resume_screening
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database URL, secret key, and SMTP credentials

# Run migrations
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `recruiters` | Recruiter accounts with auth |
| `jobs` | Job postings with JD embeddings |
| `candidates` | Applicants linked to jobs |
| `resumes` | Resume files with parsed data + embeddings |
| `candidate_scores` | Match scores with explainability |
| `interviews` | Scheduled interviews |
| `emails_sent` | Email audit log |
| `activity_logs` | Recruiter action tracking |

---

## 🤖 AI Pipeline

```
Resume Upload → Text Extraction → Structured Parsing
                                        │
                                        ▼
                    ┌──────────── Embedding ────────────┐
                    │  SentenceTransformer              │
                    │  all-MiniLM-L6-v2 (384-dim)      │
                    └───────────────┬───────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
     Resume Embedding        JD Embedding           Skill Embeddings
            │                       │                       │
            └────── Cosine ─────────┘                       │
                   Similarity                               │
                      │                                     │
                      ▼                                     ▼
              Overall Score                     Semantic Skill Matching
                      │                                     │
                      └──────────── Explainability ─────────┘
                                        │
                                        ▼
                              Ranked Candidates
                        (with matched/missing/semantic skills)
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register recruiter |
| POST | `/api/v1/auth/login` | Login (JWT) |
| GET | `/api/v1/auth/me` | Current user |
| GET/POST | `/api/v1/jobs` | List / Create jobs |
| GET/PUT/DELETE | `/api/v1/jobs/{id}` | Job CRUD |
| POST | `/api/v1/resumes/upload/{job_id}` | Upload resumes |
| GET | `/api/v1/candidates` | List candidates |
| GET | `/api/v1/candidates/{id}` | Candidate details |
| POST | `/api/v1/jobs/{id}/rank` | Trigger ranking |
| GET | `/api/v1/jobs/{id}/rankings` | View rankings |
| GET | `/api/v1/rankings/{id}/explain` | Explainability |
| GET/POST | `/api/v1/interviews` | List / Schedule |
| GET/POST | `/api/v1/emails` | Email logs / Send |
| GET | `/api/v1/analytics/dashboard` | Analytics data |

---

## 🔐 Security

- **JWT Authentication** with bcrypt password hashing
- **Input Validation** via Pydantic schemas
- **File Validation** (type + size limits)
- **CORS Configuration** for frontend origin
- **Environment Variables** for all secrets

---

## 📧 Email Templates

Three professional HTML email templates:
1. **Shortlisted** — Congratulations notification
2. **Rejected** — Professional rejection
3. **Interview Scheduled** — With date, time, mode, and meeting link

---

## 📊 Analytics Charts

- **Top Skills** — Bar chart of most required skills
- **Score Distribution** — Distribution of match scores
- **Monthly Activity** — Area chart of jobs/candidates/interviews over time
- **Status Distribution** — Pie chart of candidate statuses

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS v4, React Router, Axios, React Query, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | PostgreSQL |
| AI | Sentence Transformers (all-MiniLM-L6-v2), scikit-learn |
| File Parsing | pdfplumber, python-docx |
| Email | Gmail SMTP |
| Auth | JWT (python-jose), bcrypt (passlib) |

---

## 📄 License

This project is for research and educational purposes.
