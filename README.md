# Mr. Feynman 🧠

**"If you can’t explain it simply, you don’t understand it well enough."**

Mr. Feynman is a local-first learning companion that uses the **Feynman Technique** to help you master complex topics. By explaining concepts in simple terms, the AI analyzes your understanding, detects jargon, and identifies knowledge gaps—all running 100% locally on your machine for maximum privacy.

![Project Status](https://img.shields.io/badge/Phase_2-Complete-success)

## ✨ Features

### Phase 1: The Core Loop
- **The Feynman Loop**: Explain → Analyze → Improve.
- **Deep Analysis**: Detects "black box" jargon, logical gaps, and false understanding.
- **Local Intelligence**: Powered by **Phi-3 Mini** (via `llama.cpp`), running offline on your CPU/GPU.
- **Modern UI**: Distraction-free, dark-themed interface designed for focused thinking.

### Phase 2: Context & Growth (NEW)
- **Source Material (RAG)**: Optionally upload PDF notes/textbooks. The AI checks your explanation against the *actual source material* for accuracy, not just logic.
- **Progress Tracking**: Your previous explanations are saved locally (JSON).
- **Growth Comparison**: If you revise an explanation, the AI compares it to your last attempt and highlights improvements.
- **Adaptive UX**: The interface provides inline guidance and context reminders based on your workflow state.

## 🛠️ Architecture
The project uses a **Split Architecture** to keep the core application lightweight and the AI modular:

1.  **The Brain (`llama-server`)**: A standalone local HTTP server that hosts the GGUF model.
2.  **The App (`FastAPI` + `Vanilla JS`)**: A lightweight frontend/backend that sends prompts to "The Brain".
3.  **The Context Engine (Phase 2)**: A custom Python-based RAG pipeline (using `pypdf` + TF-IDF chunking) that requires *no* external vector database.

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

## License
MIT
