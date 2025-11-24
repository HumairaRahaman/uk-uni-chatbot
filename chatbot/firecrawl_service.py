from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

load_dotenv()

class FirecrawlService:
    def __init__(self):

        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
        self.app = FirecrawlApp(api_key=api_key)

    def scrape_url(self, url, formats=['markdown', 'html']):

        try:
            result = self.app.scrape(
                url,
                formats=formats,
                include_tags=['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article'],
                exclude_tags=['nav', 'footer', 'script', 'style'],
                wait_for=2000  # Wait 2 seconds for dynamic content
            )
            # Convert Pydantic Document object to dict for compatibility
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            return result
        except Exception as e:
            print(f"Error scraping URL {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def crawl_website(self, url, max_pages=10, include_paths=None, exclude_paths=None):

        try:
            params = {
                'limit': max_pages,
                'scrapeOptions': {
                    'formats': ['markdown', 'html'],
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article'],
                    'excludeTags': ['nav', 'footer', 'script', 'style'],
                }
            }

            if include_paths:
                params['includePaths'] = include_paths
            if exclude_paths:
                params['excludePaths'] = exclude_paths

            result = self.app.start_crawl(url, params=params)
            return result
        except Exception as e:
            print(f"Error crawling website {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_crawl_status(self, job_id):

        try:
            return self.app.get_crawl_status(job_id)
        except Exception as e:
            print(f"Error getting crawl status for job {job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def search_web(self, query, max_results=5):

        try:
            result = self.app.search(query, params={'limit': max_results})
            return result
        except Exception as e:
            print(f"Error searching web for query '{query}': {str(e)}")
            return None

    def extract_structured_data(self, url, schema):

        try:
            result = self.app.scrape(
                url,
                params={
                    'formats': ['extract'],
                    'extract': {
                        'schema': schema
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Error extracting structured data from {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
