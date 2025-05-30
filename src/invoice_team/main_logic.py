from typing import Dict, Any
import os
import sys
import logging
import re

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import agents with absolute paths
from agents.coordination_agent import CoordinationAgent
from agents.analyze_invoice_agent import AnalyzeInvoiceAgent
from agents.file_system_agent import FileSystemAccessAgent
from agents.file_renaming_agent import FileRenamingAgent
from agents.review_agent import ReviewAgent

def setup_llm_config() -> Dict[str, Any]:
    """Set up LLM configuration for Ollama."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    return {
        "config_list": [
            {
                "model": model_name,
                "base_url": f"{ollama_url}/v1",
                "api_key": "ollama",  # Ollama doesn't require real API key
                "api_type": "openai",  # Use OpenAI-compatible API
            }
        ],
        "temperature": 0.1,
    }

def parse_prompt_for_files(prompt: str) -> Dict[str, str]:
    """
    Parse the prompt to extract file paths and directories.
    
    Args:
        prompt: The user prompt containing file and directory information
        
    Returns:
        Dictionary with extracted paths
    """
    result = {
        "input_file": None,
        "codes_csv": None,
        "output_dir": "output"
    }
    
    # Pattern to extract PDF file name - more precise
    pdf_pattern = r'pdf file["\s]*["\']?([a-zA-Z0-9_\-\.]+\.pdf)["\']?'
    pdf_match = re.search(pdf_pattern, prompt, re.IGNORECASE)
    if pdf_match:
        pdf_file = pdf_match.group(1).strip()
        
        # Look for directory context before the PDF file
        dir_pattern = r'located in["\s]*["\']?([a-zA-Z0-9_\-\/\\]+)["\']?[^"\']*folder'
        dir_match = re.search(dir_pattern, prompt, re.IGNORECASE)
        if dir_match:
            directory = dir_match.group(1).strip()
            result["input_file"] = f"{directory}/{pdf_file}"
        else:
            result["input_file"] = f"input/{pdf_file}"
    
    # Pattern to extract CSV file name - more precise
    csv_pattern = r'CSV file["\s]*["\']?([a-zA-Z0-9_\-\.]+\.csv)["\']?'
    csv_match = re.search(csv_pattern, prompt, re.IGNORECASE)
    if csv_match:
        csv_file = csv_match.group(1).strip()
        
        # Look for CSV directory context
        csv_dir_pattern = r'CSV file[^"\']*["\']?[^"\']*["\']?[^"\']*located in["\s]*["\']?([a-zA-Z0-9_\-\/\\]+)["\']?'
        csv_dir_match = re.search(csv_dir_pattern, prompt, re.IGNORECASE)
        if csv_dir_match:
            directory = csv_dir_match.group(1).strip()
            result["codes_csv"] = f"{directory}/{csv_file}"
        else:
            result["codes_csv"] = f"input/{csv_file}"
    
    # Pattern to extract output directory
    output_pattern = r'output to["\s]*["\']?([a-zA-Z0-9_\-\/\\]+)["\']?'
    output_match = re.search(output_pattern, prompt, re.IGNORECASE)
    if output_match:
        result["output_dir"] = output_match.group(1).strip()
    
    return result

def process_invoice_prompt(prompt: str) -> Dict[str, Any]:
    """
    Process the invoice renaming prompt and return the result.
    Parse the prompt to extract file and CSV paths, then run the invoice renaming logic using the agents and Ollama.
    """
    # Parse the prompt to extract file paths
    parsed_files = parse_prompt_for_files(prompt)
    
    input_file = parsed_files["input_file"]
    codes_csv = parsed_files["codes_csv"]
    output_dir = parsed_files["output_dir"]
    
    # Fallback to defaults if parsing failed
    if not input_file:
        input_file = "input/pdffile11101.pdf"  # Use your actual file
    if not codes_csv:
        codes_csv = "input/accounting_codes.csv"
    
    # Validate input
    if not os.path.exists(input_file):
        return {"error": f"Input file '{input_file}' does not exist"}
    if not os.path.exists(codes_csv):
        return {"error": f"Accounting codes CSV file '{codes_csv}' does not exist"}
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    llm_config = setup_llm_config()

    coordination_agent = CoordinationAgent(
        name="CoordinationAgent",
        system_message="You are the coordination agent for the invoice processing system. You orchestrate the workflow between other agents.",
        llm_config=llm_config,
    )
    analyze_agent = AnalyzeInvoiceAgent(
        name="AnalyzeInvoiceAgent",
        system_message="You are the analysis agent for invoice PDFs. You extract text and data from invoices using Ollama.",
        llm_config=llm_config,
    )
    file_system_agent = FileSystemAccessAgent(
        name="FileSystemAccessAgent",
        system_message="You are the file system agent. You handle file operations like reading PDFs and saving renamed files.",
        llm_config=llm_config,
    )
    file_renaming_agent = FileRenamingAgent(
        name="FileRenamingAgent",
        system_message="You are the file renaming agent. You apply standardized naming rules to invoice files.",
        llm_config=llm_config,
    )
    review_agent = ReviewAgent(
        name="ReviewAgent",
        system_message="You are the review agent. You validate renamed files and generate reports.",
        llm_config=llm_config,
    )

    user_prompt = f"Read and analyze {input_file} using {codes_csv} and output to {output_dir}"
    
    try:
        coordination_agent.process_user_prompt(
            user_prompt,
            analyze_agent,
            file_system_agent,
            file_renaming_agent
        )
        all_valid, validation_report = review_agent.review_output_directory(output_dir)
        
        # Extract the actual renamed file from the output directory
        renamed_files = []
        if os.path.exists(output_dir):
            renamed_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        
        return {
            "success": True,
            "input_file": input_file,
            "codes_csv": codes_csv,
            "output_dir": output_dir,
            "renamed_files": renamed_files,
            "validation_report": validation_report,
            "all_valid": all_valid
        }
    except Exception as e:
        return {
            "error": f"Processing failed: {str(e)}",
            "input_file": input_file,
            "codes_csv": codes_csv
        } 