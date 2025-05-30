#!/bin/bash

# Batch Invoice Processing Script
# Usage: ./process_folder.sh [folder_path]

echo "📁 Batch Invoice Processing"
echo "=========================="

# Default folder if none specified
FOLDER=${1:-"input/digital"}

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
    echo "❌ Folder not found: $FOLDER"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Count PDF files
PDF_COUNT=$(find "$FOLDER" -name "*.pdf" | wc -l)
echo "📊 Found $PDF_COUNT PDF files in $FOLDER"

if [ $PDF_COUNT -eq 0 ]; then
    echo "❌ No PDF files found in $FOLDER"
    exit 1
fi

# Process each PDF file
PROCESSED=0
FAILED=0

echo ""
echo "🚀 Starting batch processing..."
echo ""

for pdf_file in "$FOLDER"/*.pdf; do
    if [ -f "$pdf_file" ]; then
        filename=$(basename "$pdf_file")
        echo "📄 Processing: $filename"
        
        # Process the invoice
        if python main.py --prompt "Process invoice $pdf_file"; then
            echo "✅ Success: $filename"
            ((PROCESSED++))
        else
            echo "❌ Failed: $filename"
            ((FAILED++))
        fi
        
        echo "---"
    fi
done

echo ""
echo "📊 Batch Processing Complete!"
echo "✅ Processed: $PROCESSED files"
echo "❌ Failed: $FAILED files"
echo "📁 Check output/ folder for results" 