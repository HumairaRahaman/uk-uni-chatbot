#!/usr/bin/env python
"""
Simple test to check if Firecrawl can scrape Wikipedia
"""
import os
import sys
from dotenv import load_dotenv

# Add the project directory to path
sys.path.insert(0, '/Users/strativ/Desktop/mine/chat-bot')

# Set environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')

# Load environment variables
load_dotenv()

from chatbot.firecrawl_service import FirecrawlService

def test_firecrawl():
    print("Testing Firecrawl service...")
    print("-" * 50)

    try:
        # Initialize service
        print("1. Initializing FirecrawlService...")
        service = FirecrawlService()
        print("Service initialized successfully")

        # Test scraping
        url = "https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom"
        print(f"\n2. Scraping URL: {url}")
        result = service.scrape_url(url)

        if result:
            print("Scraping successful!")
            print(f"\nResult keys: {result.keys()}")

            if 'markdown' in result:
                markdown_content = result['markdown']
                print(f"Markdown content length: {len(markdown_content)} characters")
                print(f"\nFirst 500 characters:")
                print(markdown_content[:500])

            if 'metadata' in result:
                print(f"\nMetadata: {result['metadata']}")
        else:
            print("Scraping failed - returned None")

    except Exception as e:
        print(f"ßError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_firecrawl()

