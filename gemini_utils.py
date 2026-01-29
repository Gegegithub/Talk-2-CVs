import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

EMBED_MODEL = "models/text-embedding-004"

def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text
    )
    return result['embedding']

def caption_image(path: str) -> str:
    model = genai.GenerativeModel("gemini-flash-latest")
    img = Image.open(path)
    response = model.generate_content([
        "Décris clairement cette image en 2-3 phrases utiles pour la recherche.",
        img
    ])
    return response.text.strip()
