# GPU-Aware Invoice Processing System

A high-performance invoice processing and renaming system that uses GPU-accelerated OCR with Ollama for intelligent document analysis.

## 🚀 Features

- **GPU-Accelerated Processing**: Utilizes NVIDIA GPUs for fast invoice processing
- **Intelligent OCR**: Combines PyPDF2, Tesseract, and Ollama LLM for accurate text extraction
- **Automated Renaming**: Generates structured filenames based on accounting codes
- **Batch Processing**: Process multiple PDF files in folders automatically
- **REST API Endpoints**: HTTP API for integration with web applications and external systems
- **Multi-Language Support**: Handles German and English invoices
- **No Cloud Dependencies**: Runs entirely on local infrastructure

## 🏗️ Architecture

```
main.py ──► GPUAwareInvoiceOCRProcessor ──► Ollama (GPU) ──► Structured Data
    │                                                              │
    └──► AccountingManager ──► Filename Generation ──► File Copy ──┘
```

## 📋 Requirements

### System Dependencies
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu poppler-utils
```

### Ollama Installation
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## 🔧 Setup

1. **Clone and Setup Environment**:
   ```bash
   git clone <repository>
   cd invoice_renaming
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install System Dependencies**:
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu poppler-utils
   ```

3. **Setup Ollama with GPU**:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Stop system service and start with GPU
   sudo systemctl stop ollama
   CUDA_VISIBLE_DEVICES=0 ollama serve &
   
   # Pull required model
   ollama pull llama3.1:8b
   ```

4. **Prepare Input Files**:
   - Place PDF invoices in `input/` directory
   - Ensure `input/accounting_codes.csv` contains your accounting codes

## ⚡ Quick Start

### Single Invoice
```bash
python main.py --prompt "Process invoice" --pdf "input/your_invoice.pdf"
```

### Batch Processing (Multiple Invoices)
```bash
# Make script executable
chmod +x process_folder.sh

# Process all PDFs in input/digital/ folder
./process_folder.sh

# Process specific folder
./process_folder.sh input/mobile_photos
```

### REST API Testing
```bash
# Start the Flask server
python simple_flask_server.py

# Test the API (in another terminal)
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Process invoice input/pdffile11101.pdf"}'
```

## 🎯 Usage

### Basic Usage
```bash
python main.py --prompt "Process the invoice input/pdffile11101.pdf and rename it according to our accounting system"
```

### Direct PDF Processing
```bash
python main.py --prompt "Process invoice" --pdf "input/digital/invoice.pdf"
```

### Custom Accounting Codes
```bash
python main.py --prompt "Process invoice" --pdf "input/invoice.pdf" --codes "custom_codes.csv"
```

## 📁 Batch Processing (Multiple Files)

### Process Entire Folder
```bash
# Process all PDFs in input/digital/ folder (default)
./process_folder.sh

# Process PDFs in specific folder
./process_folder.sh input/mobile_photos

# Process PDFs in any custom folder
./process_folder.sh /path/to/your/invoices
```

### Monitor Large Batches
```bash
# Run in background with logging
./process_folder.sh input/digital > logs/batch_$(date +%Y%m%d_%H%M).log 2>&1 &

# Monitor progress
tail -f logs/batch_*.log

# Check completion status
ps aux | grep process_folder
```

### Batch Processing Performance
- **Small Batch (10 files)**: 2-5 minutes
- **Medium Batch (50 files)**: 10-25 minutes  
- **Large Batch (100+ files)**: 20-50 minutes
- **Success Rate**: 95%+ for digital PDFs
- **GPU Memory Usage**: 5-9GB during processing

### Example Batch Output
```bash
📁 Batch Invoice Processing
==========================
📊 Found 37 PDF files in input/digital

🚀 Starting batch processing...

📄 Processing: invoice1.pdf
✅ Success: invoice1.pdf
📄 Processing: invoice2.pdf
✅ Success: invoice2.pdf
---

📊 Batch Processing Complete!
✅ Processed: 35 files
❌ Failed: 2 files
📁 Check output/ folder for results
```

## 🌐 REST API Endpoints

The system provides REST API endpoints for integration with web applications and external systems.

### Start the Flask Server

#### Option 1: Simple Flask Server (Recommended)
```bash
# Start the simplified server (bypasses AutoGen complexity)
python simple_flask_server.py
```

#### Option 2: Full AutoGen Flask Server
```bash
# Start the full server with AutoGen agents
python src/invoice_team/flask_server.py
```

### Available Endpoints

#### Health Check
```bash
# Check if server is running
curl -X GET http://localhost:5001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "invoice-processing"
}
```

#### Process Invoice
```bash
# Basic invoice processing
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process invoice input/pdffile11101.pdf"
  }'
```

**Response:**
```json
{
  "success": true,
  "original_file": "pdffile11101.pdf",
  "new_filename": "20250309 OND295 Microsoft Osterreich GmbH - Billing Invoice Nr. G081952054.pdf",
  "output_path": "output/20250309 OND295 Microsoft Osterreich GmbH - Billing Invoice Nr. G081952054.pdf",
  "invoice_data": {
    "date": "2025-03-09",
    "number": "G081952054",
    "description": "Billing for the period 01022025 - 280220",
    "amount": "€1,234.56",
    "currency": "EUR",
    "issuer": "Microsoft Osterreich GmbH",
    "recipient": "Your Company"
  },
  "accounting_code": "OND295",
  "gpu_accelerated": true,
  "processing_time": 8.5
}
```

### Advanced API Usage

#### Process Specific PDF File
```bash
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process invoice input/digital/company_invoice.pdf"
  }'
```

#### Process with Custom Accounting Codes
```bash
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process invoice input/invoice.pdf using custom_codes.csv"
  }'
```

### API Testing Examples

#### Test with Sample Invoice
```bash
# Test with the default sample file
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Read and analyze the PDF input/pdffile11101.pdf and rename it according to our accounting system"
  }' | jq '.'
```

#### Batch API Testing Script
```bash
# Create a simple test script
cat > test_api.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing Invoice Processing API"
echo "================================"

# Test health endpoint
echo "📋 Health Check:"
curl -s http://localhost:5001/health | jq '.'

echo -e "\n📄 Processing Sample Invoice:"
curl -s -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Process invoice input/pdffile11101.pdf"}' | jq '.'
EOF

chmod +x test_api.sh
./test_api.sh
```

### Error Handling

#### Missing Prompt
```bash
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "error": "Missing prompt in request body"
}
```

#### File Not Found
```bash
curl -X POST http://localhost:5001/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Process invoice input/nonexistent.pdf"
  }'
```

**Response:**
```json
{
  "error": "PDF file not found: input/nonexistent.pdf"
}
```

### API Performance Monitoring

#### Monitor Server Logs
```bash
# Watch server output in real-time
tail -f logs/flask_server.log

# Monitor GPU usage during API calls
watch -n 1 nvidia-smi
```

#### Load Testing
```bash
# Simple load test with multiple concurrent requests
for i in {1..5}; do
  curl -X POST http://localhost:5001/invoice \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Process invoice input/pdffile11101.pdf"}' &
done
wait
```

### Integration Examples

#### Python Integration
```python
import requests
import json

def process_invoice_api(pdf_path):
    url = "http://localhost:5001/invoice"
    payload = {"prompt": f"Process invoice {pdf_path}"}
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

# Usage
result = process_invoice_api("input/my_invoice.pdf")
print(json.dumps(result, indent=2))
```

#### JavaScript/Node.js Integration
```javascript
const axios = require('axios');

async function processInvoice(pdfPath) {
  try {
    const response = await axios.post('http://localhost:5001/invoice', {
      prompt: `Process invoice ${pdfPath}`
    });
    return response.data;
  } catch (error) {
    return { error: error.message };
  }
}

// Usage
processInvoice('input/my_invoice.pdf')
  .then(result => console.log(JSON.stringify(result, null, 2)));
```

## 📊 Performance

- **GPU Acceleration**: ~5-7GB GPU memory usage
- **Processing Time**: 6-28 seconds per invoice (depending on complexity)
- **Accuracy**: High accuracy with structured data extraction
- **Supported Formats**: PDF (digital and scanned)

## 📁 File Structure

```
invoice_renaming/
├── main.py                           # Main entry point
├── process_folder.sh                 # Batch processing script
├── gpu_aware_ocr_solution.py         # GPU-aware OCR processor
├── mcp_filesystem_server.py          # Accounting code management
├── mcp_invoice_extraction_server.py  # Invoice extraction server
├── input/                            # Input invoices
│   ├── accounting_codes.csv          # Accounting codes
│   ├── digital/                      # Digital PDF invoices
│   └── mobile_photos/                 # Scanned/photographed invoices
├── output/                           # Processed and renamed invoices
├── logs/                             # Application logs
└── requirements.txt                  # Python dependencies
```

## 🎯 Output Format

Invoices are renamed using the format:
```
YYYYMMDD ACCOUNTING_CODE COMPANY - Description Invoice Nr. [Number].pdf
```

Example:
```
20250309 OND295 Microsoft Osterreich GmbH - Billing for the period 01022025 - 280220 Invoice Nr. G081952054.pdf
```

## 🔍 Extracted Data

The system extracts:
- **Date**: Invoice date
- **Number**: Invoice number
- **Description**: Invoice description/purpose
- **Amount**: Total amount
- **Currency**: Currency code
- **Issuer**: Company issuing the invoice
- **Recipient**: Company receiving the invoice
- **VAT Numbers**: Tax identification numbers

## 🚀 GPU Requirements

- **Recommended**: NVIDIA GPU with 8GB+ VRAM
- **Tested**: NVIDIA A100-SXM4-40GB
- **Fallback**: CPU processing (slower but functional)

## 📝 Logging

Comprehensive logging includes:
- GPU detection and utilization
- Processing times and performance metrics
- Error handling and debugging information
- File operations and transformations

## 🛠️ Troubleshooting

### GPU Not Detected
```bash
# Check GPU availability
nvidia-smi

# Restart Ollama with GPU
sudo systemctl stop ollama
CUDA_VISIBLE_DEVICES=0 ollama serve &
```

### Model Not Found
```bash
# Pull required model
ollama pull llama3.1:8b

# List available models
ollama list
```

### Permission Issues
```bash
# Fix file permissions
chmod +x main.py
sudo chown -R $USER:$USER invoice_renaming/
```

## 📈 Future Enhancements

- [ ] REST API interface
- [ ] Docker containerization
- [ ] Batch processing capabilities
- [ ] Web UI for invoice management
- [ ] Additional language support
- [ ] Cloud deployment options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- Ollama for local LLM inference
- Tesseract OCR for text extraction
- PyPDF2 for PDF processing
- NVIDIA for GPU acceleration capabilities 