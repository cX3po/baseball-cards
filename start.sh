#!/bin/bash
# Manual launcher — mirrors the systemd unit (axiom-baseball-cards.service):
# same .venv and port 8503 so a hand-started instance never fights the service.
cd "$(dirname "$0")"
source .venv/bin/activate
echo "Starting the Family Baseball Card Finder..."
echo "Open: http://localhost:8503"
streamlit run app.py --server.port 8503 --server.headless true
