Write-Host "Checking for llama-server.exe..."
$serverPath = "llama-server.exe"

if (-not (Test-Path $serverPath)) {
    Write-Host "llama-server.exe not found in root directory!" -ForegroundColor Red
    Write-Host "Please download the latest 'llama-server.exe' (Windows zip) from:"
    Write-Host "https://github.com/ggerganov/llama.cpp/releases"
    Write-Host "Extract 'llama-server.exe' to this folder: $(Get-Location)"
    exit
}

$modelPath = "models/Phi-3-mini-4k-instruct-q4.gguf"
if (-not (Test-Path $modelPath)) {
    Write-Host "Model not found at $modelPath" -ForegroundColor Red
    Write-Host "Please download Phi-3 GGUF and place it in 'models/'"
    exit
}

Write-Host "Starting Local LLM Server..." -ForegroundColor Green
Write-Host "Model: $modelPath"
Write-Host "URL: http://localhost:8080"

# Run server with 4k context and proper chat template
./llama-server.exe -m $modelPath -c 4096 --host 0.0.0.0 --port 8080 --n-gpu-layers 0
