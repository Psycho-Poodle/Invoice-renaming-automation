#!/bin/bash

# GPU-Aware Invoice Processing System - Installation Script
# Version: 1.0
# Date: 2025-05-28

set -e  # Exit on any error

echo "🚀 GPU-Aware Invoice Processing System - Installation"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux systems only."
    exit 1
fi

print_step "1/8 - Checking system requirements..."

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    print_status "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
else
    print_warning "NVIDIA GPU not detected. System will run on CPU (slower performance)."
fi

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION detected"
else
    print_error "Python 3 is required but not installed."
    exit 1
fi

print_step "2/8 - Installing system dependencies..."

# Update package list
sudo apt update

# Install required system packages
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    poppler-utils \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget

print_status "System dependencies installed successfully"

print_step "3/8 - Installing Ollama..."

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    print_status "Ollama is already installed"
else
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    print_status "Ollama installed successfully"
fi

print_step "4/8 - Setting up Python virtual environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

print_status "Python environment set up successfully"

print_step "5/8 - Creating directory structure..."

# Create necessary directories
mkdir -p input/digital input/mobile_photos output logs test_output

print_status "Directory structure created"

print_step "6/8 - Configuring Ollama and GPU..."

# Stop system Ollama service if running
sudo systemctl stop ollama 2>/dev/null || true

# Start Ollama with GPU support
print_status "Starting Ollama with GPU support..."
CUDA_VISIBLE_DEVICES=0 ollama serve > logs/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Check if Ollama is running
if ps -p $OLLAMA_PID > /dev/null; then
    print_status "Ollama started successfully (PID: $OLLAMA_PID)"
else
    print_warning "Ollama may not have started correctly. Check logs/ollama.log"
fi

print_step "7/8 - Downloading AI model..."

# Pull required model
print_status "Downloading llama3.1:8b model (this may take several minutes)..."
ollama pull llama3.1:8b

print_status "AI model downloaded successfully"

print_step "8/8 - Running system verification..."

# Test GPU detection
if command -v nvidia-smi &> /dev/null; then
    print_status "GPU Status:"
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader
fi

# Test Ollama
print_status "Testing Ollama connection..."
if ollama list | grep -q "llama3.1:8b"; then
    print_status "✅ Ollama and model are working correctly"
else
    print_error "❌ Ollama model test failed"
fi

# Test Python environment
print_status "Testing Python environment..."
if python -c "import PyPDF2, PIL, pdf2image, pytesseract, requests, flask, mcp; print('✅ All Python dependencies available')" 2>/dev/null; then
    print_status "✅ Python environment is working correctly"
else
    print_error "❌ Python environment test failed"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo "1. Place your accounting codes CSV file in: input/accounting_codes.csv"
echo "2. Place PDF invoices in: input/ or input/digital/"
echo "3. Run the system with:"
echo "   source venv/bin/activate"
echo "   python main.py --prompt \"Process invoice input/your_invoice.pdf\""
echo ""
echo "📁 Important Files:"
echo "   - Main script: main.py"
echo "   - Configuration: input/accounting_codes.csv"
echo "   - Logs: logs/invoice_naming.log"
echo "   - Output: output/"
echo ""
echo "🔧 GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sed 's/^/   - /'
else
    echo "   - No NVIDIA GPU detected (CPU mode)"
fi
echo ""
echo "📖 For detailed usage instructions, see: COMPLETE_WORKFLOW_GUIDE.md"
echo ""
print_status "System is ready for use! 🚀" 