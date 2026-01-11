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
   *Note: If you have a GPU, ensure you install `llama-cpp-python` with CUDA support for faster performance.*

2. **Environment Setup**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if your model path is different.

3. **Run the App**:
   ```bash
   python app/main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the Interface**:
   Open your browser to `http://localhost:8000`.

## Project Structure

- `app/api`: FastAPI route handlers (endpoints).
- `app/services`: Business logic (LLM integration, Analysis logic).
- `app/prompts`: Prompt templates stored separately from code.
- `app/schemas`: Pydantic models for data validation.
- `static`: Frontend assets (HTML, JS, CSS).

## Extending the App
- **New Modes**: Add new prompt templates in `app/prompts/templates.py` and new logic in `app/services`.
- **New Models**: Just change the `MODEL_PATH` in `.env`.
