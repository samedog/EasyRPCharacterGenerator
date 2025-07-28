#textgen.py
import requests
import re
import json
import random
import time

from .helpers import sort_persona_json, query_llm
## pollinations

def generate_name_pollinations(tags, gender, retries=5):
    time.sleep(3)
    try:
        seed = random.randint(100000, 999999)
        system_msg = f"You are a character name generator. Output exactly one randomly generated Western-style name (based off this int seed: {seed}) (2–4 words)."
        user_msg = f"Topic: {tags} | Gender: {gender}\nGenerate a single character name."
        prompt = f"{system_msg} {user_msg}"
        encoded_prompt = requests.utils.quote(prompt)

        for attempt in range(retries):
            try:
                full_url = f"https://text.pollinations.ai/prompt/{encoded_prompt}?private=true"
                response = requests.get(full_url, timeout=10)
                if response.status_code > 200:
                    continue
                response.raise_for_status()

                lines = response.text.strip().split('\n')
                if lines:
                    candidate = lines[0].strip()
                    # Retry if unwanted characters are found
                    if any(c in candidate for c in "({["):
                        print(f"Retrying due to invalid characters in: {candidate}")
                        continue
                    return candidate
            except requests.RequestException:
                continue  # retry on network-related errors

            time.sleep(5)

        return "Error: Could not generate name."

    except Exception as e:
        return 

def generate_persona_pollinations(name, tags, gender, retries=5):
    time.sleep(3)
    if not name:
        return "Generate a name first."

    try:
        system_msg = (
            "You are a character-profile generator. "
            "Output ONLY a valid JSON object with EXACTLY the following keys (no extras): "
            "[Full Name, Age, Race, Gender, Nationality, Occupation, Height, Intelligence, Personality, Likes, Dislikes, "
            "Hobbies, Appearance, Breasts, Outfit, Underwear, Speech pattern, Sexuality, Libido, Fears, Goals, "
            "Sexual experience, Obedience rating, Enjoys during sex]. "
            "Do NOT add any explanations, comments, or text outside the JSON. "
            "Make sure the JSON is syntactically valid."
        )

        user_msg = (
            f"Fill the JSON fields creatively for the character with this information:\n"
            f"Name: {name}\n"
            f"Themes/Tags: {tags}\n"
            f"Gender: {gender}"
        )

        prompt = f"{system_msg} {user_msg}"
        encoded_prompt = requests.utils.quote(prompt)

        expected_keys = {
            "Full Name", "Age", "Race", "Gender", "Occupation", "Personality", "Appearance",
            "Likes", "Dislikes", "Outfit", "Speech pattern", "Fears", "Goals"
        }

        for attempt in range(retries):
            try:
                full_url = f"https://text.pollinations.ai/prompt/{encoded_prompt}?private=true"
                response = requests.get(full_url, timeout=10)
                #print(response)
                if response.status_code > 200:
                    continue
                response.raise_for_status()

                raw = response.text.strip()
                raw = re.sub(r"^```json\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

                try:
                    persona_json = json.loads(raw)
                    if not expected_keys.issubset(persona_json.keys()):
                        continue

                    persona_json = sort_persona_json(persona_json)
                    lines = []
                    for key, val in persona_json.items():
                        if isinstance(val, list):
                            val = ", ".join(str(item) for item in val)
                        lines.append(f"{key}: {val}")
                    return "\n".join(lines)

                except json.JSONDecodeError:
                    continue

            except requests.RequestException:
                continue
            time.sleep(5)

        return "Error: Could not generate valid JSON persona."

    except Exception as e:
        return f"Pollinations error: {str(e)}"


def generate_background_pollinations(tags, persona, retries=5):
    time.sleep(3)
    if not tags or not persona:
        return "Missing required fields."

    # Convert persona to string if needed, and extract name
    if isinstance(persona, dict):
        name = persona.get("Full Name", "The character")
        persona_text = json.dumps(persona, ensure_ascii=False)
    else:
        persona_text = str(persona)
        match = re.search(r"Full Name:\s*(.+)", persona_text)
        name = match.group(1).strip() if match else "The character"

    try:
        system_msg = (
            "You are a creative writer. Generate a short, vivid background "
            "paragraph for a fictional character. Do not include explanations or extra text."
        )

        user_msg = (
            f"Character: {name}\n"
            f"Themes: {tags}\n"
            f"Persona:\n{persona_text}\n"
            f"Write a single-paragraph character backstory. If no themes are provided, infer them from the character traits (e.g., sci-fi, fantasy, romance, domination, etc.)."
        )

        prompt = f"{system_msg}\n{user_msg}"
        encoded_prompt = requests.utils.quote(prompt)

        for attempt in range(retries):
            try:
                full_url = f"https://text.pollinations.ai/prompt/{encoded_prompt}?private=true"
                response = requests.get(full_url, timeout=10)
                if response.status_code > 200:
                    continue
                response.raise_for_status()

                background = response.text.strip()
                if background and len(background.split()) > 2:
                    return background
            except requests.RequestException:
                continue
            time.sleep(5)
        return "Error: Could not generate background."

    except Exception as e:
        return f"Pollinations error: {str(e)}"
        
def generate_setting_pollinations(persona, tags, retries=5):
    time.sleep(3)
    if not persona:
        return "Missing required fields."
    try:
        system_msg = (
            "You are a creative writer. Generate a short, vivid background "
            "paragraph for a fictional character. Do not include explanations or extra text."
        )

        # Generate the user message for the prompt
        user_msg = (
            "Based on the following character information, create a short (max 100 words), vivid and general setting "
            "that describes why the character and the user are together in a roleplay scenario. "
            "Avoid specific locations like bedrooms, bars, or offices. Do not include any permanent or restrictive elements. "
            "Make the setting flexible and imaginative. It is important to never assume the user's gender. "
            "Refer to the user in gender neutral way. "
            "If no tags are provided infer the genre and other tags from the character persona and background. "
            "It's mandatory to refer to the user as {{user}}. "
            "Here are the details:\n\n"
            f"Character Persona and background:\n{persona}\n\n"
            f"Tags (if any):\n{tags}"
        )

        prompt = f"{system_msg}\n{user_msg}"
        encoded_prompt = requests.utils.quote(prompt)

        for attempt in range(retries):
            try:
                full_url = f"https://text.pollinations.ai/prompt/{encoded_prompt}?private=true"
                response = requests.get(full_url, timeout=10)
                if response.status_code > 200:
                    continue
                response.raise_for_status()

                result = response.text.strip()
                if result and len(result.split()) > 2:
                    return result
            except requests.RequestException:
                continue
            time.sleep(5)

        return "Error: Could not generate background."

    except Exception as e:
        return f"Pollinations error: {str(e)}"

def generate_first_message_pollinations(persona, setting, tags=None, retries=5):
    time.sleep(3)
    if not persona or not setting:
        return "Missing required fields."
    try:
        system_msg = (
            "You are a creative writer. Generate a short, vivid first interaction "
            "paragraph for a fictional character and the user in a roleplay. Do not include explanations or extra text."
        )

        user_msg = (
            "Based on the following character information, create a vivid first interaction between the character and the user "
            "(max 400 words) that describes a roleplay scene. "
            "Dialogue should be in straight double quotes. All actions, expressions, and physical gestures MUST be enclosed in "
            "single asterisks (e.g., *smiles* or *walks closer*). Use this formatting consistently throughout the interaction. "
            "Do NOT omit the asterisks under any circumstances except for the Dialogue. write at least 2 parragraphs. "
            "It's mandatory to refer to the user as {{user}}. "
            "Here are the details (Do not include any of these fields entirely into the first message, just use them as reference and inspiration):\n\n"
            f"Character Persona and background:\n{persona}\n\n"
            f"Tags (if any):\n{tags or 'Infer from persona and background'}\n\n"
            f"Setting:\n{setting}"
        )

        prompt = f"{system_msg}\n{user_msg}"
        encoded_prompt = requests.utils.quote(prompt)

        for attempt in range(retries):
            try:
                full_url = f"https://text.pollinations.ai/prompt/{encoded_prompt}?private=true"
                response = requests.get(full_url, timeout=10)
                if response.status_code > 200:
                    continue
                response.raise_for_status()

                result = response.text.strip()
                #print(result)               
                if result and len(result.split()) > 2:
                    return result
            except requests.RequestException:
                continue
            time.sleep(5)

        return "Error: Could not generate first interaction."

    except Exception as e:
        return f"Pollinations error: {str(e)}"
        
## OpenAI

def generate_name(tags, gender, api_url, model="default", api_key=None, retries=5):
    time.sleep(3)
    #print("generating opename")
    system_msg = "You are a character name generator. Output exactly one randomly generated Western-style name (2–4 words)."
    user_msg = f"Topic: {tags} | Gender: {gender}\nGenerate a single character name."

    for _ in range(retries):
        resp = query_llm(system_msg, user_msg, api_url, api_key, max_tokens=24)
        lines = [line.strip() for line in resp.splitlines() if line.strip()]
        if lines:
            return lines[0]
    return "Error: Could not generate name."


def generate_persona(name, tags, gender, api_url, api_key=None, retries=5):
    time.sleep(2)
    if not name:
        return "Generate a name first."

    system_msg = (
        "You are a character-profile generator. "
        "Output ONLY a valid JSON object with EXACTLY the following keys (no extras): "
        "[Full Name, Age, Race, Gender, Nationality, Occupation, Height, Intelligence, Personality, Likes, Dislikes, "
        "Hobbies, Appearance, Breasts, Outfit, Underwear, Speech pattern, Sexuality, Libido, Fears, Goals, "
        "Sexual experience, Obedience rating, Enjoys during sex]. "
        "Do NOT add any explanations, comments, or text outside the JSON. "
        "Make sure the JSON is syntactically valid."
    )

    user_msg = (
        f"Fill the JSON fields for the character with this information:\n"
        f"Name: {name}\n"
        f"Themes/Tags: {tags}\n"
        f"Gender: {gender}"
    )
    
    expected_keys = {
        "Full Name", "Age", "Race", "Gender", "Occupation", "Personality", "Appearance", "Likes", "Dislikes", "Outfit", "Speech pattern", "Fears", "Goals"
        }

    
    for _ in range(retries):
        raw = query_llm(system_msg, user_msg, api_url, api_key, max_tokens=2048)
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            persona_json = json.loads(raw)

#            if set(persona_json.keys()) == set(expected_keys):
            if not expected_keys.issubset(persona_json.keys()):
                continue 
            persona_json = sort_persona_json(persona_json)
            lines = []
            for key, val in persona_json.items():
                #val = persona_json[key]
                if isinstance(val, list):
                    val = ", ".join(str(item) for item in val)
                lines.append(f"{key}: {val}")
            return "\n".join(lines)
        except json.JSONDecodeError:
            continue
        time.sleep(5)
    return "Error: Could not generate valid JSON persona."


def generate_background(tags, persona, api_url, api_key=None, retries=5):
    time.sleep(3)
    if not persona:
        return "Missing required fields."

    # Convert persona to string if needed, and extract name
    if isinstance(persona, dict):
        name = persona.get("Full Name", "The character")
        persona_text = json.dumps(persona, ensure_ascii=False)
    else:
        persona_text = str(persona)
        # Try to extract name from plain-text persona using regex
        match = re.search(r"Full Name:\s*(.+)", persona_text)
        name = match.group(1).strip() if match else "The character"

    system_msg = (
        "You are a creative writer. Generate a short, vivid background paragraph "
        "for a fictional character. Limit to one paragraph."
    )

    user_msg = (
        f"Character: {name}\n"
        f"Themes: {tags}\n"
        f"Persona:\n{persona_text}\n"
        f"Write a single-paragraph character backstory. If no themes are provided, infer them from the character traits (e.g., sci-fi, fantasy, romance, domination, etc.)."
    )

    last_exception = None
    for _ in range(retries):
        try:
            response = query_llm(system_msg, user_msg, api_url, api_key, max_tokens=2048)
            if response and len(response.split()) > 2:
                return response
        except Exception as e:
            last_exception = e
        time.sleep(3)

    return f"Error generating background: {str(last_exception) if last_exception else 'Unknown error'}"
    
    
def generate_setting(persona, tags, api_url, api_key=None, retries=5):
    time.sleep(3)
    if not persona:
        return "Missing required fields."

    system_msg = (
        "You are a creative writer. Generate a short, vivid setting "
        "paragraph for a fictional roleplay. Do not include explanations or extra text."
    )

    user_msg = (
        "Based on the following character information, create a short (max 100 words), vivid and general setting "
        "that describes why the character and the user are together in a roleplay scenario. "
        "Avoid specific locations like bedrooms, bars, or offices. Do not include any permanent or restrictive elements. "
        "Make the setting flexible and imaginative. It is important to never assume the user's gender. "
        "Refer to the user in gender neutral way. "
        "If no tags are provided infer the genre and other tags from the character persona and background. "
        "It's mandatory to refer to the user as {{user}}. "
        "Here are the details (Do not include any of these fields entirely into the first message, just use them as reference and inspiration):\n\n"
        f"Character Persona and background:\n{persona}\n\n"
        f"Tags (if any):\n{tags}"
    )

    last_exception = None
    for _ in range(retries):
        try:
            response = query_llm(system_msg, user_msg, api_url, api_key, max_tokens=2048)
            if response and len(response.split()) > 2:
                return response.strip()
        except Exception as e:
            last_exception = e
        time.sleep(5)

    return f"Error generating setting: {str(last_exception) if last_exception else 'Unknown error'}"

def generate_first_message(persona, setting, tags=None, api_url=None, api_key=None, retries=5):
    time.sleep(3)
    if not persona or not setting:
        return "Missing required fields."

    system_msg = (
        "You are a creative writer. Generate a short, vivid first interaction "
        "paragraph for a fictional character and the user in a roleplay. Do not include explanations or extra text."
    )

    user_msg = (
            "Based on the following character information, create a vivid first interaction between the character and the user "
            "(max 400 words) that describes a roleplay scene. "
            "Dialogue should be in straight double quotes. All actions, expressions, and physical gestures MUST be enclosed in "
            "single asterisks (e.g., *smiles* or *walks closer*). Use this formatting consistently throughout the interaction. "
            "Do NOT omit the asterisks under any circumstances except for the Dialogue. write at least 2 parragraphs. "
            "It's mandatory to refer to the user as {{user}}. "
            "Here are the details:\n\n"
            f"Character Persona and background:\n{persona}\n\n"
            f"Tags (if any):\n{tags or 'Infer from persona and background'}\n\n"
            f"Setting:\n{setting}"
        )

    last_exception = None
    for _ in range(retries):
        try:
            response = query_llm(system_msg, user_msg, api_url, api_key, max_tokens=2048)
            #print(response)
            if response and len(response.split()) > 2:
                return response.strip()
                
        except Exception as e:
            last_exception = e
        time.sleep(5)

    return f"Error generating first interaction: {str(last_exception) if last_exception else 'Unknown error'}"


