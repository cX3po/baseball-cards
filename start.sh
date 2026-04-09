#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Phil's Baseball Card Finder..."
echo "Open: http://localhost:8505 or http://192.168.1.183:8505"
streamlit run app.py --server.port 8505 --server.headless true
