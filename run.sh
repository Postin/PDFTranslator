#!/bin/bash
# Simple launcher for PDF Translator Web UI

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "📄 PDF Translator"
echo "================="

# Check for .env
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Create .env with your OpenAI API key:"
    echo '  echo "OPENAI_API_KEY=your-key-here" > .env'
    exit 1
fi

# Check for virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check dependencies
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${RED}Dependencies not installed${NC}"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}Starting web interface...${NC}"
echo "Open http://localhost:8501 in your browser"
echo ""

streamlit run app.py

