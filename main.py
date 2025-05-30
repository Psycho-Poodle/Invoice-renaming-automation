#!/usr/bin/env python3
"""
Main entry point for the GPU-aware Invoice Naming system.
This script uses our GPU-aware OCR solution directly without AutoGen agents.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
def setup_logging():
    """Set up logging configuration."""
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging to file and console
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, "invoice_naming.log")),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create a logger
    logger = logging.getLogger("invoice_naming")
    logger.info(f"Logging initialized with level: {log_level_str}")
    return logger

# Set up logging
logger = setup_logging()

# Try to load environment variables, but continue if .env file is missing or corrupted
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file. Using default values. Error: {e}")

# Import our GPU-aware OCR solution and MCP servers
from gpu_aware_ocr_solution import GPUAwareInvoiceOCRProcessor
from mcp_filesystem_server import accounting_manager


def process_invoice_direct(pdf_path: str, codes_csv: str = "input/accounting_codes.csv") -> Dict[str, Any]:
    """
    Process invoice directly using GPU-aware OCR without AutoGen agents.
    
    Args:
        pdf_path: Path to the PDF file
        codes_csv: Path to accounting codes CSV
        
    Returns:
        Dictionary with processing results
    """
    try:
        # Initialize GPU-aware OCR processor
        logger.info("🚀 Initializing GPU-aware OCR processor...")
        ocr_processor = GPUAwareInvoiceOCRProcessor()
        
        # Validate input files
        if not os.path.exists(pdf_path):
            return {"error": f"PDF file not found: {pdf_path}"}
        
        if not os.path.exists(codes_csv):
            return {"error": f"Accounting codes CSV not found: {codes_csv}"}
        
        # Load accounting codes
        logger.info(f"📊 Loading accounting codes from: {codes_csv}")
        success = accounting_manager.load_accounting_codes(codes_csv)
        if not success:
            return {"error": f"Failed to load accounting codes from: {codes_csv}"}
        
        logger.info(f"✅ Loaded {len(accounting_manager.codes)} accounting codes")
        
        # Extract invoice data using GPU-aware OCR
        logger.info(f"🔍 Processing invoice: {pdf_path}")
        invoice_data = ocr_processor.ExtractInvoiceDetailsFromPdf(pdf_path)
        
        if "error" in invoice_data:
            return {"error": f"OCR processing failed: {invoice_data['error']}"}
        
        # Find matching accounting code
        logger.info("🎯 Finding matching accounting code...")
        accounting_code = accounting_manager.find_matching_code(invoice_data)
        
        # Generate new filename
        logger.info("📝 Generating new filename...")
        new_filename = accounting_manager.generate_filename(invoice_data, accounting_code)
        
        # Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy and rename file
        import shutil
        source_path = pdf_path
        dest_path = os.path.join(output_dir, new_filename)
        
        logger.info(f"📁 Copying file...")
        logger.info(f"   From: {source_path}")
        logger.info(f"   To: {dest_path}")
        
        shutil.copy2(source_path, dest_path)
        file_size = os.path.getsize(dest_path)
        
        logger.info(f"✅ Successfully processed invoice!")
        logger.info(f"   • Original: {os.path.basename(pdf_path)}")
        logger.info(f"   • Renamed: {new_filename}")
        logger.info(f"   • Size: {file_size:,} bytes")
        logger.info(f"   • GPU Accelerated: {invoice_data.get('gpu_accelerated', False)}")
        logger.info(f"   • Processing Time: {invoice_data.get('processing_time', 0):.2f}s")
        
        return {
            "success": True,
            "original_file": os.path.basename(pdf_path),
            "new_filename": new_filename,
            "output_path": dest_path,
            "file_size": file_size,
            "invoice_data": invoice_data,
            "accounting_code": accounting_code,
            "gpu_accelerated": invoice_data.get('gpu_accelerated', False),
            "processing_time": invoice_data.get('processing_time', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing invoice: {e}")
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GPU-aware Invoice Naming System (Direct Processing)")
    parser.add_argument(
        "--prompt", "-p",
        help="Prompt describing the invoice renaming task",
        required=True
    )
    parser.add_argument(
        "--pdf", 
        help="Direct path to PDF file (overrides prompt parsing)",
        default=None
    )
    parser.add_argument(
        "--codes",
        help="Path to accounting codes CSV",
        default="input/accounting_codes.csv"
    )
    
    args = parser.parse_args()
    
    # Determine PDF path
    if args.pdf:
        pdf_path = args.pdf
    else:
        # Simple prompt parsing to extract PDF path
        import re
        pdf_match = re.search(r'input/[^\s]+\.pdf', args.prompt)
        if pdf_match:
            pdf_path = pdf_match.group(0)
        else:
            pdf_path = "input/pdffile11101.pdf"  # Default
    
    logger.info(f"🎯 Processing: {pdf_path}")
    
    # Process the invoice
    result = process_invoice_direct(pdf_path, args.codes)
    
    if result.get("success"):
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Processed: {result['original_file']}")
        print(f"📝 Renamed to: {result['new_filename']}")
        print(f"📁 Saved to: {result['output_path']}")
        print(f"🚀 GPU Accelerated: {result['gpu_accelerated']}")
        print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 