# 🧬 Easy RP Character Generator

A **multi-tab web interface** for generating rich, detailed roleplay (RP) characters using tags, images, or uploaded pictures. This tool combines **OpenAI**, **Pollinations.ai**, and **Stable Diffusion** with intuitive persona creation and image generation workflows. Ideal for writers, roleplayers, and AI character builders.

---

## 🚀 Features

- 🧬 Generate Role Play personas from text or image inputs.
- 🤖 Supports **OpenAI API** and **Pollinations.ai** for language and vision generation  
- 🎨 Image generation via **Stable Diffusion** or **Pollinations.ai**  
- 🧠 One-click persona, background, scenario, first message and portrait generation.
- 📥 Export and download PNG character cards ready to use with SillyTavern (or any ccv3 compatible platform)  
- ✅ Auto-start scripts for **Linux** and **Windows**  

---

## 🛠️ Prerequisites

- **Python 3.10+**

## ▶️ Launch Instructions
These script will create the venv and install any required packages.

### 🐧 Linux

Run the following in a terminal or double-click if your File Manager supports running scripts:

```bash
./webui.sh
```

### 🪟 Windows

Run the following in Command Prompt or double-click:

```bash
webui.cmd
```

> The app will automatically open in your default browser.

---

## 🧑‍🎨 UI Overview

### Tabs:

#### 1. 🧬 Generate from Tags
- Input: Tags, gender, model
- Choose between **OpenAI** or **Pollinations** for persona and image generation
- Pollinations: Realistic / Anime / Cartoon
- Stable Diffusion: Prompt and negative prompt support
- One-click character based generation
- Finalize character with `⏬ EXPORT ⏬` and `Download PNG`

#### 3. 🖼️ Generate from Image
- Upload image and analyze using **OpenAI Vision**
- Extract persona, background, scenario, and initial message from image content
- Finalize character with `⏬ EXPORT ⏬` and `Download PNG`
---

## 🔐 API Settings

You can configure API endpoints and keys in the interface:

- **OpenAI (Text & Vision)**: Optional API key and endpoint input

---

## 📦 Export & Download

Generated characters can be exported using the built-in `Download PNG` after finalizing it with `⏬ EXPORT ⏬`.

---

## ✨ Example Use Cases

- Create **chatbot personas** for character AI platforms  
- Build **rich NPCs** for tabletop games or story writing  
- Generate **artwork and personality** for OC or avatar creation  

---

## 📝 TODO

- Improve error handling and add timeout detection  
- Add a **Character Editor** tab with support for:  
  - Lorebook integration  
  - Alternative greetings  
  - Embedded images  
  - Example dialogues  
  - Creator’s metadata  
  - Prompt override options  
- Perform code cleanup and refactoring  

---

## 🤝 Contributing

Issues, feedback, and pull requests are welcome!  
Feel free to [open an issue](https://github.com/your-repo/issues) to report bugs or suggest features.

---

## 📄 License

This project is licensed under the [GNU General Public License version 2 (GPL-2.0)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
