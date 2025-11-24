import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


class ChatbotService:
    def __init__(self, rag_service):
        self.rag_service = rag_service
        self.client = None

        # Get API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key and api_key != 'your-anthropic-api-key-here':
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                print("✅ Anthropic Claude API initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize Anthropic client: {e}")
                self.client = None
        else:
            print("ℹ️ No Anthropic API key found. Using simple retrieval responses.")

    def get_response(self, user_query):
        """Get chatbot response using optimized RAG"""
        # Retrieve relevant context with optimized settings
        relevant_docs = self.rag_service.search(user_query, n_results=5)

        if not relevant_docs:
            return "I don't have information about that topic in my knowledge base. Try asking about UK universities, admissions, or student life."

        if self.client:
            # Use Claude AI with optimized prompting
            context = "\n\n".join(relevant_docs)

            prompt = f"""You are a knowledgeable UK universities advisor. Answer the user's question clearly and concisely using ONLY the information provided in the context below.

Rules:
- Give direct, focused answers in 2-4 sentences maximum
- If the context doesn't contain the answer, say "I don't have that specific information"
- Don't add information not in the context
- Be conversational but precise

Context:
{context}

User Question: {user_query}

Answer (be brief and direct):"""

            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,  # Reduced for faster, more concise responses
                    temperature=0.3,  # Lower temperature for more focused responses
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text.strip()
            except Exception as e:
                print(f"Error calling Claude API: {e}")
                return self._simple_response(user_query, relevant_docs)
        else:
            return self._simple_response(user_query, relevant_docs)

    def _simple_response(self, user_query, relevant_docs):
        """Generate a concise response without AI"""
        if len(relevant_docs) == 0:
            return "I don't have information about that topic."

        # Create a concise response with top 2 sources
        response = f"**About '{user_query}':**\n\n"

        for i, doc in enumerate(relevant_docs[:2]):
            doc_clean = doc.strip()

            # Extract the most relevant sentence
            sentences = doc_clean.split('.')
            relevant_sentence = sentences[0] if sentences else doc_clean

            if len(relevant_sentence) > 200:
                relevant_sentence = relevant_sentence[:200] + "..."

            response += f"• {relevant_sentence}.\n\n"

        response += f"\n_Found {len(relevant_docs)} related sources._"

        return response