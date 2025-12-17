<h1>
  <img src="static/logo.svg" alt="AI Health Coach logo" width="40" style="vertical-align: middle; margin-right: 10px;" />
  AI Health Coach
</h1>

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-1cdaff)
![OpenAI](https://img.shields.io/badge/OpenAI-Responses%20API-1cdaff)
![Status](https://img.shields.io/badge/Status-Working%20Prototype-success)
![Mobile](https://img.shields.io/badge/Mobile--First-Yes-brightgreen)
![License](https://img.shields.io/badge/License-MIT-teal)


A **mobile-first AI health & fitness coach** that turns daily check-ins into clear, practical action plans.

Built to explore how **AI-driven coaching** can support consistency, nervous-system regulation, and behavior change without replacing human judgment or care.

---

## What it does

- Daily check-in (sleep, protein, steps, training, energy, mood)
- Generates a **personalized daily plan** using AI
- Emphasizes:
  - sleep
  - protein
  - movement
  - strength training
  - recovery & regulation
- Works on **desktop and phone**
- Persists recent check-ins locally for context

This is intentionally simple, as a foundation for more advanced coaching, analytics, and longitudinal insight.

---

## 📱 Mobile Screenshots

<div style="display: flex; gap: 24; align-items: flex-start; flex-wrap: wrap;">
  <img src="screenshots/form.png" alt="Daily check-in form" width="300">
  
  <img src="screenshots/response.png" alt="AI-generated daily plan" width="300">
</div>


---

## Design philosophy

- **Mobile first** — quick, low-friction check-ins
- **Coach-like tone** — supportive, practical, non-medical
- **Small wins > perfect plans**
- AI as a *thinking partner*, not an authority

The system prompt explicitly avoids diagnosis and prioritizes fundamentals.

---

## 🛠 Tech stack

- **Python 3.11**
- **FastAPI**
- **OpenAI Responses API**
- Vanilla **HTML / CSS / JS**
- Local JSONL persistence (easy to swap for a database)

---

## Run locally

### 1. Install dependencies
```bash
pip install fastapi uvicorn python-dotenv openai
````

### 2. Set environment variable

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Start the server

```bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open the app

* Desktop: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Phone (same Wi-Fi): http://YOUR_LOCAL_IP:8000

---

## 📂 Project structure

```
.
├── app.py
├── health_plan.md
├── checkins.jsonl        # ignored by git
├── templates/
│   └── index.html
├── static/
│   ├── styles.css
│   ├── app.js
│   ├── logo.svg
│   └── favicon.ico
└── screenshots/
    ├── checkin-form.png
    └── daily-plan.png
```

---

## 🔒 Notes on safety

* No medical diagnosis
* Encourages professional care when symptoms are concerning
* API keys handled via environment variables
* Personal data stored locally only (for now)

---

## 🔮 Possible next steps

* Authentication & user accounts
* Weekly trend summaries
* Metrics & progress visualization
* Database backend
* Deployment (Render / Fly.io)

---
