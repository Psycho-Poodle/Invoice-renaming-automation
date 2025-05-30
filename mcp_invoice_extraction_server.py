#!/usr/bin/env python3
"""
MCP Invoice Details Extraction Server
Wraps our GPU-aware OCR solution to provide invoice extraction tools via MCP protocol
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent
from gpu_aware_ocr_solution import GPUAwareInvoiceOCRProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the GPU-aware OCR processor
ocr_processor = GPUAwareInvoiceOCRProcessor()

# Create MCP server
server = Server("invoice-extraction-server")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available invoice extraction tools"""
    return [
        Tool(
            name="ExtractInvoiceDetailsFromPdf",
            description="Extract structured invoice data from PDF file as JSON with GPU acceleration",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to analyze"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="ExtractMarkdownFromPdf", 
            description="Convert PDF invoice to structured Markdown format with GPU acceleration",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to convert"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="ExtractTextFromPdf",
            description="Extract raw text from PDF using hybrid OCR approach",
            inputSchema={
                "type": "object", 
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to extract text from"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="GetGPUStatus",
            description="Get current GPU status and availability information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "ExtractInvoiceDetailsFromPdf":
            pdf_path = arguments.get("pdf_path")
            if not pdf_path:
                return [TextContent(type="text", text=json.dumps({"error": "pdf_path is required"}))]
            
            logger.info(f"Extracting invoice details from: {pdf_path}")
            result = ocr_processor.ExtractInvoiceDetailsFromPdf(pdf_path)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "ExtractMarkdownFromPdf":
            pdf_path = arguments.get("pdf_path")
            if not pdf_path:
                return [TextContent(type="text", text=json.dumps({"error": "pdf_path is required"}))]
            
            logger.info(f"Converting PDF to Markdown: {pdf_path}")
            result = ocr_processor.ExtractMarkdownFromPdf(pdf_path)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "ExtractTextFromPdf":
            pdf_path = arguments.get("pdf_path")
            if not pdf_path:
                return [TextContent(type="text", text=json.dumps({"error": "pdf_path is required"}))]
            
            logger.info(f"Extracting raw text from: {pdf_path}")
            text = ocr_processor.extract_text_hybrid(pdf_path)
            result = {
                "success": True,
                "text": text,
                "length": len(text),
                "gpu_accelerated": ocr_processor.gpu_available
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "GetGPUStatus":
            gpu_stats = ocr_processor._get_gpu_stats()
            result = {
                "gpu_available": ocr_processor.gpu_available,
                "gpu_info": ocr_processor.gpu_info,
                "current_stats": gpu_stats,
                "model_used": ocr_processor.text_model
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the MCP server"""
    logger.info("Starting GPU-Aware MCP Invoice Extraction Server...")
    logger.info(f"GPU Available: {ocr_processor.gpu_available}")
    
    # Import and run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 