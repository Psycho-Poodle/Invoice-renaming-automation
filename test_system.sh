#!/bin/bash

# GPU-Aware Invoice Processing System - Test Script
# Version: 1.0
# Date: 2025-05-28

echo "🧪 GPU-Aware Invoice Processing System - System Test"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ️  INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        print_status "$test_name"
        ((TESTS_PASSED++))
    else
        print_error "$test_name"
        ((TESTS_FAILED++))
    fi
}

echo "🔍 Running System Tests..."
echo "========================="

# Test 1: Check if virtual environment exists
run_test "Virtual Environment" "[ -d 'venv' ]"

# Test 2: Check if main script exists
run_test "Main Script" "[ -f 'main.py' ]"

# Test 3: Check if GPU-aware OCR solution exists
run_test "GPU OCR Module" "[ -f 'gpu_aware_ocr_solution.py' ]"

# Test 4: Check if MCP servers exist
run_test "MCP Servers" "[ -f 'mcp_filesystem_server.py' ] && [ -f 'mcp_invoice_extraction_server.py' ]"

# Test 5: Check if accounting codes exist
run_test "Accounting Codes" "[ -f 'input/accounting_codes.csv' ]"

# Test 6: Check if directories exist
run_test "Directory Structure" "[ -d 'input' ] && [ -d 'output' ] && [ -d 'logs' ]"

# Test 7: Check if Ollama is installed
run_test "Ollama Installation" "command -v ollama"

# Test 8: Check if NVIDIA GPU is available
if command -v nvidia-smi &>/dev/null; then
    run_test "NVIDIA GPU" "nvidia-smi"
else
    print_warning "NVIDIA GPU not detected (CPU mode will be used)"
fi

# Test 9: Check if Ollama is running
run_test "Ollama Service" "curl -s http://localhost:11434/api/tags"

# Test 10: Check if required model is available
run_test "AI Model (llama3.1:8b)" "ollama list | grep -q 'llama3.1:8b'"

echo ""
echo "🧪 Running Functional Tests..."
echo "============================="

# Activate virtual environment for Python tests
source venv/bin/activate 2>/dev/null || {
    print_error "Could not activate virtual environment"
    exit 1
}

# Test 11: Check Python dependencies
echo -n "Testing Python Dependencies... "
if python -c "import PyPDF2, PIL, pdf2image, pytesseract, requests, flask, mcp" 2>/dev/null; then
    print_status "Python Dependencies"
    ((TESTS_PASSED++))
else
    print_error "Python Dependencies"
    ((TESTS_FAILED++))
fi

# Test 12: Test with sample invoice (if available)
if [ -f "input/pdffile11101.pdf" ]; then
    echo -n "Testing Invoice Processing... "
    if timeout 60 python main.py --prompt "Test invoice processing" --pdf "input/pdffile11101.pdf" &>/dev/null; then
        print_status "Invoice Processing"
        ((TESTS_PASSED++))
    else
        print_error "Invoice Processing (timeout or error)"
        ((TESTS_FAILED++))
    fi
else
    print_warning "No test invoice found (input/pdffile11101.pdf)"
fi

echo ""
echo "📊 System Information"
echo "===================="

# GPU Information
if command -v nvidia-smi &>/dev/null; then
    print_info "GPU Information:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/    /'
else
    print_info "GPU: Not available (CPU mode)"
fi

# Python version
PYTHON_VERSION=$(python --version 2>&1)
print_info "Python: $PYTHON_VERSION"

# Ollama version
if command -v ollama &>/dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -1)
    print_info "Ollama: $OLLAMA_VERSION"
fi

# Available models
print_info "Available AI Models:"
ollama list 2>/dev/null | tail -n +2 | sed 's/^/    /' || echo "    None available"

# Disk space
DISK_USAGE=$(df -h . | tail -1 | awk '{print $4}')
print_info "Available Disk Space: $DISK_USAGE"

echo ""
echo "📋 Test Results Summary"
echo "======================"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    print_status "🎉 All tests passed! System is ready for production use."
    echo ""
    echo "📖 Quick Start:"
    echo "   source venv/bin/activate"
    echo "   python main.py --prompt \"Process invoice input/your_invoice.pdf\""
    echo ""
    echo "📚 For detailed instructions, see: COMPLETE_WORKFLOW_GUIDE.md"
    exit 0
else
    echo ""
    print_error "❌ Some tests failed. Please check the installation."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Run: ./install.sh"
    echo "   2. Check logs in: logs/"
    echo "   3. Verify GPU with: nvidia-smi"
    echo "   4. Check Ollama with: ollama list"
    echo ""
    echo "📚 For help, see: COMPLETE_WORKFLOW_GUIDE.md"
    exit 1
fi 