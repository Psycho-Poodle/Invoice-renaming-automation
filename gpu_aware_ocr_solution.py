#!/usr/bin/env python3
"""
GPU-Aware OCR Solution for Invoice Processing
Enhanced version with proper GPU detection, utilization, and logging
"""

import requests
import json
import base64
import subprocess
import os
import time
import logging
from pathlib import Path
from pdf2image import convert_from_path
import tempfile
import pytesseract
from PIL import Image
import PyPDF2
from typing import Dict, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUAwareInvoiceOCRProcessor:
    """
    GPU-aware OCR processor with comprehensive GPU detection and logging
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.text_model = "llama3.1:8b"
        self.gpu_available = False
        self.gpu_info = {}
        
        # Initialize GPU detection and Ollama setup
        self._detect_gpu()
        self._setup_ollama_gpu()
        self._verify_ollama_status()
    
    def _detect_gpu(self) -> None:
        """Detect GPU availability and log details"""
        try:
            # Check NVIDIA GPU
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                gpu_lines = result.stdout.strip().split('\n')
                for i, line in enumerate(gpu_lines):
                    parts = line.split(', ')
                    if len(parts) >= 4:
                        self.gpu_info[f'gpu_{i}'] = {
                            'name': parts[0],
                            'memory_total_mb': int(parts[1]),
                            'memory_used_mb': int(parts[2]),
                            'utilization_percent': int(parts[3])
                        }
                
                self.gpu_available = True
                logger.info("🚀 GPU DETECTION SUCCESS")
                for gpu_id, info in self.gpu_info.items():
                    logger.info(f"   • {gpu_id.upper()}: {info['name']}")
                    logger.info(f"     - Memory: {info['memory_used_mb']}/{info['memory_total_mb']} MB")
                    logger.info(f"     - Utilization: {info['utilization_percent']}%")
            else:
                logger.warning("❌ nvidia-smi command failed")
                self.gpu_available = False
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"❌ GPU DETECTION FAILED: {e}")
            self.gpu_available = False
        
        # Log final GPU status
        if self.gpu_available:
            logger.info("✅ GPU AVAILABLE - Will use GPU acceleration")
        else:
            logger.warning("⚠️  GPU NOT AVAILABLE - Will use CPU fallback")
    
    def _setup_ollama_gpu(self) -> None:
        """Setup Ollama to use GPU if available"""
        try:
            if self.gpu_available:
                logger.info("🔧 Configuring Ollama for GPU usage...")
                
                # Stop any existing Ollama processes
                subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)
                time.sleep(2)
                
                # Set CUDA environment variables
                env = os.environ.copy()
                env['CUDA_VISIBLE_DEVICES'] = '0'
                env['OLLAMA_GPU_LAYERS'] = '999'  # Use all GPU layers
                
                # Start Ollama with GPU support
                logger.info("🚀 Starting Ollama with GPU support...")
                subprocess.Popen(['ollama', 'serve'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(5)  # Give Ollama time to start
                
                logger.info("✅ Ollama configured for GPU usage")
            else:
                logger.info("🔧 Starting Ollama in CPU mode...")
                subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)
                time.sleep(2)
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"❌ Failed to setup Ollama: {e}")
    
    def _verify_ollama_status(self) -> None:
        """Verify Ollama is running and check model status"""
        try:
            # Test Ollama connection
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                logger.info("✅ Ollama is running")
                logger.info(f"📋 Available models: {model_names}")
                
                if self.text_model in model_names:
                    logger.info(f"✅ Target model '{self.text_model}' is available")
                else:
                    logger.warning(f"⚠️  Target model '{self.text_model}' not found")
                    
                # Check if model is loaded on GPU
                if self.gpu_available:
                    self._check_model_gpu_status()
            else:
                logger.error(f"❌ Ollama not responding: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to verify Ollama status: {e}")
    
    def _check_model_gpu_status(self) -> None:
        """Check if model is loaded on GPU"""
        try:
            # Make a simple request to load the model
            test_payload = {
                "model": self.text_model,
                "prompt": "Test",
                "stream": False
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=test_payload, timeout=30)
            
            if response.status_code == 200:
                # Check GPU memory usage after model load
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    current_memory = int(result.stdout.strip())
                    initial_memory = self.gpu_info.get('gpu_0', {}).get('memory_used_mb', 0)
                    
                    if current_memory > initial_memory + 1000:  # More than 1GB increase
                        logger.info(f"🎯 Model loaded on GPU - Memory usage: {current_memory} MB")
                    else:
                        logger.warning(f"⚠️  Model may be running on CPU - Memory usage: {current_memory} MB")
                        
        except Exception as e:
            logger.warning(f"⚠️  Could not verify model GPU status: {e}")
    
    def extract_text_from_pdf_ocr(self, pdf_path: str) -> str:
        """Extract text using traditional OCR (Tesseract)"""
        try:
            logger.info("🔄 Converting PDF to images for OCR...")
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)
            
            extracted_text = ""
            for i, image in enumerate(images):
                logger.info(f"📄 Processing page {i+1}...")
                
                # Use Tesseract OCR with German and English
                text = pytesseract.image_to_string(
                    image, 
                    lang='eng+deu',  # English + German
                    config='--psm 6'  # Uniform block of text
                )
                extracted_text += f"\n--- PAGE {i+1} ---\n{text}\n"
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return ""
    
    def extract_text_from_pdf_direct(self, pdf_path: str) -> str:
        """Extract text directly from PDF (for digital PDFs)"""
        try:
            logger.info("📖 Extracting text directly from PDF...")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(min(3, len(pdf_reader.pages))):  # First 3 pages
                    page = pdf_reader.pages[page_num]
                    text += f"\n--- PAGE {page_num+1} ---\n{page.extract_text()}\n"
                return text.strip()
        except Exception as e:
            logger.error(f"❌ Direct PDF extraction failed: {e}")
            return ""
    
    def extract_text_hybrid(self, pdf_path: str) -> str:
        """Hybrid text extraction: try direct first, then OCR"""
        logger.info(f"🔍 Extracting text from: {Path(pdf_path).name}")
        
        # Try direct extraction first (faster for digital PDFs)
        direct_text = self.extract_text_from_pdf_direct(pdf_path)
        if direct_text and len(direct_text.strip()) > 100:
            logger.info("✅ Used direct PDF text extraction")
            return direct_text
        
        # Fallback to OCR for scanned/image PDFs
        logger.info("🔄 Direct extraction insufficient, using OCR...")
        ocr_text = self.extract_text_from_pdf_ocr(pdf_path)
        if ocr_text:
            logger.info("✅ Used OCR text extraction")
            return ocr_text
        
        logger.error("❌ Both extraction methods failed")
        return ""
    
    def call_text_llm(self, prompt: str, timeout: int = 120) -> Tuple[Optional[str], Dict[str, Any]]:
        """Call text-only LLM via Ollama with GPU monitoring"""
        start_time = time.time()
        gpu_stats_before = self._get_gpu_stats()
        
        try:
            payload = {
                "model": self.text_model,
                "prompt": prompt,
                "stream": False
            }
            
            logger.info(f"🤖 Calling LLM with GPU: {self.gpu_available}")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate", 
                json=payload, 
                timeout=timeout
            )
            
            processing_time = time.time() - start_time
            gpu_stats_after = self._get_gpu_stats()
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')
                
                # Log performance metrics
                stats = {
                    "processing_time": round(processing_time, 2),
                    "gpu_used": self.gpu_available,
                    "model": self.text_model,
                    "gpu_stats_before": gpu_stats_before,
                    "gpu_stats_after": gpu_stats_after
                }
                
                logger.info(f"✅ LLM processing completed in {processing_time:.2f}s")
                if self.gpu_available:
                    memory_diff = gpu_stats_after.get('memory_used', 0) - gpu_stats_before.get('memory_used', 0)
                    logger.info(f"🎯 GPU memory change: +{memory_diff} MB")
                
                return llm_response, stats
            else:
                logger.error(f"❌ LLM API Error: {response.status_code}")
                return None, {"error": f"HTTP {response.status_code}", "processing_time": processing_time}
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ LLM call failed: {e}")
            return None, {"error": str(e), "processing_time": processing_time}
    
    def _get_gpu_stats(self) -> Dict[str, Any]:
        """Get current GPU statistics"""
        if not self.gpu_available:
            return {}
        
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                return {
                    "memory_used": int(parts[0]),
                    "utilization": int(parts[1])
                }
        except Exception:
            pass
        
        return {}
    
    def ExtractInvoiceDetailsFromPdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Enhanced invoice extraction with GPU awareness and comprehensive logging
        """
        logger.info(f"\n🎯 ExtractInvoiceDetailsFromPdf: {Path(pdf_path).name}")
        logger.info(f"🔧 GPU Mode: {'ENABLED' if self.gpu_available else 'DISABLED (CPU fallback)'}")
        
        # Step 1: Extract text
        extracted_text = self.extract_text_hybrid(pdf_path)
        if not extracted_text:
            return {"error": "Could not extract text from PDF"}
        
        # Step 2: Use LLM to structure the data
        prompt = f"""Analyze the following invoice text and extract key information. Return ONLY a valid JSON object with these fields:

{{
  "invoice_date": "YYYY-MM-DD format or empty string",
  "invoice_number": "invoice number or empty string", 
  "issuer_name": "company/issuer name or empty string",
  "issuer_address": "issuer address or empty string",
  "issuer_vat": "issuer VAT number or empty string",
  "recipient_name": "recipient/customer name or empty string", 
  "recipient_address": "recipient address or empty string",
  "recipient_vat": "recipient VAT number or empty string",
  "amount": "total amount as number or empty string",
  "currency": "currency code (EUR, USD, etc.) or empty string",
  "description": "brief description of goods/services or empty string",
  "language": "German or English"
}}

Invoice text:
{extracted_text[:3000]}

Return only the JSON object, no other text:"""

        logger.info("🤖 Processing with LLM...")
        
        llm_response, stats = self.call_text_llm(prompt, timeout=120)
        
        if not llm_response:
            error_result = {"error": "LLM processing failed"}
            error_result.update(stats)
            return error_result
        
        # Try to parse JSON response
        try:
            # Clean the response (remove any markdown formatting)
            clean_response = llm_response.strip()
            if clean_response.startswith('```'):
                clean_response = clean_response.split('\n', 1)[1]
            if clean_response.endswith('```'):
                clean_response = clean_response.rsplit('\n', 1)[0]
            
            invoice_data = json.loads(clean_response)
            
            # Add processing metadata
            invoice_data.update({
                "processing_time": stats.get("processing_time", 0),
                "extraction_method": "gpu_aware_hybrid_ocr_llm",
                "model_used": self.text_model,
                "gpu_accelerated": self.gpu_available,
                "gpu_stats": stats
            })
            
            logger.info(f"✅ Structured data extracted in {stats.get('processing_time', 0):.2f}s")
            if self.gpu_available:
                logger.info("🚀 Processing completed with GPU acceleration")
            else:
                logger.info("🐌 Processing completed with CPU fallback")
            
            return invoice_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            return {
                "error": "Could not parse LLM response as JSON",
                "raw_response": llm_response[:500],
                "processing_time": stats.get("processing_time", 0),
                "gpu_accelerated": self.gpu_available
            }
    
    def ExtractMarkdownFromPdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Enhanced markdown extraction with GPU awareness
        """
        logger.info(f"\n📝 ExtractMarkdownFromPdf: {Path(pdf_path).name}")
        logger.info(f"🔧 GPU Mode: {'ENABLED' if self.gpu_available else 'DISABLED (CPU fallback)'}")
        
        # Step 1: Extract text
        extracted_text = self.extract_text_hybrid(pdf_path)
        if not extracted_text:
            return {"error": "Could not extract text from PDF"}
        
        # Step 2: Convert to structured Markdown
        prompt = f"""Convert the following invoice text into well-structured Markdown format. 
Organize the information with clear headers and formatting:

# Invoice Document

## Company Information
- **Issuer**: [Company Name]
- **Address**: [Address]
- **VAT Number**: [VAT if available]

## Invoice Details
- **Invoice Number**: [Number]
- **Date**: [Date]
- **Amount**: [Amount] [Currency]

## Description
[Brief description of goods/services]

## Recipient
- **Name**: [Recipient name]
- **Address**: [Recipient address if available]

---

Invoice text to convert:
{extracted_text[:3000]}

Return the structured Markdown:"""

        logger.info("🤖 Converting to Markdown with LLM...")
        
        llm_response, stats = self.call_text_llm(prompt, timeout=120)
        
        if not llm_response:
            error_result = {"error": "LLM processing failed"}
            error_result.update(stats)
            return error_result
        
        result = {
            "success": True,
            "markdown": llm_response,
            "processing_time": stats.get("processing_time", 0),
            "extraction_method": "gpu_aware_hybrid_ocr_llm",
            "model_used": self.text_model,
            "gpu_accelerated": self.gpu_available,
            "gpu_stats": stats
        }
        
        logger.info(f"✅ Markdown conversion completed in {stats.get('processing_time', 0):.2f}s")
        if self.gpu_available:
            logger.info("🚀 Processing completed with GPU acceleration")
        else:
            logger.info("🐌 Processing completed with CPU fallback")
        
        return result

def test_gpu_aware_solution():
    """Test the GPU-aware OCR solution"""
    logger.info("🧪 Testing GPU-Aware OCR Solution")
    logger.info("=" * 60)
    
    processor = GPUAwareInvoiceOCRProcessor()
    
    # Test with sample PDF
    test_pdf = "input/pdffile11101.pdf"
    
    if not os.path.exists(test_pdf):
        logger.error(f"❌ Test PDF not found: {test_pdf}")
        return
    
    # Test invoice extraction
    result = processor.ExtractInvoiceDetailsFromPdf(test_pdf)
    
    if "error" in result:
        logger.error(f"❌ Test failed: {result['error']}")
    else:
        logger.info("✅ Test completed successfully!")
        logger.info(f"   • GPU Accelerated: {result.get('gpu_accelerated', False)}")
        logger.info(f"   • Processing Time: {result.get('processing_time', 0):.2f}s")
        logger.info(f"   • Issuer: {result.get('issuer_name', 'N/A')}")

if __name__ == "__main__":
    test_gpu_aware_solution() 