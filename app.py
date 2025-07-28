import gradio as gr
import random
from PIL import Image
import tempfile
import os
import shutil

from gen import (
    ##textgen.py
    generate_name, generate_persona, generate_background, generate_setting, generate_first_message,
    generate_name_pollinations, generate_persona_pollinations, generate_background_pollinations,
    generate_setting_pollinations, generate_first_message_pollinations,
    ##imagegen.py
    generate_image_with_api, generate_image_with_pollinations,
    ##imagequery.py
    generate_persona_from_image,
    ##helpers.py
    check_api_online, check_llm_api_online, query_llm,fetch_models, generate_prompt_from_persona,
    sort_persona_json,
    #export_funcs.py
    character_exporter_png
)
    
DEFAULT_SEED = random.randint(100000, 999999)

def refresh_model_choices(api_url):
    return gr.update(choices=fetch_models(api_url), value="default")

def handle_llm_check(api_url):
    status, models = check_llm_api_online(api_url)
    return status, gr.update(choices=models, value=models[0] if models else "default")


def generate_image_switch(polli_prompt, prompt, source, url, seed, model, style, negative_prompt, height, width):
    if source == "📡 Pollinations":
        img = generate_image_with_pollinations(polli_prompt, width, height, seed, model, style)
        return img
    else:
        result = generate_image_with_api(prompt, url, width, height, negative_prompt, seed)
        return result


def on_export(persona, setting, image):
    png_bytes, tmp_name = character_exporter_png(persona, setting, image)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(png_bytes.getvalue())
    tmp.flush()
    tmp.close()

    desired_path = os.path.join(os.path.dirname(tmp.name), tmp_name+".png")
    shutil.move(tmp.name, desired_path)
    
    return desired_path, gr.update(visible=True), desired_path
    
def cleanup_file(path):
    #silently clean stuff
    if path:
        if os.path.exists(path):
            os.remove(path)
            return

    
with gr.Blocks(title="Easy Character Generator 🧬",
css="""
.plain-text { font-family: monospace; white-space: pre-wrap; }
.scrollable-textbox textarea { overflow-y: auto !important; resize: vertical; }
@media (max-width: 1080px) {
    .gr-row { flex-direction: column; }
    .gr-column { width: 100% !important; }
}
.gr-button.loading::after { content: " ⏳"; }
""") as demo:
    with gr.Row():
        gr.Markdown("# 🧬 Easy Character Generator")
            
    with gr.Tab("🧬 Generate from Tags"):
        with gr.Row():
            export_file_path = gr.State()
            export_button = gr.Button(" ⏬ EXPORT ⏬ ", variant="primary", scale=1)
            download_btn = gr.DownloadButton("Download PNG", visible=False)
            download_btn.click(
                lambda path:cleanup_file(path),
                export_file_path,
                None
            )
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🧬 Persona Generator")
                with gr.Tab("## 📡 Pollinations.ai"):
                    with gr.Group():
                        gr.Markdown("This uses the simple GET pollinations textgen, for advanced generation use the OpenAI tab.")
                    pass                 
                with gr.Tab("## 🔗 OpenAI"):
                    with gr.Group():
                        gr.Markdown("### 🔧 OpenAI Settings")
                        with gr.Row():
                            llm_api_url_input = gr.Textbox(label="URL", value="", placeholder="https://text.pollinations.ai/openai", scale=1)
                            llm_api_key_input = gr.Textbox(label="API Key (Optional)", value=None, type="password", scale=1)
                        with gr.Row():
                            llm_status_output = gr.Textbox(label="API Status", interactive=False, scale=2)
                            check_llm_status_button = gr.Button("🔍 Check API Status", scale=1)
                            model_dropdown = gr.Dropdown(label="Model", choices=["default"], value="default", scale=2)
                            refresh_models_button = gr.Button("🔄 Refresh Models", scale=1)

                        check_llm_status_button.click(
                            lambda url: handle_llm_check(url),
                            [llm_api_url_input],
                            [llm_status_output, model_dropdown]
                        )
                        refresh_models_button.click(
                            lambda url: gr.update(choices=fetch_models(url), value="default"),
                            [llm_api_url_input],
                            model_dropdown
                        )
                        
                with gr.Group():
                    gr.Markdown("### 🧠 Character Inputs")
                    with gr.Row():
                        tags_input = gr.Textbox(label="Tags", scale=1)
                        gender_input = gr.Textbox(label="Gender", scale=1)
                    with gr.Row():
                        with gr.Column():
                            image_source_radio = gr.Radio(
                                label="Image Generator",
                                choices=["📡 Pollinations", "🛠️ Stable Diffusion"],
                                value="📡 Pollinations",
                                scale=1
                            )

                    with gr.Row():
                        gr.Markdown("Remember to set your Stable Diffusion settings on the right panel if needed.")
                    with gr.Row():
                        gr.Markdown("General Image Settings")
                    with gr.Row():
                        seed_input = gr.Number(label="Seed", value=DEFAULT_SEED, precision=0, scale=1)
                    with gr.Row():
                        width_input = gr.Number(label="Width", value=360, precision=0, scale=1)
                        height_input = gr.Number(label="Height", value=640, precision=0, scale=1)
                        
                with gr.Group():
                    generate_all_button = gr.Button("⚡ Generate All ⚡", variant="primary")
                    generation_status = gr.Markdown("🛑 Stopped...")  # Status feedback line
                with gr.Group():
                    gr.Markdown("### 🪪 Generated Identity")
                    with gr.Row():
                        name_output = gr.Textbox(label="Character Name", scale=4)
                        generate_name_button = gr.Button("🎲 Generate Name", scale=1)
                    with gr.Row():
                        with gr.Column():
                            generate_personabackground_button = gr.Button("🧬📜 Generate Persona and Background", scale=2)
                            with gr.Row():
                                generate_persona_button = gr.Button("🧬 Generate Persona (Failsafe)", size=1)
                                generate_background_button = gr.Button("📜 Generate Background (Failsafe)", size=1)
                            persona_output = gr.Textbox(label="Character Persona (Info and Background)", lines=12, elem_classes=["scrollable-textbox"])
                        with gr.Column():
                            generate_settingmessage_button = gr.Button("📜 Generate Setting and First Message", scale=2)
                            with gr.Row():
                                generate_setting_button = gr.Button("📜 Generate Setting (Failsafe)", size=1)
                                generate_firstmessage_button = gr.Button("📜 Generate First Message (Failsafe)", size=1)
                            roleplay_output = gr.Textbox(label="RP Setting and First Message", lines=12, elem_classes=["scrollable-textbox"])

                generate_name_button.click(
                    lambda tags, gender, url, model, api_key, llm_status: (
                        generate_name_pollinations(tags, gender) if llm_status != "✅ LLM API is online and reachable." else generate_name(tags, gender, url, model=model, api_key=api_key)
                    ),
                    [tags_input, gender_input, llm_api_url_input, model_dropdown, llm_api_key_input, llm_status_output],
                    name_output
                )
                
                generate_personabackground_button.click(
                    lambda name, tags, gender, url, api_key, llm_status: (
                        generate_persona_pollinations(name, tags, gender) if llm_status != "✅ LLM API is online and reachable." else generate_persona(name, tags, gender, url, api_key=api_key)
                    ),
                    [name_output, tags_input, gender_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    persona_output
                ).then(
                    lambda tags, persona_text, url, api_key, llm_status: (
                        persona_text + "\n\n---\n\n" +
                        (generate_background_pollinations(tags, persona_text) if llm_status != "✅ LLM API is online and reachable." else generate_background(tags, persona_text, url, api_key=api_key))
                    ),
                    [tags_input, persona_output, llm_api_url_input, llm_api_key_input, llm_status_output],
                    persona_output
                )
                
                generate_persona_button.click(
                    lambda name, tags, gender, url, api_key, llm_status: (
                        generate_persona_pollinations(name, tags, gender) if llm_status != "✅ LLM API is online and reachable." else generate_persona(name, tags, gender, url, api_key=api_key)
                    ),
                    [name_output, tags_input, gender_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    persona_output
                )
                
                generate_settingmessage_button.click(
                    lambda persona, tags, url, api_key, llm_status: (
                        generate_setting_pollinations(persona, tags) if llm_status != "✅ LLM API is online and reachable." else generate_setting(persona, tags, url, api_key=api_key)
                    ),
                    [persona_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    roleplay_output
                ).then(
                    lambda persona, setting_text, tags, url, api_key, llm_status: (
                        setting_text + "\n\n---\n\n" +
                        (generate_first_message_pollinations(persona, setting_text, tags) if llm_status != "✅ LLM API is online and reachable." else generate_first_message(persona, setting_text, tags, url, api_key=api_key))
                    ),
                    [persona_output, roleplay_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    roleplay_output
                )
                
                
                generate_background_button.click(
                    lambda tags, persona_text, url, api_key, llm_status: (
                        persona_text + "\n\n---\n\n" +
                        (generate_background_pollinations(tags, persona_text) if llm_status != "✅ LLM API is online and reachable." else generate_background(tags, persona_text, url, api_key=api_key))
                    ),
                    [tags_input, persona_output, llm_api_url_input, llm_api_key_input, llm_status_output],
                    persona_output
                )
                
                generate_setting_button.click(
                    lambda persona, tags, url, api_key, llm_status: (
                        generate_setting_pollinations(persona, tags) if llm_status != "✅ LLM API is online and reachable." else generate_setting(persona, tags, url, api_key=api_key)
                    ),
                    [persona_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    roleplay_output
                )
                
                generate_firstmessage_button.click(
                    lambda persona, setting_text, tags, url, api_key, llm_status: (
                        setting_text + "\n\n---\n\n" +
                        (generate_first_message_pollinations(persona, setting_text, tags) if llm_status != "✅ LLM API is online and reachable." else generate_first_message(persona, setting_text, tags, url, api_key=api_key))
                    ),
                    [persona_output, roleplay_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
                    roleplay_output
                )
                
            with gr.Column(scale=1):
                gr.Markdown("## 🎨 Image Generator")
                with gr.Tabs():
                    with gr.Tab("📡 Pollinations.ai"):
                        with gr.Group():
                            with gr.Row():
                                gr.Markdown("### 🖼️ Free Image Generator With Watermark (Pollinations.ai)")
                            with gr.Row():
                                image_style_radio = gr.Radio(
                                    label="Image Style",
                                    choices=["📷 Realistic", "🎌 Anime", "🖌️ Cartoon"],
                                    value="📷 Realistic",
                                )
                            with gr.Row():
                                pollinations_model_dropdown = gr.Dropdown(
                                    label="Pollinations Model",
                                    choices=["flux", "turbo", "gptimage"],
                                    value="flux",
                                )
                            with gr.Row():
                                pollinations_prompt_input = gr.Textbox(label="Prompt", placeholder="e.g. anime elf warrior princess", lines=6, elem_classes=["scrollable-textbox"])
                            with gr.Row():
                                generate_pollinations_button = gr.Button("🖼️ Generate Image", scale=1)
                                generate_pollinations_from_persona_button = gr.Button("🧠 Generate from Persona", scale=1)


                    with gr.Tab("🛠️ Stable Diffusion"):
                        with gr.Group():
                            gr.Markdown("### 🔧 API Settings")
                            with gr.Row():
                                sdapi_url_input = gr.Textbox(label="API URL", value="http://127.0.0.1:7860", scale=3)
                                check_api_button = gr.Button("🔍 Check API", scale=1)
                            api_status_output = gr.Textbox(label="Status", interactive=False)

                        with gr.Group():
                            gr.Markdown("### 🖼️ Prompt Settings")
                            prompt_input = gr.Textbox(label="Prompt", lines=4, placeholder="Describe your character...", elem_classes=["scrollable-textbox"])
                            negative_prompt_input = gr.Textbox(label="Negative Prompt (Optional)", lines=4, elem_classes=["scrollable-textbox"])
                            with gr.Row():
                                generate_image_button = gr.Button("🖼️ Generate Image", scale=1)
                                generate_from_persona_button = gr.Button("🧠 Generate from Persona", scale=1)
                    with gr.Group():
                        gr.Markdown("### 🖼️ Output Image")
                        output_image = gr.Image(label="Generated Image", type="pil", height=400, width=300)

                        generate_pollinations_button.click(
                            lambda prompt, seed, width, height, model, style: generate_image_with_pollinations(prompt, width, height, seed, model, style),
                            [pollinations_prompt_input, seed_input, width_input, height_input, pollinations_model_dropdown, image_style_radio],
                            output_image
                        )
                    
                        generate_pollinations_from_persona_button.click(
                            lambda persona: generate_prompt_from_persona(persona),
                            [persona_output],
                            pollinations_prompt_input
                        ).then(
                            lambda prompt, seed, width, height, model, style: generate_image_with_pollinations(prompt, width, height, seed, model, style),
                            [pollinations_prompt_input, seed_input, width_input, height_input, pollinations_model_dropdown, image_style_radio],
                            output_image
                        )

                        check_api_button.click(
                            lambda url: check_api_online(url),
                            [sdapi_url_input],
                            api_status_output
                        )
                        generate_image_button.click(
                            lambda prompt, negative_prompt, url, width, height, seed: generate_image_with_api(prompt, url, width, height, negative_prompt, seed),
                            [prompt_input, negative_prompt_input, sdapi_url_input, width_input, height_input, seed_input],
                            output_image
                        )
                        generate_from_persona_button.click(
                            lambda persona: generate_prompt_from_persona(persona),
                            [persona_output],
                            prompt_input
                        ).then(
                            lambda prompt, negative_prompt, url, width, height, seed: generate_image_with_api(prompt, url, width, height, negative_prompt, seed),
                            [prompt_input, negative_prompt_input, sdapi_url_input, width_input, height_input, seed_input],
                            output_image
                        )

        generate_all_button.click(
            lambda: gr.update(value="🧠 Generating Name..."),
            None,
            generation_status
        ).then(
            lambda tags, gender, url, model, api_key, llm_status: generate_name_pollinations(tags, gender) if llm_status != "✅ LLM API is online and reachable." else generate_name(tags, gender, url, model=model, api_key=api_key),
            [tags_input, gender_input, llm_api_url_input, model_dropdown, llm_api_key_input, llm_status_output],
            name_output
        ).then(
            lambda: gr.update(value="🧬 Generating Persona..."),
            None,
            generation_status
        ).then(
            lambda name, tags, gender, url, api_key, llm_status: (
                generate_persona_pollinations(name, tags, gender) if llm_status != "✅ LLM API is online and reachable." else generate_persona(name, tags, gender, url, api_key=api_key)
            ),
            [name_output, tags_input, gender_input, llm_api_url_input, llm_api_key_input, llm_status_output],
            persona_output
        ).then(
            lambda tags, persona_text, url, api_key, llm_status: (
                persona_text + "\n\n---\n\n" +
                (generate_background_pollinations(tags, persona_text) if llm_status != "✅ LLM API is online and reachable." else generate_background(tags, persona_text, url, api_key=api_key))
            ),
            [tags_input, persona_output, llm_api_url_input, llm_api_key_input, llm_status_output],
            persona_output
        ).then(
            lambda: gr.update(value="📜 Generating Setting..."),
            None,
            generation_status
        ).then(
            lambda persona, tags, url, api_key, llm_status: (
                generate_setting_pollinations(persona, tags) if llm_status != "✅ LLM API is online and reachable." else generate_setting(persona, tags, url, api_key=api_key)
            ),
            [persona_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
            roleplay_output
        ).then(
            lambda persona, setting_text, tags, url, api_key, llm_status: (
                setting_text + "\n\n---\n\n" +
                (generate_first_message_pollinations(persona, setting_text, tags) if llm_status != "✅ LLM API is online and reachable." else generate_first_message(persona, setting_text, tags, url, api_key=api_key))
            ),
            [persona_output, roleplay_output, tags_input, llm_api_url_input, llm_api_key_input, llm_status_output],
            roleplay_output
        ).then(
            lambda: gr.update(value="📝 Generating Image Prompt..."),
            None,
            generation_status
        ).then(
    lambda persona, source: (
            generate_prompt_from_persona(persona), None
            ) if source == "📡 Pollinations" else (
                None, generate_prompt_from_persona(persona)
            ),
            [persona_output, image_source_radio],
            [pollinations_prompt_input, prompt_input]
        ).then(
            lambda: gr.update(value="🎨 Generating Image..."),
            None,
            generation_status
        ).then(
            lambda polli_prompt, prompt, source, url, seed, model, style, negative_prompt, height, width :generate_image_switch(polli_prompt, prompt, source, url, seed, model, style, negative_prompt, height, width),
            [pollinations_prompt_input, prompt_input, image_source_radio, sdapi_url_input, seed_input, pollinations_model_dropdown, image_style_radio, negative_prompt_input, height_input, width_input],
            output_image
        ).then(
            lambda: gr.update(value="✅ Generation Complete!"),
            None,
            generation_status
        )
   
    with gr.Tab("🖼️ Generate from Image"):
        
        with gr.Row():
            export_vision_button = gr.Button(" ⏬ EXPORT ⏬ ", variant="primary", scale=1)
            download_vision_btn = gr.DownloadButton("Download PNG", visible=False)
            download_vision_btn.click(
                lambda path:cleanup_file(path),
                export_file_path,
                None
            )

        with gr.Row():
            with gr.Column():
                with gr.Group():
                    gr.Markdown("### 🔧 OpenAI Vision Settings")
                    with gr.Row():
                        vision_api_url_input = gr.Textbox(label="URL", value="", placeholder="https://text.pollinations.ai/openai", scale=1)
                        vision_api_key_input = gr.Textbox(label="API Key (Optional)", value=None, type="password", scale=1)
                    with gr.Row():
                        vision_status_output = gr.Textbox(label="Status", interactive=False, scale=2)
                        check_vision_status_button = gr.Button("🔍 Check API Status", scale=1)
                        vision_model_dropdown = gr.Dropdown(label="Model", choices=["default"], value="default", scale=2)
                        refresh_vision_models_button = gr.Button("🔄 Refresh Models", scale=1)

                    check_vision_status_button.click(
                        lambda url: handle_llm_check(url),
                        [vision_api_url_input],
                        [vision_status_output, vision_model_dropdown]
                    )
                    refresh_vision_models_button.click(
                        lambda url: gr.update(choices=fetch_models(url), value="default"),
                        [vision_api_url_input],
                        model_dropdown
                    )
            with gr.Column():  
                with gr.Row():
                    image_input = gr.Image(type="pil", label="Upload an Image", height=400, width=300, scale=2)
        with gr.Group():
            with gr.Row():
                vision_generate_button = gr.Button("🔍 Analyze Image (GENERATE ALL)", variant="primary")
            with gr.Row():
                with gr.Column():
                    vision_generate_persona_button = gr.Button("🧬 Generate Persona (Failsafe)", size="sm")
                    vision_generate_background_button = gr.Button("📜 Generate Background (Failsafe)", size="sm")
                with gr.Column():
                    vision_generate_setting_button = gr.Button("📜 Generate Setting (Failsafe)", size="sm")
                    vision_generate_firstmessage_button = gr.Button("📜 Generate First Message (Failsafe)", size="sm")
            with gr.Row():
                vision_response_output = gr.Textbox(label="Character Persona (Info and Background)", lines=12, elem_classes=["scrollable-textbox"])
                setting_from_vision = gr.Textbox(label="RP Setting and First Message", lines=12, elem_classes=["scrollable-textbox"])
        
        vision_generate_button.click(
            lambda image, api_url, model, api_key: generate_persona_from_image(image, api_url, model, api_key),
            [image_input, vision_api_url_input, vision_model_dropdown, vision_api_key_input],
            vision_response_output
        ).then(
            lambda tags, persona_text, url, api_key: (
                persona_text + "\n\n---\n\n" +
                generate_background(tags, persona_text, url, api_key=api_key)),
            [tags_input, vision_response_output, vision_api_url_input, vision_api_key_input],
            vision_response_output
        ).then(
            lambda persona, tags, url, api_key: generate_setting(persona, tags, url, api_key=api_key),
            [vision_response_output, tags_input, vision_api_url_input, vision_api_key_input],
            setting_from_vision
        ).then(
            lambda persona, setting_text, tags, url, api_key: (
                setting_text + "\n\n---\n\n" +
                generate_first_message(persona, setting_text, tags, url, api_key=api_key)
            ),
            [vision_response_output, setting_from_vision, tags_input, vision_api_url_input, vision_api_key_input],
            setting_from_vision
        )
        
        vision_generate_persona_button.click(
            lambda image, api_url, model, api_key: generate_persona_from_image(image, api_url, model, api_key),
            [image_input, vision_api_url_input, vision_model_dropdown, vision_api_key_input],
            vision_response_output
        )
        
        vision_generate_background_button.click(
            lambda tags, persona_text, url, api_key: (
                persona_text + "\n\n---\n\n" +
                generate_background(tags, persona_text, url, api_key=api_key)),
            [tags_input, vision_response_output, vision_api_url_input, vision_api_key_input],
            vision_response_output
        )
        vision_generate_setting_button.click(
            lambda persona, tags, url, api_key: generate_setting(persona, tags, url, api_key=api_key),
            [vision_response_output, tags_input, vision_api_url_input, vision_api_key_input],
            setting_from_vision
        )
        vision_generate_firstmessage_button.click(
            lambda persona, setting_text, tags, url, api_key: (
                setting_text + "\n\n---\n\n" +
                generate_first_message(persona, setting_text, tags, url, api_key=api_key)
            ),
            [vision_response_output, setting_from_vision, tags_input, vision_api_url_input, vision_api_key_input],
            setting_from_vision
        )
        export_button.click(
            lambda persona, roleplay, image: on_export(persona, roleplay, image),
            [persona_output, roleplay_output, output_image],
            [download_btn, download_btn, export_file_path]
        )
        export_vision_button.click(
            lambda persona, roleplay, image: on_export(persona, roleplay, image),
            [vision_response_output, setting_from_vision, image_input],
            [download_vision_btn, download_vision_btn, export_file_path]
        )
    
demo.launch(server_port=7861, inbrowser=True) ## sd usually runs on 7860

