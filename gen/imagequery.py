#imagequery.py
import base64
import requests
import json
import re
from PIL import Image  # If not already imported
from io import BytesIO

from .helpers import sort_persona_json

def generate_persona_from_image(image, api_url, model, api_key=None, retries=3):

    if not image:
        return "Please upload an image."

    system_msg = (
        "You are a character-profile generator. "
        "Output ONLY a valid JSON object with EXACTLY the following keys (no extras): "
        "[Full Name, Age, Race, Gender, Nationality, Occupation, Height, Intelligence, Personality, Likes, Dislikes, "
        "Hobbies, Appearance, Breasts, Outfit, Underwear, Speech pattern, Sexuality, Libido, Fears, Goals, "
        "Sexual experience, Obedience rating, Enjoys during sex]. "
        "You may infer or create details based on the visual input. "
        "Do NOT add any explanations, comments, or text outside the JSON. "
        f"Make sure the JSON is syntactically valid."
    )

    expected_keys = {
        "Full Name", "Age", "Race", "Gender", "Nationality", "Occupation", "Height", "Intelligence", "Personality",
        "Likes", "Dislikes", "Hobbies", "Appearance", "Breasts", "Outfit", "Underwear", "Speech pattern",
        "Sexuality", "Libido", "Fears", "Goals", "Sexual experience", "Obedience rating", "Enjoys during sex"
    }

    # Determine image format
    format_map = {
        "JPEG": "jpeg",
        "JPG": "jpeg",
        "PNG": "png",
        "BMP": "bmp"
    }
    img_format = image.format.upper() if image.format else "PNG"
    img_format = format_map.get(img_format, "png")  # fallback to png

    # Encode image to base64
    buffered = BytesIO()
    image.save(buffered, format=img_format.upper())
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    user_msg = [
        {"type": "text", "text": "Describe this character as if they were a fictional persona in detail using JSON."},
        {"type": "image_url", "image_url": {"url": f"data:image/{img_format};base64,{img_str}"}}
    ]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "max_tokens": 2048
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    for _ in range(retries):
        try:
            response = requests.post(f"{api_url}/chat/completions", json=payload, headers=headers, timeout=30)
            raw = response.json()["choices"][0]["message"]["content"]

            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            persona_json = json.loads(raw)

            print("Returned keys:", set(persona_json.keys()))
            print("Missing keys:", expected_keys - set(persona_json.keys()))
            print("Extra keys:", set(persona_json.keys()) - expected_keys)

            if not expected_keys.issubset(persona_json.keys()):
                continue

            persona_json = sort_persona_json(persona_json)
            lines = []
            for key, val in persona_json.items():
                if isinstance(val, list):
                    val = ", ".join(str(item) for item in val)
                lines.append(f"{key}: {val}")
            return "\n".join(lines)

        except Exception:
            continue

    return "Error: Could not generate valid JSON persona from image."

    
