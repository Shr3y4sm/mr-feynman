# Mr. Feynman 🧠

**"If you can’t explain it simply, you don’t understand it well enough."**

Mr. Feynman is a local-first learning companion that uses the **Feynman Technique** to help you master complex topics. By explaining concepts in simple terms, the AI analyzes your understanding, detects jargon, and identifies knowledge gaps—all running 100% locally on your machine for maximum privacy.

![Project Status](https://img.shields.io/badge/Phase_1-Complete-success)

## ✨ Phase 1 Features
- **The Feynman Loop**: Explain → Analyze → Improve.
- **Deep Analysis**: Detects "black box" jargon, logical gaps, and false understanding.
- **Local Intelligence**: Powered by **Phi-3 Mini** (via `llama.cpp`), running offline on your CPU/GPU.
- **Modern UI**: Distraction-free, dark-themed interface designed for focused thinking.
- **Structured Feedback**:
  - 📝 **Summary**: A high-level assessment of your explanation.
  - 🚩 **Gaps**: Specific logical holes or undefined terms.
  - 💡 **Suggestions**: Concrete tips to simplify your mental model.
  - ❓ **Deep Dive**: Follow-up questions to test the edges of your knowledge.

## 🛠️ Architecture
The project uses a **Split Architecture** to keep the core application lightweight and the AI modular:

1.  **The Brain (`llama-server`)**: A standalone local HTTP server that hosts the GGUF model.
2.  **The App (`FastAPI` + `Vanilla JS`)**: A lightweight frontend/backend that sends prompts to "The Brain".

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- A Windows PC (Phase 1 optimized for Windows)

### 1. Installation
Clone the repo and install the Python dependencies:
```bash
# Create venv (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setup "The Brain" (One-time only)
This project requires two binary components to run locally:

1.  **The Engine**: Download `llama-server.exe` (Windows zip) from [llama.cpp releases](https://github.com/ggerganov/llama.cpp/releases). Extract it to the **root** of this folder.
2.  **The Model**: Download [Phi-3 Mini 4k Instruct (GGUF)](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) (specifically `Phi-3-mini-4k-instruct-q4.gguf`) and place it in the `models/` folder.

### 3. Run the System
You need **two** terminal windows open.

**Terminal 1: Start "The Brain"**
```powershell
./start_model_server.ps1
```
*Wait until you see "HTTP server listening"*

**Terminal 2: Start "The App"**
```powershell
# If using venv
$env:PYTHONPATH="$PWD"; & ".venv\Scripts\python.exe" -m app.main
```

Visit **[http://localhost:8000](http://localhost:8000)** to start learning!

## 📂 Project Structure
```text
Mr. Feynman/
├── app/
│   ├── api/            # FastAPI Endpoints
│   ├── core/           # Config & Privacy settings
│   ├── prompts/        # The "Feynman Persona" templates
│   ├── services/       # Logic for talking to the Local LLM
│   └── main.py         # App Entrypoint
├── static/             # Frontend (HTML/CSS/JS)
├── models/             # GGUF Models (Ignored by Git)
├── scripts/            # Helper scripts 
└── start_model_server.ps1  # Launcher for the AI Engine
```

## 🤝 Contributing
Since this is a personal learning tool, feel free to fork it and add your own "Modes" in `app/prompts/templates.py`.

## License
MIT
