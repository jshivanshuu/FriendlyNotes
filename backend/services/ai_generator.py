"""
AI generation service for FriendlyNotes.

Uses the Google Gemini 2.5 Flash model with a strict JSON response schema
to reliably convert PDF content into structured study materials.
"""

import json
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response schema — enforces the exact JSON shape Gemini must return.
# This eliminates unpredictable AI output from ever reaching the frontend.
# ---------------------------------------------------------------------------

_FORMULA_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    description="A single formula or equation found in the document.",
    properties={
        "name": types.Schema(
            type=types.Type.STRING,
            description="Short name or label for the formula (e.g. 'Newton's Second Law').",
        ),
        "equation": types.Schema(
            type=types.Type.STRING,
            description="The formula itself, written in plain text or LaTeX notation.",
        ),
        "description": types.Schema(
            type=types.Type.STRING,
            description="A plain-English explanation of what the formula means and when to use it.",
        ),
    },
    required=["name", "equation", "description"],
)

_QUESTION_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    description="A practice question with its answer.",
    properties={
        "question": types.Schema(
            type=types.Type.STRING,
            description="A clear, specific practice question based on the topic content.",
        ),
        "answer": types.Schema(
            type=types.Type.STRING,
            description="A thorough, step-by-step answer to the practice question.",
        ),
    },
    required=["question", "answer"],
)

_TOPIC_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    description="A major topic or section from the document.",
    properties={
        "title": types.Schema(
            type=types.Type.STRING,
            description="The topic or section title.",
        ),
        "notes": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.STRING,
                description="A single concise note or key concept bullet point.",
            ),
            description="List of key notes, concepts, and takeaways for this topic.",
        ),
        "formulas": types.Schema(
            type=types.Type.ARRAY,
            items=_FORMULA_SCHEMA,
            description="All formulas and equations that belong to this topic. Empty list if none.",
        ),
        "questions": types.Schema(
            type=types.Type.ARRAY,
            items=_QUESTION_SCHEMA,
            description="Practice questions (with answers) to test understanding of this topic.",
        ),
    },
    required=["title", "notes", "formulas", "questions"],
)

RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    description="Root response object containing all extracted topics.",
    properties={
        "topics": types.Schema(
            type=types.Type.ARRAY,
            items=_TOPIC_SCHEMA,
            description="Ordered list of topics extracted from the document.",
        ),
    },
    required=["topics"],
)

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_PROMPT = """\
You are an expert study-material generator. Carefully read the entire PDF document
and extract ALL learning content, covering every major topic or section.

For each topic:
1. **Notes** — Write concise, factual bullet points covering every key concept,
   definition, and important idea. Be comprehensive; do not skip anything important.
2. **Formulas** — List every formula, equation, or mathematical expression,
   giving it a clear name and a plain-English description of what it means
   and when it is used. If there are no formulas, return an empty list.
3. **Practice Questions** — Write 3-5 challenging questions per topic that test
   deep understanding, not just memorisation. Provide detailed, step-by-step
   answers. If the topic has no testable content, return an empty list.

Cover the document thoroughly. Return ONLY the structured JSON — no extra commentary.
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Gemini request timeout in milliseconds (2 minutes)
_TIMEOUT_MS = 120_000


def generate_learning_materials(pdf_path: str, api_key: str) -> dict:
    """
    Upload *pdf_path* to the Gemini Files API, generate structured study
    materials using a strict JSON schema, clean up the remote file, and
    return the parsed dict.

    Raises:
        ValueError: if the AI response cannot be decoded as valid JSON.
        TimeoutError: re-raised as-is so the caller can map it to HTTP 504.
        Exception: any other Gemini / network error.
    """
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=_TIMEOUT_MS),
    )

    uploaded_file = None
    try:
        logger.info("Uploading PDF to Gemini Files API…")
        uploaded_file = client.files.upload(file=pdf_path)

        logger.info("Requesting content generation from gemini-2.5-flash…")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, _PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.2,
            ),
        )

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The AI returned a response that could not be parsed as JSON. "
                "Please try again."
            ) from exc

        # Sanity-check the top-level key even though the schema should enforce it.
        if "topics" not in result or not isinstance(result["topics"], list):
            raise ValueError(
                "Unexpected response structure from AI: 'topics' key is missing."
            )

        return result

    finally:
        # Always attempt to delete the uploaded file from Gemini storage.
        if uploaded_file:
            try:
                client.files.delete(name=uploaded_file.name)
                logger.info("Deleted remote file '%s' from Gemini storage.", uploaded_file.name)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not delete remote Gemini file: %s", exc)
