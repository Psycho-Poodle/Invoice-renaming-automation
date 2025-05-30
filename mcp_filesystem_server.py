#!/usr/bin/env python3
"""
MCP File System Server
Handles file operations, accounting codes, and invoice renaming logic
"""

import asyncio
import json
import os
import shutil
import csv
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import re
from mcp.server import Server
from mcp.types import Tool, TextContent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("filesystem-server")

class AccountingCodeManager:
    """Manages accounting codes and invoice renaming logic"""
    
    def __init__(self):
        self.codes = {}
        self.codes_loaded = False
    
    def load_accounting_codes(self, csv_path: str) -> bool:
        """Load accounting codes from CSV file"""
        try:
            self.codes = {}
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    code = row.get('Accounting Code', '').strip()
                    short_desc = row.get('Short descriptoin for finance reports', '').strip()
                    long_desc = row.get('Long description', '').strip()
                    
                    if code:
                        self.codes[code] = {
                            'short_description': short_desc,
                            'long_description': long_desc
                        }
            
            self.codes_loaded = True
            logger.info(f"Loaded {len(self.codes)} accounting codes from {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load accounting codes: {e}")
            return False
    
    def find_matching_code(self, invoice_data: Dict[str, Any]) -> Optional[str]:
        """Find the best matching accounting code for invoice data"""
        if not self.codes_loaded:
            return None
        
        # Extract key information
        issuer = invoice_data.get('issuer_name', '').lower()
        description = invoice_data.get('description', '').lower()
        
        # Simple matching logic - can be enhanced
        if any(term in issuer or term in description for term in ['google', 'azure', 'aws', 'cloud']):
            return 'OND295'  # IT - Infra - Cloud Google
        elif any(term in issuer or term in description for term in ['microsoft', 'office', 'teams']):
            return 'OND295'  # IT - Infra - Cloud Google (includes Microsoft Azure)
        elif any(term in issuer or term in description for term in ['restaurant', 'lunch', 'dinner', 'meal']):
            return 'OND300'  # Sales
        elif any(term in issuer or term in description for term in ['office', 'supplies', 'paper', 'coffee']):
            return 'OND532'  # Operations Office Supplies
        elif any(term in issuer or term in description for term in ['internet', 'mobile', 'phone', 'laptop']):
            return 'OND533'  # Operations Office IT
        elif any(term in issuer or term in description for term in ['rent', 'energy', 'heating']):
            return 'OND534'  # Operations Office Rent
        else:
            return 'OND290'  # Default: IT - Operations
    
    def generate_filename(self, invoice_data: Dict[str, Any], accounting_code: str) -> str:
        """Generate standardized filename from invoice data"""
        # Extract and format date
        date_str = invoice_data.get('invoice_date', '')
        if date_str:
            try:
                # Try to parse various date formats
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        formatted_date = date_obj.strftime('%Y%m%d')
                        break
                    except ValueError:
                        continue
                else:
                    formatted_date = datetime.now().strftime('%Y%m%d')
            except:
                formatted_date = datetime.now().strftime('%Y%m%d')
        else:
            formatted_date = datetime.now().strftime('%Y%m%d')
        
        # Extract company name
        company = invoice_data.get('issuer_name', 'Unknown')
        # Clean company name
        company = re.sub(r'[^\w\s-]', '', company).strip()
        company = re.sub(r'\s+', ' ', company)
        if len(company) > 30:
            company = company[:30].strip()
        
        # Extract description
        description = invoice_data.get('description', 'Invoice')
        description = re.sub(r'[^\w\s-]', '', description).strip()
        description = re.sub(r'\s+', ' ', description)
        if len(description) > 40:
            description = description[:40].strip()
        
        # Extract invoice number
        invoice_number = invoice_data.get('invoice_number', '')
        if invoice_number:
            invoice_number = re.sub(r'[^\w-]', '', invoice_number)
            if len(invoice_number) > 20:
                invoice_number = invoice_number[:20]
        else:
            invoice_number = 'NoNumber'
        
        # Format: YYYYMMDD ACCOUNTING_CODE COMPANY - Description Invoice Nr. [Number].pdf
        filename = f"{formatted_date} {accounting_code} {company} - {description} Invoice Nr. {invoice_number}.pdf"
        
        # Clean filename for filesystem compatibility
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', ' ', filename)
        
        return filename

# Initialize accounting code manager
accounting_manager = AccountingCodeManager()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available file system tools"""
    return [
        Tool(
            name="LoadAccountingCodes",
            description="Load accounting codes from CSV file",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_path": {
                        "type": "string",
                        "description": "Path to the accounting codes CSV file"
                    }
                },
                "required": ["csv_path"]
            }
        ),
        Tool(
            name="GetAccountingCodes",
            description="Get all loaded accounting codes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="FindMatchingAccountingCode",
            description="Find the best matching accounting code for invoice data",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_data": {
                        "type": "object",
                        "description": "Invoice data object with issuer_name, description, etc."
                    }
                },
                "required": ["invoice_data"]
            }
        ),
        Tool(
            name="GenerateInvoiceFilename",
            description="Generate standardized filename from invoice data and accounting code",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_data": {
                        "type": "object",
                        "description": "Invoice data object"
                    },
                    "accounting_code": {
                        "type": "string",
                        "description": "Accounting code to use"
                    }
                },
                "required": ["invoice_data", "accounting_code"]
            }
        ),
        Tool(
            name="CopyAndRenameFile",
            description="Copy a file to output directory with new name",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "output_dir": {
                        "type": "string", 
                        "description": "Output directory"
                    },
                    "new_filename": {
                        "type": "string",
                        "description": "New filename"
                    }
                },
                "required": ["source_path", "output_dir", "new_filename"]
            }
        ),
        Tool(
            name="ListFiles",
            description="List files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list"
                    },
                    "extension": {
                        "type": "string",
                        "description": "File extension filter (optional)"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="FileExists",
            description="Check if a file exists",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path to check"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "LoadAccountingCodes":
            csv_path = arguments.get("csv_path")
            success = accounting_manager.load_accounting_codes(csv_path)
            result = {
                "success": success,
                "codes_count": len(accounting_manager.codes) if success else 0,
                "csv_path": csv_path
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "GetAccountingCodes":
            result = {
                "success": accounting_manager.codes_loaded,
                "codes": accounting_manager.codes,
                "count": len(accounting_manager.codes)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "FindMatchingAccountingCode":
            invoice_data = arguments.get("invoice_data", {})
            matching_code = accounting_manager.find_matching_code(invoice_data)
            result = {
                "success": True,
                "accounting_code": matching_code,
                "invoice_issuer": invoice_data.get('issuer_name', ''),
                "invoice_description": invoice_data.get('description', '')
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "GenerateInvoiceFilename":
            invoice_data = arguments.get("invoice_data", {})
            accounting_code = arguments.get("accounting_code", "")
            filename = accounting_manager.generate_filename(invoice_data, accounting_code)
            result = {
                "success": True,
                "filename": filename,
                "accounting_code": accounting_code
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "CopyAndRenameFile":
            source_path = arguments.get("source_path")
            output_dir = arguments.get("output_dir")
            new_filename = arguments.get("new_filename")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy and rename file
            destination_path = os.path.join(output_dir, new_filename)
            shutil.copy2(source_path, destination_path)
            
            result = {
                "success": True,
                "source_path": source_path,
                "destination_path": destination_path,
                "new_filename": new_filename
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "ListFiles":
            directory = arguments.get("directory")
            extension = arguments.get("extension")
            
            if not os.path.exists(directory):
                result = {"error": f"Directory does not exist: {directory}"}
                return [TextContent(type="text", text=json.dumps(result))]
            
            files = []
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if not extension or file.endswith(extension):
                        files.append(file)
            
            result = {
                "success": True,
                "directory": directory,
                "files": files,
                "count": len(files)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "FileExists":
            file_path = arguments.get("file_path")
            exists = os.path.exists(file_path)
            result = {
                "success": True,
                "file_path": file_path,
                "exists": exists
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP File System Server...")
    
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