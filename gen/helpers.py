#helpers.py
import requests
import re

## stable diffusion
def check_api_online(url):
    try:
        response = requests.get(f"{url}/sdapi/v1/sd-models")
        if response.status_code == 200:
            return "API is online and reachable."
        return f"Error: Received status code {response.status_code}."
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to reach the API. {str(e)}"

def fetch_models(api_url, api_key=None):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        response = requests.get(f"{api_url}/models", headers=headers)
        response.raise_for_status()
        data = response.json().get("data", [])
        models = [m["id"] for m in data if "id" in m]
        return models if models else ["default"]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return ["default"]

## LLM
def check_llm_api_online(api_url, api_key=None):
    """Returns (status_message, list_of_models)"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.get(f"{api_url}/models", headers=headers)

        if response.status_code == 200:
            models = [m["id"] for m in response.json().get("data", []) if "id" in m]
            return "LLM API is online and reachable.", models or ["default"]
        return f"Error: Status code {response.status_code}.", ["default"]
    except requests.RequestException as e:
        return f"Error: {str(e)}", ["default"]

def query_llm(system_prompt, user_prompt, api_url, api_key=None, model="openai", max_tokens=1024, stop=None, timeout=10):
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8,
        "top_p": 0.9,
        "stop": stop
    }

    try:
        response = requests.post(
            f"{api_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        return None  # Or return f"Error: {e}" if you want error detail
## general functions


def generate_prompt_from_persona(persona):
    if not persona:
        return "Error: No persona available to generate an image prompt."

    if isinstance(persona, dict):
        appearance_text = persona.get("Appearance", "A mysterious character with striking features.")
        outfit_text = persona.get("Outfit", "Wearing a unique, stylish outfit.")
    else:
        # Extract lines safely
        lines = persona.split("\n")
        race = next((line.split(":", 1)[1].strip() for line in lines if "Race:" in line), "")
        gender = next((line.split(":", 1)[1].strip() for line in lines if "Gender:" in line), "")
        appearance = next((line.split(":", 1)[1].strip() for line in lines if "Appearance:" in line), "")
        breasts = next((line.split(":", 1)[1].strip() for line in lines if "Breasts:" in line), "")
        outfit = next((line.split(":", 1)[1].strip() for line in lines if "Outfit:" in line), "")
        underwear = next((line.split(":", 1)[1].strip() for line in lines if "Underwear:" in line), "")

        # Graceful fallback logic
        appearance_parts = [part for part in [appearance, breasts] if part]
        outfit_parts = [part for part in [outfit, underwear] if part]

        appearance_text = ", ".join(appearance_parts) if appearance_parts else "A mysterious character with striking features."
        outfit_text = ", ".join(outfit_parts) if outfit_parts else "Wearing a unique, stylish outfit."

    prompt = f"score_9, score_8_up, score_7_up, {race}, {gender}, {appearance_text}, {outfit_text}, highly detailed, perfect face"
    return re.sub(r'[<>]', '', prompt)

def sort_persona_json(persona_json):
    key_order = [
        "Full Name", "Age", "Race", "Gender", "Nationality", "Occupation", "Height",
        "Intelligence", "Personality", "Likes", "Dislikes", "Hobbies", "Appearance",
        "Breasts", "Outfit", "Underwear", "Speech pattern", "Sexuality", "Libido",
        "Fears", "Goals", "Sexual experience", "Obedience rating", "Enjoys during sex"
    ]

    sorted_json = {key: persona_json.get(key, "") for key in key_order}
    return sorted_json
