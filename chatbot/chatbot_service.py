import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class ChatbotService:
    def __init__(self, rag_service):
        self.rag_service = rag_service
        self.client = None

        # Try to initialize Anthropic client if API key is available
        # api_key = os.getenv('ANTHROPIC_API_KEY')
        api_key = "your-anthropic-api-key-here"
        if api_key and api_key != 'your-anthropic-api-key-here':
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                print("✅ Anthropic Claude API initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize Anthropic client: {e}")
                self.client = None
        else:
            print("ℹ️ No Anthropic API key found. Chatbot will use simple retrieval responses.")

    def get_response(self, user_query):
        """Get chatbot response using RAG"""
        # Retrieve relevant context
        relevant_docs = self.rag_service.search(user_query, n_results=10)

        if not relevant_docs:
            return "I don't have information about that topic in my knowledge base. You can add web content using the 'Add Web Content' or 'Add Search Results' buttons above to expand my knowledge!"

        if self.client:
            # Use Claude AI for sophisticated responses
            context = "\n\n".join(relevant_docs)

            prompt = f"""You are a helpful assistant for UK universities information. 
                        Use the following context to answer the user's question. If the answer is not in the context, say so politely.
                        
                        Context:
                        {context}
                        
                        User Question: {user_query}
                        
                        Answer:"""

            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
            except Exception as e:
                print(f"Error calling Claude API: {e}")
                # Fall back to simple retrieval
                return self._simple_response(user_query, relevant_docs)
        else:
            # Use simple retrieval-based response
            return self._simple_response(user_query, relevant_docs)

    def _simple_response(self, user_query, relevant_docs):
        """Generate a simple response without AI when Claude is not available"""
        if len(relevant_docs) == 0:
            return "I don't have information about that topic in my knowledge base."

        # Create a simple response by combining the most relevant information
        response = f"Based on the information in my knowledge base about **'{user_query}'**:\n\n"
        response += "---\n\n"

        # Show top 3-5 most relevant sources
        num_sources = 10

        for i, doc in enumerate(relevant_docs[:num_sources]):
            # Clean up the document text
            doc_clean = doc.strip()

            # Truncate very long documents but keep enough context
            if len(doc_clean) > 400:
                # Try to cut at a sentence boundary
                truncate_at = doc_clean.rfind('.', 0, 400)
                if truncate_at > 200:
                    doc_preview = doc_clean[:truncate_at + 1] + "..."
                else:
                    doc_preview = doc_clean[:400] + "..."
            else:
                doc_preview = doc_clean

            response += f"**Source {i + 1}:**\n{doc_preview}\n\n"

        if len(relevant_docs) > num_sources:
            response += f"*({len(relevant_docs) - num_sources} more sources available)*\n\n"

        response += "---\n\n"
        return response
