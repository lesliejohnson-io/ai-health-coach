import json
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

# ---------- Paths / Constants ----------
BASE_DIR = Path(__file__).resolve().parent
PLAN_PATH = BASE_DIR / "health_plan.md"
CHECKINS_PATH = BASE_DIR / "checkins.jsonl"
INDEX_HTML_PATH = BASE_DIR / "templates" / "index.html"
FAVICON_PATH = BASE_DIR / "static" / "favicon.ico"

MODEL_NAME = "gpt-5"

SYSTEM_PROMPT = """You are an AI health and fitness coach.
You are supportive, candid, and practical.
You never give medical diagnosis. If symptoms are concerning, advise seeing a clinician.
Prioritize: sleep, protein, steps, strength training, stress regulation.
Ask at most 2 clarifying questions if needed, otherwise produce a clear plan.

Output MUST be valid JSON with this schema:
{
  "today_focus": "string",
  "plan": {
    "sleep": ["..."],
    "nutrition": ["..."],
    "training": ["..."],
    "steps": ["..."],
    "recovery": ["..."]
  },
  "one_small_win": "string",
  "check_in_questions": ["q1", "q2"]
}
"""

# ---------- App ----------
app = FastAPI(title="AI Health Coach")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ---------- Models ----------
class CheckIn(BaseModel):
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    protein_g: int | None = Field(default=None, ge=0, le=500)
    steps: int | None = Field(default=None, ge=0, le=100000)
    training: str = ""
    energy_1_10: int | None = Field(default=None, ge=1, le=10)
    mood_1_10: int | None = Field(default=None, ge=1, le=10)
    notes: str = ""


# ---------- Helpers ----------
def load_plan() -> str:
    if not PLAN_PATH.exists():
        return "# Health Plan\n\n(health_plan.md not found yet — add your plan.)"
    return PLAN_PATH.read_text(encoding="utf-8")


def load_recent_checkins(limit: int = 7) -> list[dict[str, Any]]:
    if not CHECKINS_PATH.exists():
        return []

    out: list[dict[str, Any]] = []
    for line in CHECKINS_PATH.read_text(encoding="utf-8").splitlines()[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            # Skip malformed lines rather than crashing
            continue
    return out


def append_checkin(checkin: dict[str, Any]) -> None:
    CHECKINS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHECKINS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(checkin) + "\n")


def extract_output_text(resp) -> str:
    """Support multiple SDK shapes: prefer resp.output_text; fallback to output list parsing."""
    text = getattr(resp, "output_text", None)
    if text:
        return text

    chunks: list[str] = []
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for c in getattr(item, "content", []) or []:
                if getattr(c, "type", None) == "output_text":
                    chunks.append(getattr(c, "text", ""))
    return "".join(chunks).strip()


def call_ai_coach(plan_text: str, recent: list[dict[str, Any]], today: dict[str, Any]) -> dict[str, Any]:
    client = OpenAI()

    payload = {
        "health_plan": plan_text,
        "recent_checkins": recent,
        "today_checkin": today,
    }

    resp = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
    )

    text = extract_output_text(resp)
    if not text:
        raise ValueError("Empty response from coach.")

    return json.loads(text)


# ---------- Routes ----------
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # If you don't have favicon.ico yet, this will raise a clear file not found error.
    return FileResponse(str(FAVICON_PATH))


@app.get("/", response_class=HTMLResponse)
def index():
    if not INDEX_HTML_PATH.exists():
        return HTMLResponse("<h1>Missing templates/index.html</h1>", status_code=500)
    return HTMLResponse(INDEX_HTML_PATH.read_text(encoding="utf-8"))


@app.get("/api/plan")
def get_plan():
    return {"health_plan": load_plan()}


@app.get("/api/checkins")
def get_checkins():
    return {"checkins": load_recent_checkins(limit=14)}


@app.post("/api/checkin")
def post_checkin(checkin: CheckIn):
    today: dict[str, Any] = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        **checkin.model_dump(),
    }
    append_checkin(today)

    advice = call_ai_coach(
        plan_text=load_plan(),
        recent=load_recent_checkins(limit=7),
        today=today,
    )
    return {"advice": advice}
