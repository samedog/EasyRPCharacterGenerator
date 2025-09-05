import json
import base64
from PIL import Image

def read_data(image: Image.Image):
    """
    Extracts character data from a PNG image (from the 'data' block).
    Returns: [name, description, personality, scenario, first_mes, mes_example]
    """
    try:
        metadata = image.info.copy()
        if hasattr(image, "text"):
            metadata.update(image.text)

        # Try to decode from "chara" or "ccv3"
        for key in ["chara", "ccv3"]:
            if key in metadata:
                try:
                    decoded_json = base64.b64decode(metadata[key]).decode("utf-8", errors="ignore")
                    data = json.loads(decoded_json)
                    break
                except Exception as e:
                    return [f"❌ Failed to decode JSON: {e}"] + [""] * 5
        else:
            return ["⚠️ No chara/ccv3 data found in image metadata."] + [""] * 5

        inner = data.get("data", {})
        
        if inner.get("name") == None:
            inner = data
            #print(inner.get("first_mes", ""))
            
        return [
            inner.get("name", ""),
            inner.get("description", ""),
            inner.get("personality", ""),
            inner.get("scenario", "")+"\n\n---\n\n"+inner.get("first_mes", ""),
            inner.get("mes_example", "")
        ]

    except Exception as e:
        return [f"❌ Unexpected error: {e}"] + [""] * 5
