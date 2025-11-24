import chromadb
from sentence_transformers import SentenceTransformer
from chatbot.firecrawl_service import FirecrawlService
import re
from typing import List, Dict, Optional


class EnhancedRAGService:
    def __init__(self, data_file_path, collection_name="enhanced_knowledge_base"):
        self.data_file = data_file_path
        self.collection_name = collection_name

        # Use persistent client for better performance
        self.client = chromadb.Client()

        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Optimized for cosine similarity
            )
            print(f"✅ Created new collection: {collection_name}")

        # Use faster embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")

        self.firecrawl = None

        # Initialize with existing data if collection is empty
        try:
            count = self.collection.count()
            if count == 0:
                print("Collection is empty, loading data...")
                self.load_data()
            else:
                print(f"✅ Collection has {count} documents")
        except:
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
        """Load and chunk data with optimized chunking strategy"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Improved chunking: smaller, more focused chunks
            chunks = self._split_into_chunks(content, chunk_size=300)

            print(f"Processing {len(chunks)} chunks...")

            # Batch add for better performance
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                ids = [f"file_chunk_{j}" for j in range(i, i + len(batch))]
                metadatas = [{"source": "local_file", "type": "file"} for _ in batch]

                try:
                    # Check if any IDs already exist
                    existing = self.collection.get(ids=ids)
                    existing_ids = set(existing['ids']) if existing['ids'] else set()

                    # Only add new chunks
                    new_chunks = []
                    new_ids = []
                    new_metadatas = []

                    for chunk, chunk_id, metadata in zip(batch, ids, metadatas):
                        if chunk_id not in existing_ids:
                            new_chunks.append(chunk)
                            new_ids.append(chunk_id)
                            new_metadatas.append(metadata)

                    if new_chunks:
                        self.collection.add(
                            documents=new_chunks,
                            ids=new_ids,
                            metadatas=new_metadatas
                        )
                except Exception as e:
                    print(f"Error adding batch {i}: {e}")
                    continue

            print(f"✅ Loaded {len(chunks)} chunks into knowledge base")

        except FileNotFoundError:
            print(f"⚠️ Data file {self.data_file} not found. Starting with empty knowledge base.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def _split_into_chunks(self, text: str, chunk_size: int = 300) -> List[str]:
        """
        Split text into optimized chunks
        Smaller chunks = more precise retrieval = faster responses
        """
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = self._clean_text(para)

            # Skip very short paragraphs (likely headers or noise)
            if len(para) < 30:
                continue

            # If paragraph is small enough, add to current chunk
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + " "
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Start new chunk with current paragraph
                if len(para) > chunk_size:
                    # Split long paragraphs into sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    temp_chunk = ""
                    for sent in sentences:
                        if len(temp_chunk) + len(sent) < chunk_size:
                            temp_chunk += sent + " "
                        else:
                            if temp_chunk.strip():
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sent + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = para + " "

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def search(self, query: str, n_results: int = 5, source_filter: Optional[str] = None) -> List[str]:
        """
        Optimized search with better relevance filtering
        """
        try:
            where_clause = None
            if source_filter:
                where_clause = {"type": source_filter}

            # Increased n_results to get more candidates, then filter
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results * 2, 10),  # Get more candidates
                where=where_clause
            )

            if not results['documents'] or not results['documents'][0]:
                return []

            # Return top n_results
            documents = results['documents'][0][:n_results]

            # Filter out very short or irrelevant chunks
            filtered_docs = [
                doc for doc in documents
                if len(doc.strip()) > 50  # Minimum length
            ]

            return filtered_docs if filtered_docs else documents

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_sources(self, query: str, n_results: int = 3) -> List[Dict]:
        """Get search results with source metadata"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            sources = []
            if results['documents'] and results['metadatas']:
                for doc, metadata, distance in zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0] if results.get('distances') else [0] * len(results['documents'][0])
                ):
                    sources.append({
                        'content': doc,
                        'source': metadata.get('source', 'Unknown'),
                        'type': metadata.get('type', 'Unknown'),
                        'title': metadata.get('title', 'Unknown'),
                        'relevance': 1 - distance  # Convert distance to relevance score
                    })

            return sources
        except Exception as e:
            print(f"Error getting sources: {e}")
            return []

    def reload_data(self):
        """Reload data from file"""
        try:
            # Delete only file-based chunks
            file_chunks = self.collection.get(where={"type": "file"})
            if file_chunks['ids']:
                self.collection.delete(ids=file_chunks['ids'])
                print(f"Deleted {len(file_chunks['ids'])} old file chunks")

            # Reload file content
            self.load_data()
        except Exception as e:
            print(f"Error reloading data: {e}")

    def refetch_and_reload_data(self,
                                url: str = "https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom") -> bool:
        """Refetch data from URL using Firecrawl"""
        firecrawl = self.get_firecrawl_service()
        if not firecrawl:
            print("Firecrawl service not available")
            return False

        try:
            print(f"Fetching data from {url}...")
            result = firecrawl.scrape_url(url)

            if not result or 'markdown' not in result:
                print("Failed to fetch data from URL")
                return False

            content = result['markdown']
            title = result.get('metadata', {}).get('title', 'Unknown')

            # Clean the content
            cleaned_content = self._clean_text(content)

            # Save to local file
            print(f"Saving data to {self.data_file}...")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(cleaned_content)

            # Reload into ChromaDB
            self.reload_data()
            print("✅ Data successfully refetched and reloaded")

            return True

        except Exception as e:
            print(f"Error refetching data: {e}")
            return False

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
            print(f"Error getting stats: {e}")
            return {'total_chunks': 0, 'file_chunks': 0, 'web_chunks': 0}

    def clear_web_content(self):
        """Clear all web-scraped content"""
        try:
            web_chunks = self.collection.get(where={"type": "web_scrape"})
            if web_chunks['ids']:
                self.collection.delete(ids=web_chunks['ids'])
                print(f"Cleared {len(web_chunks['ids'])} web content chunks")
        except Exception as e:
            print(f"Error clearing web content: {e}")

    # Keep other methods from original file for web scraping functionality
    def add_web_content(self, url: str, max_pages: int = 1) -> bool:
        """Add web content to the knowledge base"""
        firecrawl = self.get_firecrawl_service()
        if not firecrawl:
            return False

        try:
            result = firecrawl.scrape_url(url)
            if result and 'markdown' in result:
                self._add_scraped_content(result, url)
                return True
            return False
        except Exception as e:
            print(f"Error adding web content: {e}")
            return False

    def _add_scraped_content(self, scraped_data: Dict, url: str, search_query: Optional[str] = None):
        """Add scraped content to vector database"""
        if 'markdown' not in scraped_data:
            return

        content = scraped_data['markdown']
        title = scraped_data.get('metadata', {}).get('title', 'Unknown')

        cleaned_content = self._clean_text(content)
        chunks = self._split_into_chunks(cleaned_content)

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