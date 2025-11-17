#!/usr/bin/env python
"""
Demo script to test Firecrawl functionality without Anthropic API
Run this to test your Firecrawl integration independently.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
django.setup()

from chatbot.firecrawl_service import FirecrawlService
from chatbot.enhanced_rag_service import EnhancedRAGService

def test_firecrawl():
    """Test Firecrawl functionality"""
    print("🔥 Testing Firecrawl Integration")
    print("=" * 40)

    try:
        # Initialize services
        print("1. Initializing Firecrawl service...")
        firecrawl = FirecrawlService()
        print("Firecrawl service initialized successfully!")

        # Test URL scraping
        print("\n2. Testing URL scraping...")
        test_url = "https://www.cam.ac.uk/about-the-university"  # Cambridge University info

        result = firecrawl.scrape_url(test_url)
        if result and 'markdown' in result:
            content_preview = result['markdown'][:200] + "..." if len(result['markdown']) > 200 else result['markdown']
            print(f"Successfully scraped content from {test_url}")
            print(f"Content preview: {content_preview}")

            # Test enhanced RAG service
            print("\n3. Testing Enhanced RAG service...")
            data_file = project_root / 'chatbot' / 'universities_data.txt'
            rag_service = EnhancedRAGService(str(data_file))

            # Add scraped content to knowledge base
            print("4. Adding scraped content to knowledge base...")
            success = rag_service.add_web_content(test_url)

            if success:
                print("Content added to knowledge base!")

                # Get stats
                stats = rag_service.get_stats()
                print(f"Knowledge base stats: {stats}")

                # Test search
                print("\n5. Testing search functionality...")
                search_results = rag_service.search("Cambridge University", n_results=2)
                if search_results:
                    print(f"Found {len(search_results)} relevant results")
                    for i, result in enumerate(search_results, 1):
                        preview = result[:100] + "..." if len(result) > 100 else result
                        print(f"   Result {i}: {preview}")
                else:
                    print("No search results found")
            else:
                print("Failed to add content to knowledge base")
        else:
            print("Failed to scrape content")

    except ValueError as e:
        if "FIRECRAWL_API_KEY" in str(e):
            print("Error: Firecrawl API key not found or invalid")
            print("Make sure you have set FIRECRAWL_API_KEY in your .env file")
            print("Get your API key from: https://firecrawl.dev/")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\n" + "=" * 40)
    print("Demo complete!")
    print("\nWhat you can do with just Firecrawl:")
    print("   • Scrape web content and add to knowledge base")
    print("   • Search web and add relevant results")
    print("   • Query your enhanced knowledge base")
    print("   • Get simple retrieval-based responses")
    print("\nTo get AI-powered responses, add ANTHROPIC_API_KEY to .env")

if __name__ == "__main__":
    test_firecrawl()
