import os
import json
from google import genai
from google.genai import types

def generate_learning_materials(pdf_path: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Upload the file
    uploaded_file = client.files.upload(file=pdf_path)
    
    prompt = """
      generate a friendly UI with all the notes, formulas, and practice questions.
      it should be easy to navigate and understand.
      use markdown for formatting.
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
