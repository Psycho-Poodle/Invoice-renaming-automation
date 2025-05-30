#!/usr/bin/env python3
"""
Simplified Flask Server for Invoice Processing
Uses GPU-aware OCR solution directly without AutoGen agents.
"""

from flask import Flask, request, jsonify
import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our GPU-aware OCR solution
from gpu_aware_ocr_solution import GPUAwareInvoiceOCRProcessor
from mcp_filesystem_server import accounting_manager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "invoice-processing"})

@app.route('/invoice', methods=['POST'])
def process_invoice():
    """Process invoice endpoint"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt in request body'}), 400
        
        prompt = data['prompt']
        logger.info(f"Processing request: {prompt}")
        
        # Extract PDF path from prompt (simple parsing)
        import re
        pdf_match = re.search(r'input/[^\s]+\.pdf', prompt)
        if pdf_match:
            pdf_path = pdf_match.group(0)
        else:
            pdf_path = "input/pdffile11101.pdf"  # Default
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            return jsonify({'error': f'PDF file not found: {pdf_path}'}), 404
        
        # Initialize OCR processor
        logger.info("Initializing GPU-aware OCR processor...")
        ocr_processor = GPUAwareInvoiceOCRProcessor()
        
        # Load accounting codes
        codes_csv = "input/accounting_codes.csv"
        if os.path.exists(codes_csv):
            accounting_manager.load_accounting_codes(codes_csv)
            logger.info(f"Loaded {len(accounting_manager.codes)} accounting codes")
        
        # Process the invoice
        logger.info(f"Processing invoice: {pdf_path}")
        invoice_data = ocr_processor.ExtractInvoiceDetailsFromPdf(pdf_path)
        
        if "error" in invoice_data:
            return jsonify({'error': f'OCR processing failed: {invoice_data["error"]}'}), 500
        
        # Find matching accounting code
        accounting_code = accounting_manager.find_matching_code(invoice_data)
        
        # Generate new filename
        new_filename = accounting_manager.generate_filename(invoice_data, accounting_code)
        
        # Create output directory and copy file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        import shutil
        dest_path = os.path.join(output_dir, new_filename)
        shutil.copy2(pdf_path, dest_path)
        
        result = {
            "success": True,
            "original_file": os.path.basename(pdf_path),
            "new_filename": new_filename,
            "output_path": dest_path,
            "invoice_data": invoice_data,
            "accounting_code": accounting_code,
            "gpu_accelerated": invoice_data.get('gpu_accelerated', False),
            "processing_time": invoice_data.get('processing_time', 0)
        }
        
        logger.info(f"Successfully processed: {new_filename}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    print(f"🚀 Starting Simple Flask Server on http://localhost:{port}")
    print(f"📋 Available endpoints:")
    print(f"   GET  /health - Health check")
    print(f"   POST /invoice - Process invoice")
    print(f"🛑 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=True) 