# imagegen.py
import requests
import base64
from io import BytesIO
from PIL import Image

def generate_image_with_pollinations(prompt, width, height, seed=1, model=None, style=None):
    try:
        # ✅ Inject style into the prompt BEFORE encoding
        style_map = {
            "🎌 Anime": "anime style",
            "📷 Realistic": "realistic",
            "🖌️ Cartoon": "cartoon style"
        }

        if style:
            style_suffix = style_map.get(style)
            if style_suffix:
                prompt = f"{prompt}, {style_suffix}"

        # ✅ Encode the full modified prompt
        encoded_prompt = requests.utils.quote(prompt)

        params = []
        if seed:
            params.append(f"seed={seed}")
        if model:
            params.append(f"model={model}")
        if width:
            params.append(f"width={width}")
        if height:
            params.append(f"height={height}")

        query_string = "?" + "&".join(params) if params else ""
        full_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}{query_string}"

        #print("full url is:", full_url)

        response = requests.get(full_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image

    except Exception as e:
        return f"Pollinations error: {str(e)}"

        
def generate_image_with_api(prompt, api_url, width, height, user_negative_prompt="", seed=-1, steps=50, cfg_scale=7.5):
#def generate_image_with_api(prompt, api_url, user_negative_prompt="", seed=-1):
    base_negative_prompt = (
        "(worst quality), (low quality), (normal quality), lowres, monochrome, grayscale..."
    )
    negative_prompt = f"{base_negative_prompt}, {user_negative_prompt}" if user_negative_prompt else base_negative_prompt

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "seed": seed if seed is not None else -1
    }

    try:
        api = api_url
        response = requests.post(f"{api}/sdapi/v1/txt2img", json=payload)
        if response.status_code == 200:
            result = response.json()
            if "images" in result and result["images"]:
                base64_image = result["images"][0]
                image_bytes = base64.b64decode(base64_image)
                return Image.open(BytesIO(image_bytes))
            return "Error: No image data received from API."
        return f"Error: Failed to generate image. Response code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

