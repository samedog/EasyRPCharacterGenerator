# gen/__init__.py
# Optional: expose key functions directly from the package
from .textgen import (
    generate_name,
    generate_persona,
    generate_background,
    generate_setting,
    generate_first_message,
    generate_name_pollinations, 
    generate_persona_pollinations, 
    generate_background_pollinations,
    generate_setting_pollinations,
    generate_first_message_pollinations
)
from .imagegen import (
    generate_image_with_api,
    generate_image_with_pollinations,
)

from .imagequery import(
    generate_persona_from_image
)

from .helpers import(
    check_api_online,
    check_llm_api_online,
    fetch_models, 
    query_llm,
    generate_prompt_from_persona,
    sort_persona_json
)

from .export_funcs import(
    character_exporter_png
)
