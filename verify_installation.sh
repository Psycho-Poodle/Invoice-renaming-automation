#!/bin/bash

echo "🔍 Invoice Processing System - Installation Verification"
echo "========================================================"

# Check Python
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo "✅ Python3 found"
else
    echo "❌ Python3 not found"
    exit 1
fi

# Check GPU
echo -e "\n🎮 Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo "✅ NVIDIA GPU detected"
else
    echo "⚠️  No NVIDIA GPU detected (will use CPU)"
fi

# Check Ollama
echo -e "\n🤖 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama installed"
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Ollama service running"
    else
        echo "⚠️  Ollama service not running"
        echo "   Start with: CUDA_VISIBLE_DEVICES=0 ollama serve &"
    fi
else
    echo "❌ Ollama not found"
fi

# Check required files
echo -e "\n📁 Checking required files..."
required_files=(
    "main.py"
    "gpu_aware_ocr_solution.py"
    "simple_flask_server.py"
    "process_folder.sh"
    "requirements.txt"
    "input/accounting_codes.csv"
    "input/pdffile11101.pdf"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

# Check directories
echo -e "\n📂 Checking directories..."
required_dirs=("input" "output" "logs")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ missing"
        mkdir -p "$dir"
        echo "   Created $dir/"
    fi
done

# Check Python packages
echo -e "\n📦 Checking Python packages..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    if python3 -c "import requests, pdf2image, PIL" 2>/dev/null; then
        echo "✅ Core packages installed"
    else
        echo "⚠️  Some packages missing. Run: pip install -r requirements.txt"
    fi
else
    echo "❌ requirements.txt missing"
fi

echo -e "\n🎯 Quick Test Commands:"
echo "1. Test single invoice:    python main.py --prompt 'Process invoice' --pdf 'input/pdffile11101.pdf'"
echo "2. Test batch processing:  ./process_folder.sh input/digital"
echo "3. Test API server:        python simple_flask_server.py"
echo "4. Run full system test:   ./test_system.sh"

echo -e "\n✅ Verification complete!"
echo "📖 See CLIENT_README.md for detailed usage instructions" 