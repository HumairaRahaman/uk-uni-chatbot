#!/bin/bash

echo "🎓 UK Universities Chatbot with Firecrawl Setup"
echo "=============================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Created .env file. Please edit it with your API keys:"
    echo "   - ANTHROPIC_API_KEY (get from console.anthropic.com)"
    echo "   - FIRECRAWL_API_KEY (get from firecrawl.dev)"
    echo ""
else
    echo ".env file already exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "Virtual environment created"
    echo "Activate it with: source venv/bin/activate"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: python manage.py runserver"
echo "3. Open: http://127.0.0.1:8000"
echo ""
echo "New Firecrawl features:"
echo "   • Scrape web content and add to knowledge base"
echo "   • Search the web and add relevant results"
echo "   • Manage web vs file content separately"
echo "   • Enhanced chatbot with broader knowledge"
echo ""
echo "Need help? Check README.md for detailed instructions!"
