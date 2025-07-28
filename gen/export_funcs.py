## JSON TEMPLATE:
##
##{
##    "spec": "chara_card_v3",
##    "spec_version": "3.0"
##    "name": {name},                                         ## can be extracted from {persona} -> "Full Name:"
##    "description": "{description}\n\n{background}",         ## dvidide {persona} -> description --- background
##    "personality": {personality},                           ## can be extracted from {persona} -> "Personality:",maybe remove it from the {persona} varaible?
##    "scenario": {scenario},                                 ## {setting} -> scenario --- first_message
##    "first_mes": {first_mesage},                            ## {setting} -> scenario --- first_message
##    "mes_example": "",
##    "data": {
##        "name": {name},
##        "description": "{description}\n\n{background}",
##        "personality": {personality},
##        "scenario": {scenario},
##        "first_mes": {first_message},
##        "mes_example": "",
##        "tags": {tags}, ## ["tag1", "tag2", "etc"]
##        "avatar": "none",
##        "alternate_greetings": [],
##        {char_book}
##        "extensions": {
##            "fav": false,
##            "talkativeness": "0.5",
##            "world": {world_name}, ## only if charbook is present, else "world": ""
##            "depth_prompt": {
##                "prompt": "",
##                "depth": 4,
##                "role": "system"
##            }
##        },
##        "creator_notes": "",
##        "system_prompt": "",
##        "post_history_instructions": "",
##        "creator": "",
##        "character_version": "",
##        "group_only_greetings": []
##    },
##    "avatar": "none",
##    "tags": [],
##    "spec": "chara_card_v3",
##    "spec_version": "3.0",
##    "fav": false, ## irrelevant
##    "create_date": {creationdate}, ##format "2025-6-17 @02h 00m 18s 763ms"
##    "creatorcomment": "",
##    "talkativeness": "0.5"
##}

## SOON(tm)
## {char_book}:
##    "character_book": {
##            "name": {world_name},                           ## maybe use the char's name, like "{name}'s lorebook"
##            "entries": [
##                {
##                    "id": {id},                             ## incremental
##                    "keys": [],                             ## keys for the lorebook to trigger
##                    "secondary_keys": [],                   ## additional keywords, support logic operation (AND, OR, ANY, ALL)
##                    "comment": "",                          ## pseudoname
##                    "content": "",                          ## content of the lorebook
##                    "constant": false,                      ## The entry would always be present in the prompt.
##                    "selective": true,                      ## The entry will be triggered only in the presence of the keyword.
##                    "insertion_order": 100,
##                    "enabled": true,
##                    "position": "before_char",
##                    "use_regex": true,
##                    "extensions": {
##                        "position": 0,
##                        "exclude_recursion": false,         ## avoid trigering by other lorebooks
##                        "display_index": 0,
##                        "probability": 100,
##                        "useProbability": true,
##                        "depth": 4,
##                        "selectiveLogic": 0,
##                        "group": "",
##                        "group_override": false,
##                        "group_weight": 100,
##                        "prevent_recursion": false,         ## wont trigger recursion for other lorebooks
##                        "delay_until_recursion": false,
##                        "scan_depth": null,
##                        "match_whole_words": null,
##                        "use_group_scoring": false,
##                        "case_sensitive": null,
##                        "automation_id": "",
##                        "role": 0,
##                        "vectorized": false,
##                        "sticky": 0,
##                        "cooldown": 0,
##                        "delay": 0,
##                        "match_persona_description": false,
##                        "match_character_description": false,
##                        "match_character_personality": false,
##                        "match_character_depth_prompt": false,
##                        "match_scenario": false,
##                        "match_creator_notes": false,
##                        "triggers": []
##                    }
##                },
##                
##            ],



from PIL import Image, PngImagePlugin
from datetime import datetime
from io import BytesIO
import json
import base64

def character_exporter_png(persona: str, setting: str, image: Image.Image) -> BytesIO:
    ## persona and settinfgs are strings of text, separated by "---"
    persona_parts = persona.strip().split('---')
    if len(persona_parts) != 2:
        raise ValueError("Persona must be split by '---' into description and background.")
    persona_meta = persona_parts[0].strip()
    background = persona_parts[1].strip()

    # persona fields
    persona_data = {}
    for line in persona_meta.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            persona_data[key.strip()] = value.strip()

    name = persona_data.get("Full Name", "Unknown")
    personality = persona_data.get("Personality", "Unknown")


    setting_parts = setting.strip().split('---')
    if len(setting_parts) != 2:
        raise ValueError("Setting must be split by '---' into scenario and first message.")
    scenario = setting_parts[0].strip()
    first_message = setting_parts[1].strip()


    tags = list(filter(None, [
        persona_data.get("Race", ""),
        persona_data.get("Occupation", ""),
        persona_data.get("Gender", ""),
        persona_data.get("Nationality", "")
    ]))

    # Date
    now = datetime.now()
    create_date = f"{now.year}-{now.month}-{now.day} @{now.hour:02d}h {now.minute:02d}m {now.second:02d}s {now.microsecond // 1000}ms"

    # Build JSON structure
    card_json = {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "name": name,
        "description": f"{persona_meta}\n\n{background}",
        "personality": personality,
        "scenario": scenario,
        "first_mes": first_message,
        "mes_example": "",
        "data": {
            "name": name,
            "description": f"{persona_meta}\n\n{background}",
            "personality": personality,
            "scenario": scenario,
            "first_mes": first_message,
            "mes_example": "",
            "tags": tags,
            "avatar": "none",
            "alternate_greetings": [],
            "extensions": {
                "fav": False,
                "talkativeness": "0.5",
                "world": "",
                "depth_prompt": {
                    "prompt": "",
                    "depth": 4,
                    "role": "system"
                }
            },
            "creator_notes": "",
            "system_prompt": "",
            "post_history_instructions": "",
            "creator": "",
            "character_version": "",
            "group_only_greetings": []
        },
        "avatar": "none",
        "tags": tags,
        "fav": False,
        "create_date": create_date,
        "creatorcomment": "",
        "talkativeness": "0.5"
    }

    #print(card_json)

    # Embed JSON into PNG metadata
    meta = PngImagePlugin.PngInfo()
    json_str = json.dumps(card_json, ensure_ascii=False, separators=(',', ':'))
    
    try:
        json.loads(json_str)  # Validate it parses correctly
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        
    json_b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    meta.add_text("chara", json_b64)
    meta.add_text("ccv3", json_b64)

    # Save image to memory
    output = BytesIO()
    image.save(output, format="PNG", pnginfo=meta)
    output.seek(0)
    return [output, name]

