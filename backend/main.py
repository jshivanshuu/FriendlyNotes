import os
import logging
import tempfile
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from services.ai_generator import generate_learning_materials

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FriendlyNotes API",
    description="AI-powered PDF → structured study materials (notes, formulas, Q&A).",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — restrict to explicit origins from the environment
# ---------------------------------------------------------------------------
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS: List[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 20 971 520 bytes


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class MaterialResponse(BaseModel):
    topics: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def read_root():
    return {"message": "FriendlyNotes API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    """Lightweight liveness probe for uptime monitors."""
    return {"status": "ok"}


@app.post("/upload", response_model=MaterialResponse, tags=["Materials"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accept a PDF upload and return AI-generated study materials.

    Returns a JSON object with a 'topics' array, each topic containing:
    - title (str)
    - notes (list[str])
    - formulas (list[{name, equation, description}])
    - questions (list[{question, answer}])
    """

    # --- 1. File-type validation ---
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a valid .pdf file.",
        )

    # --- 2. API-key guard ---
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set.")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error. Please contact the administrator.",
        )

    # --- 3. Read & size-validate the file content ---
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large ({file_size_mb:.1f} MB). "
                f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
            ),
        )

    # --- 4. Process ---
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        logger.info("Processing '%s' (%.2f MB)", file.filename, file_size_mb)
        materials = generate_learning_materials(tmp_path, api_key)
        logger.info("Successfully generated materials for '%s'.", file.filename)
        return materials

    except ValueError as exc:
        # Raised explicitly by the service layer (e.g. bad AI response shape)
        logger.warning("Validation error for '%s': %s", file.filename, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except TimeoutError as exc:
        logger.error("Gemini request timed out for '%s'.", file.filename)
        raise HTTPException(
            status_code=504,
            detail="The AI model took too long to respond. Please try again with a smaller PDF.",
        ) from exc

    except Exception as exc:
        logger.error("Unexpected error for '%s': %s", file.filename, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process the PDF. Please try again later.",
        ) from exc

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
