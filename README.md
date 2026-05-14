# FriendlyNotes 📝

> **Turn any PDF into structured notes, formulas, and practice questions in seconds** — powered by Google Gemini 2.5 Flash.

---

## How It Works

1. User uploads a PDF via the drag-and-drop interface.
2. The FastAPI backend validates the file, uploads it to Gemini Files API, and sends a structured prompt.
3. Gemini returns a **strictly-typed JSON** object containing topics, notes, formulas, and Q&A.
4. The React frontend renders the content in an interactive tabbed dashboard.

---

## Project Structure

```
FriendlyNotes/
├── backend/
│   ├── main.py                  # FastAPI app, routes, validation
│   ├── services/
│   │   └── ai_generator.py      # Gemini API integration + response schema
│   ├── requirements.txt
│   ├── .env                     # ⚠️ Not committed — see .env.example
│   └── .env.example             # Template for environment variables
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── index.css
    │   └── components/
    │       ├── UploadSection.jsx
    │       └── LearningDashboard.jsx
    ├── index.html
    ├── package.json
    ├── .env                     # ⚠️ Not committed — see .env.example
    └── .env.example             # Template for environment variables
```

---

## Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- A **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey)

---

## Setup — Backend

```bash
cd backend

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and fill in your GEMINI_API_KEY

# 4. Start the development server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Setup — Frontend

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment variables
cp .env.example .env
# Edit .env if your backend runs on a different port/host

# 3. Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Your Google Gemini API key |
| `ALLOWED_ORIGINS` | optional | Comma-separated frontend origins (default: `http://localhost:5173`) |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | optional | Backend base URL (default: `http://localhost:8000`) |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Version info |
| `GET` | `/health` | Liveness probe |
| `POST` | `/upload` | Upload a PDF and receive study materials |

### `POST /upload` Response Shape

```json
{
  "topics": [
    {
      "title": "Topic Name",
      "notes": ["Key concept 1", "Key concept 2"],
      "formulas": [
        {
          "name": "Formula Name",
          "equation": "E = mc²",
          "description": "Explanation of the formula"
        }
      ],
      "questions": [
        {
          "question": "Practice question?",
          "answer": "Detailed answer."
        }
      ]
    }
  ]
}
```

---

## Limits

| Constraint | Value |
|---|---|
| Max PDF size | 20 MB |
| Accepted formats | PDF only |
| AI model timeout | 120 seconds |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Vanilla CSS |
| Backend | FastAPI, Python 3.10+ |
| AI | Google Gemini 2.5 Flash |
| Styling | Glassmorphism dark theme, Inter font |

---

## Production Deployment

- **Frontend**: Deploy the `frontend/` directory to [Vercel](https://vercel.com) or [Netlify](https://netlify.com). Set `VITE_API_URL` to your production backend URL.
- **Backend**: Deploy to [Railway](https://railway.app), [Render](https://render.com), or [Fly.io](https://fly.io). Set `GEMINI_API_KEY` and `ALLOWED_ORIGINS` as environment variables on the platform.

---

## License

MIT
