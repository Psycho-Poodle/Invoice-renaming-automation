from flask import Flask, request, jsonify
import os
import sys
from typing import Any, Dict

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import with absolute path
from src.invoice_team.main_logic import process_invoice_prompt

app = Flask(__name__)

@app.route('/invoice', methods=['POST'])
def invoice():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing prompt'}), 400
    prompt = data['prompt']
    try:
        result = process_invoice_prompt(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 