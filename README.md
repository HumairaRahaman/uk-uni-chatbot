# UK Universities Chatbot with Firecrawl Integration

A Django-based chatbot that can answer questions about UK universities using RAG (Retrieval-Augmented Generation) with Claude AI. Now enhanced with Firecrawl for web scraping capabilities.

## Features

- 💬 Interactive chatbot interface
- 📚 RAG-based question answering using local data
- 🌐 **Web scraping with Firecrawl** (NEW!)
- 🔍 **Web search integration** (NEW!)
- 🧠 Vector database for knowledge storage (ChromaDB)
- 🎯 Semantic search with sentence transformers
- 📊 Knowledge base statistics and management

## New Firecrawl Capabilities

### 1. Web Content Scraping
- Scrape individual web pages or entire websites
- Automatically extract and clean content
- Add scraped content to your knowledge base
- Support for markdown and HTML format extraction

### 2. Web Search Integration
- Search the web for relevant content
- Automatically scrape and add top search results
- Expand your knowledge base with fresh web content

### 3. Content Management
- View knowledge base statistics (file vs web content)
- Clear web content while preserving local files
- Source tracking for all content

## Installation

1. **Clone and install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

Required API keys:
- `ANTHROPIC_API_KEY`: Get from [Anthropic](https://console.anthropic.com/)
- `FIRECRAWL_API_KEY`: Get from [Firecrawl](https://firecrawl.dev/)

3. **Run the server:**
```bash
python manage.py runserver
```

## API Endpoints

### Chat Endpoints
- `POST /chat/` - Send a message to the chatbot
- `POST /reload/` - Reload data from local files

### Firecrawl Endpoints (NEW)
- `POST /add-web-content/` - Add content from a web URL
- `POST /add-search-content/` - Add content from web search results
- `GET /knowledge-stats/` - Get knowledge base statistics
- `POST /clear-web-content/` - Clear all web-scraped content
- `POST /search-sources/` - Search with source information

## Usage Examples

### Adding Web Content
```javascript
// Add a single webpage
fetch('/add-web-content/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        url: 'https://example-university.edu/admissions', 
        max_pages: 1 
    })
});

// Crawl multiple pages from a website
fetch('/add-web-content/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        url: 'https://example-university.edu', 
        max_pages: 10 
    })
});
```

### Adding Search Results
```javascript
// Search and add relevant content
fetch('/add-search-content/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        query: 'UK university application deadlines 2024', 
        max_results: 5 
    })
});
```

## Web Interface Features

The updated web interface includes:

1. **Add Web Content** - Scrape content from specific URLs
2. **Add Search Results** - Search the web and add relevant content
3. **Clear Web Content** - Remove all web-scraped content
4. **Knowledge Base Stats** - View content statistics
5. **Real-time Stats** - See how many chunks are from files vs web

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Firecrawl     │    │  Enhanced RAG    │    │   ChromaDB      │
│   Service       │────│    Service       │────│  Vector Store   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Web Scraping   │    │  Content Mgmt    │    │  Semantic       │
│  & Search       │    │  & Processing    │    │  Search         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Dependencies

- `django==4.2` - Web framework
- `chromadb==1.3.4` - Vector database
- `sentence-transformers==5.1.2` - Embeddings
- `anthropic==0.73.0` - Claude API
- `firecrawl-py==4.8.0` - Web scraping (NEW!)
- `python-dotenv==1.0.0` - Environment variables
- `beautifulsoup4==4.12.3` - HTML parsing

## File Structure

```
chatbot/
├── firecrawl_service.py     # Firecrawl integration (NEW)
├── enhanced_rag_service.py  # Enhanced RAG with web content (NEW)
├── chatbot_service.py       # Claude AI integration
├── rag_service.py          # Original RAG service
├── views.py                # Django views with new endpoints
├── urls.py                 # URL routing
└── models.py              # Django models

templates/chatbot/
└── index.html             # Enhanced UI with Firecrawl features
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-anthropic-key
FIRECRAWL_API_KEY=your-firecrawl-key

# Optional
TOKENIZERS_PARALLELISM=false
SECRET_KEY=your-django-secret-key
```

## Troubleshooting

### Common Issues

1. **"FIRECRAWL_API_KEY environment variable is required"**
   - Make sure you've set your Firecrawl API key in `.env`

2. **"Failed to scrape content"**
   - Check if the URL is accessible
   - Verify your Firecrawl API key is valid
   - Some websites may block scraping

3. **TokenizersParallelism warnings**
   - Set `TOKENIZERS_PARALLELISM=false` in your environment

### Getting API Keys

1. **Anthropic API Key:**
   - Go to [console.anthropic.com](https://console.anthropic.com/)
   - Create an account and get your API key

2. **Firecrawl API Key:**
   - Go to [firecrawl.dev](https://firecrawl.dev/)
   - Sign up and get your API key
   - Free tier includes 500 credits per month

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
