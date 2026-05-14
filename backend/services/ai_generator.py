import os
import json
from google import genai
from google.genai import types

def generate_learning_materials(pdf_path: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Upload the file
    uploaded_file = client.files.upload(file=pdf_path)
    
    prompt = """
    You are an expert tutor. I have uploaded a PDF document containing notes.
    Analyze the document and generate a structured JSON response containing learning materials designed for quick exam cramming.
    Extract the main topics, and for each topic, provide:
    1. A short, summarized set of notes (key takeaways).
    2. Any important formulas, equations, or rules mentioned.
    3. A few practice questions (with answers) to test knowledge.

    Return valid JSON conforming exactly to this structure:
    {
      "topics": [
        {
          "title": "Topic Name",
          "notes": ["Point 1", "Point 2"],
          "formulas": [{"name": "Formula Name", "equation": "E=mc^2", "description": "Energy-mass equivalence"}],
          "questions": [{"question": "What is...", "answer": "It is..."}]
        }
      ]
    }
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    
    # Delete the file from Gemini storage to clean up
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception as e:
        print(f"Warning: Failed to delete uploaded file from Gemini API: {e}")
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        raise Exception("Failed to parse AI response as JSON")
