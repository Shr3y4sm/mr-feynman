# Mr. Feynman 🧠

A local web app that uses the Feynman learning technique to analyze your explanations of complex topics using local LLMs.

## Features
- **Privacy First**: Runs entirely locally using `llama.cpp`.
- **Feynman Analysis**: Scores your explanation based on simplicity, logic, and jargon usage.
- **Modern UI**: Dark-mode enabled interface built with Tailwind CSS.

## Prerequisites

1. **Python 3.10+**
2. **Download a GGUF Model**:
   - We recommend [Phi-3 Mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf).
   - Create a `models` folder in the root directory.
   - Download `Phi-3-mini-4k-instruct-q4.gguf` and place it inside `models/`.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Model Engine (Required for Windows/No-Compiler)**:
   - Download `llama-server.exe` from [llama.cpp releases](https://github.com/ggerganov/llama.cpp/releases) (look for `llama-b*-bin-win-xyz-x64.zip`).
   - Extract `llama-server.exe` into the root folder of this project.

3. **Download Model**:
   - Create a `models` folder.
   - Download [Phi-3 Mini GGUF](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) (file: `Phi-3-mini-4k-instruct-q4.gguf`) to `models/`.

4. **Run the System**:
   
   **Terminal 1 (Model Server)**:
   ```powershell
   ./start_model_server.ps1
   ```

   **Terminal 2 (App)**:
   ```powershell
   python app/main.py
   ```

## Project Structure

- `app/api`: FastAPI route handlers (endpoints).
- `app/services`: Business logic (LLM integration, Analysis logic).
- `app/prompts`: Prompt templates stored separately from code.
- `app/schemas`: Pydantic models for data validation.
- `static`: Frontend assets (HTML, JS, CSS).

## Extending the App
- **New Modes**: Add new prompt templates in `app/prompts/templates.py` and new logic in `app/services`.
- **New Models**: Just change the `MODEL_PATH` in `.env`.
