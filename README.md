# 🤖 Self-Healing Sandbox

> **Autonomous QA Agent** — Paste a bug report, get a reproducible Dockerfile.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.5-4285F4.svg)](https://ai.google.dev)
[![E2B](https://img.shields.io/badge/E2B-Sandbox-orange.svg)](https://e2b.dev)

---

## ✨ Features

- 🧠 **AI-Powered Analysis** — Gemini understands natural language bug reports
- 🎭 **Playwright Automation** — Generates browser test scripts automatically
- 🔄 **Self-Healing** — Fixes broken selectors using Vision AI
- 📸 **Console Error Capture** — Detects JavaScript errors on target apps
- 🐙 **GitHub Integration** — Import issues with one click
- 💾 **Redis Persistence** — Sessions survive server restarts
- 📦 **Dockerfile Export** — Reproducible bug environments

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, falls back to in-memory)

### 1. Clone & Install

```bash
git clone https://github.com/your-repo/Self-Healing-Sandbox.git
cd Self-Healing-Sandbox

# Backend
pip install -r requirements.txt

# Frontend
cd dashboard
npm install
```

### 2. Configure Environment

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
E2B_API_KEY=your_e2b_api_key
REDIS_URL=redis://localhost:6379  # Optional
```

### 3. Run

```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload --port 3001

# Terminal 2 - Frontend
cd dashboard
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) 🎉

---

## 📁 Project Structure

```
Self-Healing-Sandbox/
├── agent/
│   ├── brain.py       # Gemini AI integration
│   ├── sandbox.py     # E2B sandbox management
│   └── workflow.py    # Self-healing loop
├── backend/
│   ├── main.py        # FastAPI endpoints
│   └── storage.py     # Redis session storage
├── dashboard/
│   └── src/
│       ├── App.jsx    # React dashboard
│       └── pages/     # Analytics pages
└── .env               # API keys
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Submit bug report for analysis |
| `GET` | `/status/{id}` | Get session status & logs |
| `POST` | `/reproduce/{id}` | Start reproduction workflow |
| `POST` | `/github/fetch-issue` | Import from GitHub Issue URL |
| `GET` | `/sessions` | List all sessions |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| AI | Gemini 2.5 Flash |
| Vision | Gemini Pro Vision |
| Sandbox | E2B Desktop |
| Browser | Playwright |
| Storage | Redis |

---

## 📊 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Bug       │────▶│   Gemini    │────▶│  Playwright │
│   Report    │     │   Analysis  │     │   Script    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Dockerfile │◀────│   Self-     │◀────│    E2B      │
│   Export    │     │   Healing   │     │   Sandbox   │
└─────────────┘     └─────────────┘     └─────────────┘
```
