import chromadb
from sentence_transformers import SentenceTransformer
from chatbot.firecrawl_service import FirecrawlService
import re
from typing import List, Dict, Optional

class EnhancedRAGService:
    def __init__(self, data_file_path, collection_name="enhanced_knowledge_base"):
        self.data_file = data_file_path
        self.collection_name = collection_name
        self.client = chromadb.Client()

        # Try to get existing collection or create new one
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(name=collection_name)

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.firecrawl = None

        # Initialize with existing data
        self.load_data()

    def get_firecrawl_service(self):
        """Lazy initialize Firecrawl service"""
        if self.firecrawl is None:
            try:
                self.firecrawl = FirecrawlService()
            except ValueError as e:
                print(f"Firecrawl not initialized: {e}")
                self.firecrawl = None
        return self.firecrawl

    def load_data(self):
        """Load and chunk existing data into vector database"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into chunks
            chunks = self._split_into_chunks(content)

            # Add to vector database with source metadata
            for i, chunk in enumerate(chunks):
                chunk_id = f"file_chunk_{i}"
                # Check if chunk already exists
                try:
                    existing = self.collection.get(ids=[chunk_id])
                    if not existing['documents']:
                        self.collection.add(
                            documents=[chunk],
                            ids=[chunk_id],
                            metadatas=[{"source": "local_file", "type": "file"}]
                        )
                except:
                    self.collection.add(
                        documents=[chunk],
                        ids=[chunk_id],
                        metadatas=[{"source": "local_file", "type": "file"}]
                    )
        except FileNotFoundError:
            print(f"Data file {self.data_file} not found. Starting with empty knowledge base.")

    def add_web_content(self, url: str, max_pages: int = 1) -> bool:
        """
        Add web content to the knowledge base using Firecrawl

        Args:
            url (str): URL to scrape and add
            max_pages (int): Maximum pages to crawl if doing full site crawl

        Returns:
            bool: Success status
        """
        firecrawl = self.get_firecrawl_service()
        if not firecrawl:
            return False

        try:
            if max_pages == 1:
                # Single page scrape
                result = firecrawl.scrape_url(url)
                if result and 'markdown' in result:
                    self._add_scraped_content(result, url)
                    return True
            else:
                # Multi-page crawl
                crawl_result = firecrawl.crawl_website(url, max_pages=max_pages)
                if crawl_result and 'jobId' in crawl_result:
                    # You might want to implement polling for job completion
                    # For now, we'll just return the job ID
                    print(f"Crawl job started with ID: {crawl_result['jobId']}")
                    return True

            return False
        except Exception as e:
            print(f"Error adding web content from {url}: {str(e)}")
            return False

    def add_search_results(self, query: str, max_results: int = 3) -> bool:
        """
        Search the web and add relevant content to knowledge base

        Args:
            query (str): Search query
            max_results (int): Maximum search results to process

        Returns:
            bool: Success status
        """
        firecrawl = self.get_firecrawl_service()
        if not firecrawl:
            return False

        try:
            search_results = firecrawl.search_web(query, max_results=max_results)
            if search_results and 'data' in search_results:
                for result in search_results['data'][:max_results]:
                    if 'url' in result:
                        # Scrape each search result URL
                        scraped = firecrawl.scrape_url(result['url'])
                        if scraped and 'markdown' in scraped:
                            self._add_scraped_content(scraped, result['url'], search_query=query)
                return True
            return False
        except Exception as e:
            print(f"Error adding search results for query '{query}': {str(e)}")
            return False

    def _add_scraped_content(self, scraped_data: Dict, url: str, search_query: Optional[str] = None):
        """Add scraped content to the vector database"""
        if 'markdown' not in scraped_data:
            return

        content = scraped_data['markdown']
        title = scraped_data.get('metadata', {}).get('title', 'Unknown')

        # Clean and chunk the content
        cleaned_content = self._clean_markdown(content)
        chunks = self._split_into_chunks(cleaned_content)

        # Add chunks to database
        for i, chunk in enumerate(chunks):
            chunk_id = f"web_{hash(url)}_{i}"
            metadata = {
                "source": url,
                "type": "web_scrape",
                "title": title,
                "chunk_index": i
            }
            if search_query:
                metadata["search_query"] = search_query

            try:
                # Check if chunk already exists
                existing = self.collection.get(ids=[chunk_id])
                if not existing['documents']:
                    self.collection.add(
                        documents=[chunk],
                        ids=[chunk_id],
                        metadatas=[metadata]
                    )
            except:
                self.collection.add(
                    documents=[chunk],
                    ids=[chunk_id],
                    metadatas=[metadata]
                )

    def _clean_markdown(self, markdown_content: str) -> str:
        """Clean markdown content for better processing"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        # Remove markdown links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # Remove image references
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        return content.strip()

    def _split_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks by paragraphs/sections"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def search(self, query: str, n_results: int = 3, source_filter: Optional[str] = None) -> List[str]:
        """
        Search for relevant information with optional source filtering

        Args:
            query (str): Search query
            n_results (int): Number of results to return
            source_filter (str): Filter by source type ('web_scrape', 'local_file', or None for all)

        Returns:
            List[str]: Relevant documents
        """
        where_clause = None
        if source_filter:
            where_clause = {"type": source_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        return results['documents'][0] if results['documents'] else []

    def get_sources(self, query: str, n_results: int = 3) -> List[Dict]:
        """Get search results with source metadata"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas']
        )

        sources = []
        if results['documents'] and results['metadatas']:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                sources.append({
                    'content': doc,
                    'source': metadata.get('source', 'Unknown'),
                    'type': metadata.get('type', 'Unknown'),
                    'title': metadata.get('title', 'Unknown')
                })

        return sources

    def reload_data(self):
        """Reload data from file (keeps web scraped content)"""
        # Only reload file-based content, keep web content
        try:
            # Get all existing file chunks
            file_chunks = self.collection.get(where={"type": "file"})
            if file_chunks['ids']:
                self.collection.delete(ids=file_chunks['ids'])

            # Reload file content
            self.load_data()
        except Exception as e:
            print(f"Error reloading data: {str(e)}")

    def refetch_and_reload_data(self, url: str = "https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom") -> bool:
        """
        Refetch data from URL using Firecrawl, save to local file, and reload into ChromaDB

        Args:
            url (str): URL to fetch data from

        Returns:
            bool: Success status
        """
        firecrawl = self.get_firecrawl_service()
        if not firecrawl:
            print("Firecrawl service not available")
            return False

        try:
            # Scrape the URL
            print(f"Fetching data from {url}...")
            result = firecrawl.scrape_url(url)

            if not result or 'markdown' not in result:
                print("Failed to fetch data from URL")
                return False

            # Extract content
            content = result['markdown']
            title = result.get('metadata', {}).get('title', 'Unknown')

            # Clean the content
            cleaned_content = self._clean_markdown(content)

            # Save to local file
            print(f"Saving data to {self.data_file}...")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(cleaned_content)

            # Delete old file-based chunks from ChromaDB
            file_chunks = self.collection.get(where={"type": "file"})
            if file_chunks['ids']:
                self.collection.delete(ids=file_chunks['ids'])
                print(f"Deleted {len(file_chunks['ids'])} old file chunks")

            # Reload the new data into ChromaDB
            self.load_data()
            print("Data successfully reloaded into ChromaDB")

            return True

        except Exception as e:
            print(f"Error refetching and reloading data: {str(e)}")
            return False

    def clear_web_content(self):
        """Clear all web-scraped content"""
        try:
            web_chunks = self.collection.get(where={"type": "web_scrape"})
            if web_chunks['ids']:
                self.collection.delete(ids=web_chunks['ids'])
                print(f"Cleared {len(web_chunks['ids'])} web content chunks")
        except Exception as e:
            print(f"Error clearing web content: {str(e)}")

    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        try:
            all_items = self.collection.get(include=['metadatas'])
            file_count = sum(1 for meta in all_items['metadatas'] if meta.get('type') == 'file')
            web_count = sum(1 for meta in all_items['metadatas'] if meta.get('type') == 'web_scrape')

            return {
                'total_chunks': len(all_items['metadatas']),
                'file_chunks': file_count,
                'web_chunks': web_count
            }
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {'total_chunks': 0, 'file_chunks': 0, 'web_chunks': 0}
