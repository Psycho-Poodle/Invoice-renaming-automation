# 🚀 Invoice Processing Automation System - Client Package

**Professional GPU-Accelerated Invoice Processing and Renaming System**

## 📦 What's Included

This package contains a complete invoice processing automation system that:
- ✅ Processes PDF invoices using GPU-accelerated OCR
- ✅ Automatically renames files according to accounting codes
- ✅ Supports batch processing of multiple invoices
- ✅ Provides REST API endpoints for integration
- ✅ Runs entirely on your local infrastructure (no cloud dependencies)

## 🎯 Quick Start (5 Minutes)

### 1. Install System
```bash
# Make installation script executable and run
chmod +x install.sh
./install.sh
```

### 2. Test Single Invoice
```bash
python main.py --prompt "Process invoice" --pdf "input/pdffile11101.pdf"
```

### 3. Process Multiple Invoices
```bash
chmod +x process_folder.sh
./process_folder.sh input/digital
```

### 4. Start REST API
```bash
python simple_flask_server.py
```

## 📋 System Requirements

### Hardware
- **GPU**: NVIDIA GPU with 8GB+ VRAM (recommended)
- **RAM**: 16GB+ system memory
- **Storage**: 10GB+ free space

### Software
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.10+
- **CUDA**: Compatible NVIDIA drivers

## 🔧 Installation Guide

### Automated Installation
```bash
./install.sh
```

This script will:
- Install system dependencies (Tesseract, Poppler)
- Set up Python virtual environment
- Install Python packages
- Configure Ollama with GPU support
- Download required AI models

### Manual Installation (if needed)
```bash
# 1. System dependencies
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu poppler-utils

# 2. Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Ollama setup
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl stop ollama
CUDA_VISIBLE_DEVICES=0 ollama serve &
ollama pull llama3.1:8b
```

## 🎯 Usage Methods

### Method 1: Command Line Interface (CLI)
```bash
# Process single invoice
python main.py --prompt "Process invoice" --pdf "input/your_invoice.pdf"

# Use custom accounting codes
python main.py --prompt "Process invoice" --pdf "input/invoice.pdf" --codes "custom_codes.csv"
```

### Method 2: Batch Processing
```bash
# Process all PDFs in input/digital/ folder
./process_folder.sh

# Process specific folder
./process_folder.sh input/mobile_photos

# Process custom folder
./process_folder.sh /path/to/your/invoices
```

### Method 3: REST API
```bash
# Start server
python simple_flask_server.py

# Test API (in another terminal)
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Process invoice input/pdffile11101.pdf"}'
```

## 📁 File Structure

```
Invoice_renaming_automation/
├── main.py                           # Main CLI interface
├── process_folder.sh                 # Batch processing script
├── simple_flask_server.py            # REST API server
├── gpu_aware_ocr_solution.py         # Core OCR processor
├── mcp_filesystem_server.py          # Accounting code management
├── mcp_invoice_extraction_server.py  # Invoice extraction logic
├── install.sh                        # Automated installation
├── test_system.sh                    # System testing
├── requirements.txt                  # Python dependencies
├── input/                            # Input invoices and codes
│   ├── accounting_codes.csv          # Your accounting codes
│   ├── digital/                      # Sample digital invoices
│   ├── mobile_photos/                # Sample scanned invoices
│   └── pdffile11101.pdf              # Test invoice
├── output/                           # Processed invoices appear here
├── logs/                             # System logs
├── src/                              # AutoGen server implementation
└── Documentation/
    ├── CLIENT_README.md              # This file
    ├── README.md                     # Technical documentation
    ├── COMPLETE_WORKFLOW_GUIDE.md    # Detailed workflow guide
    └── CLIENT_DELIVERY_PACKAGE.md    # Package overview
```

## 🎯 Output Format

Invoices are automatically renamed to:
```
YYYYMMDD ACCOUNTING_CODE COMPANY - Description Invoice Nr. [Number].pdf
```

**Example:**
```
20250309 OND295 Microsoft Osterreich GmbH - Billing Invoice Nr. G081952054.pdf
```

## 📊 Performance

- **Processing Time**: 6-30 seconds per invoice
- **GPU Memory Usage**: 5-9GB during processing
- **Batch Processing**: 35+ invoices in 15-20 minutes
- **Success Rate**: 95%+ for digital PDFs
- **Languages**: German and English supported

## 🔍 Accounting Codes

The system uses `input/accounting_codes.csv` to categorize invoices. Format:
```csv
Code,Description,Keywords
OND290,Software Development,development,programming,coding
OND295,Cloud Services,cloud,aws,azure,hosting
OND300,Office Supplies,office,supplies,stationery
```

### Adding Your Codes
1. Edit `input/accounting_codes.csv`
2. Add your accounting codes and keywords
3. System will automatically match invoices to codes

## 🧪 Testing

### System Test
```bash
./test_system.sh
```

### API Test
```bash
# Start server
python simple_flask_server.py

# Test health
curl http://localhost:5001/health

# Test processing
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Process invoice input/pdffile11101.pdf"}'
```

## 🔧 Configuration

### GPU Settings
- System automatically detects and uses available GPU
- Falls back to CPU if GPU unavailable
- Monitor GPU usage: `watch -n 1 nvidia-smi`

### Environment Variables
Edit `.env` file:
```bash
OLLAMA_HOST=http://localhost:11434
FLASK_PORT=5001
LOG_LEVEL=INFO
```

## 📝 Logs and Monitoring

### Log Files
- **Main logs**: `logs/invoice_naming.log`
- **Server logs**: Console output when running servers
- **Error logs**: Detailed error information in logs/

### Monitor Processing
```bash
# Watch logs in real-time
tail -f logs/invoice_naming.log

# Monitor GPU usage
watch -n 1 nvidia-smi

# Check system status
./test_system.sh
```

## ⚠️ Troubleshooting

### Common Issues

#### GPU Not Detected
```bash
# Check GPU
nvidia-smi

# Restart Ollama with GPU
sudo systemctl stop ollama
CUDA_VISIBLE_DEVICES=0 ollama serve &
```

#### Processing Fails
```bash
# Check logs
tail -f logs/invoice_naming.log

# Test system
./test_system.sh

# Restart services
pkill ollama
CUDA_VISIBLE_DEVICES=0 ollama serve &
```

#### API Not Working
```bash
# Check server status
curl http://localhost:5001/health

# Restart server
python simple_flask_server.py
```

### Getting Help
1. Check logs in `logs/` directory
2. Run system test: `./test_system.sh`
3. Verify GPU status: `nvidia-smi`
4. Check documentation files

## 🚀 Production Deployment

### For High Volume Processing
1. **Dedicated GPU Server**: Use server with 16GB+ GPU memory
2. **Batch Processing**: Use `process_folder.sh` for large volumes
3. **API Integration**: Use REST API for web application integration
4. **Monitoring**: Set up log monitoring and alerting

### Integration Examples

#### Python Integration
```python
import requests

def process_invoice(pdf_path):
    response = requests.post('http://localhost:5001/invoice', 
                           json={"prompt": f"Process invoice {pdf_path}"})
    return response.json()
```

#### Bash Integration
```bash
#!/bin/bash
for pdf in /path/to/invoices/*.pdf; do
    python main.py --prompt "Process invoice" --pdf "$pdf"
done
```

## 📞 Support

For technical support:
1. Check this documentation
2. Review log files in `logs/` directory
3. Run system diagnostics: `./test_system.sh`
4. Contact your technical team with log files

## 🎉 Success!

Your invoice processing automation system is ready! The system will:
- ✅ Process invoices with 95%+ accuracy
- ✅ Rename files according to your accounting codes
- ✅ Handle both digital and scanned PDFs
- ✅ Provide API access for integration
- ✅ Run entirely on your infrastructure

**Happy Processing!** 🚀 