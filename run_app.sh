#!/bin/bash
echo "Starting Team Tools Calculator..."
echo ""
echo "Open your browser to: http://localhost:5000"
echo "Press Ctrl+C to stop the calculator"
echo ""
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
