import chromadb
from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self, data_file_path):
        self.data_file = data_file_path
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="uk_universities")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.load_data()
    
    def load_data(self):

        with open(self.data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks
        chunks = self._split_into_chunks(content)
        
        # Add to vector database
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                ids=[f"chunk_{i}"]
            )
    
    def _split_into_chunks(self, text, chunk_size=500):

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
    
    def search(self, query, n_results=3):

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    
    def reload_data(self):

        self.client.delete_collection(name="uk_universities")
        self.collection = self.client.create_collection(name="uk_universities")
        self.load_data()
