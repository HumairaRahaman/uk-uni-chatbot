# import anthropic
# import os
# from dotenv import load_dotenv
# from typing import List, Dict
#
# load_dotenv()
#
#
# class ChatbotService:
#     def __init__(self, rag_service):
#         self.rag_service = rag_service
#         self.client = None
#         self.conversation_history = []  # Store conversation history for context
#
#         # Get API key from environment
#         api_key = os.getenv('ANTHROPIC_API_KEY')
#         if api_key and api_key != 'your-anthropic-api-key-here':
#             try:
#                 self.client = anthropic.Anthropic(api_key=api_key)
#                 print("✅ Anthropic Claude API initialized with conversation support")
#             except Exception as e:
#                 print(f"⚠️ Could not initialize Anthropic client: {e}")
#                 self.client = None
#         else:
#             print("ℹ️ No Anthropic API key found. Using enhanced retrieval responses.")
#
#     def get_response(self, user_query, include_history=True):
#         """
#         Get chatbot response using enhanced RAG with ChatGPT/Gemini-style responses
#
#         Args:
#             user_query: The user's question
#             include_history: Whether to include conversation history for context
#         """
#         # Retrieve relevant context with more results for comprehensive answers
#         relevant_docs = self.rag_service.search(user_query, n_results=10)
#
#         if not relevant_docs:
#             response = "I don't have specific information about that in my knowledge base. However, I'd be happy to help with questions about:\n\n" \
#                        "• UK universities and their history\n" \
#                        "• Admission processes and requirements\n" \
#                        "• Student life and accommodation\n" \
#                        "• University rankings and reputation\n" \
#                        "• Funding, tuition fees, and financial support\n" \
#                        "• Different types of universities (ancient, redbrick, plate glass, etc.)\n\n" \
#                        "What would you like to know?"
#             return response
#
#         if self.client:
#             # Use Claude AI with enhanced prompting for natural, specific, conversational responses
#             return self._get_ai_response(user_query, relevant_docs, include_history)
#         else:
#             return self._get_enhanced_simple_response(user_query, relevant_docs)
#
#     def _get_ai_response(self, user_query, relevant_docs, include_history):
#         """Generate AI-powered response with conversation context"""
#         context = "\n\n---\n\n".join(relevant_docs)
#
#         # Build system prompt
#         system_prompt = """You are an expert UK universities advisor assistant with deep knowledge of higher education in the United Kingdom. You communicate in a warm, friendly, and conversational style similar to ChatGPT and Gemini.
#
# YOUR PERSONALITY:
# - Enthusiastic and passionate about education
# - Patient and thorough in explanations
# - Use natural, flowing language
# - Break down complex topics into digestible parts
# - Provide specific examples and concrete details
#
# YOUR RESPONSE STYLE:
# 1. Start with a direct answer to the question
# 2. Expand with relevant details, facts, and context
# 3. Use natural paragraph breaks (not bullet points unless asked)
# 4. Include specific numbers, dates, names when available
# 5. Make connections between different pieces of information
# 6. End with something helpful (related info, next steps, or invitation for follow-up questions)
#
# IMPORTANT RULES:
# - ONLY use information from the provided context
# - If information is not in the context, say so clearly
# - Be conversational but accurate
# - Aim for 3-6 paragraphs for most questions
# - For simple questions, give concise but complete answers
# - For complex questions, provide comprehensive, detailed responses
# - Never make up information or statistics"""
#
#         # Build the conversation messages
#         messages = []
#
#         # Add conversation history if enabled and available
#         if include_history and self.conversation_history:
#             # Include last 3 exchanges for context (to stay within token limits)
#             recent_history = self.conversation_history[-6:]  # Last 3 Q&A pairs
#             for msg in recent_history:
#                 messages.append(msg)
#
#         # Add current query with context
#         current_message = f"""Context Information (from knowledge base):
# {context}
#
# ---
#
# User Question: {user_query}
#
# Please provide a detailed, conversational answer based on the context above:"""
#
#         messages.append({"role": "user", "content": current_message})
#
#         try:
#             response = self.client.messages.create(
#                 model="claude-sonnet-4-20250514",
#                 max_tokens=2000,  # Generous limit for detailed responses
#                 temperature=0.8,  # High temperature for natural, varied responses
#                 system=system_prompt,
#                 messages=messages
#             )
#
#             assistant_response = response.content[0].text.strip()
#
#             # Store in conversation history
#             self.conversation_history.append({"role": "user", "content": user_query})
#             self.conversation_history.append({"role": "assistant", "content": assistant_response})
#
#             # Keep history manageable (last 10 exchanges = 20 messages)
#             if len(self.conversation_history) > 20:
#                 self.conversation_history = self.conversation_history[-20:]
#
#             return assistant_response
#
#         except Exception as e:
#             print(f"Error calling Claude API: {e}")
#             return self._get_enhanced_simple_response(user_query, relevant_docs)
#
#     def _get_enhanced_simple_response(self, user_query, relevant_docs):
#         """Generate an enhanced response without AI - much more detailed and organized"""
#         if len(relevant_docs) == 0:
#             return "I don't have information about that topic in my knowledge base."
#
#         # Create a comprehensive, well-structured response
#         response = f"# About: {user_query}\n\n"
#
#         # Analyze and group the information
#         combined_info = []
#         for doc in relevant_docs[:6]:
#             doc_clean = doc.strip()
#             # Extract substantive sentences
#             sentences = [s.strip() for s in doc_clean.split('.') if len(s.strip()) > 30]
#             combined_info.extend(sentences[:4])  # Take up to 4 sentences per doc
#
#         # Remove duplicates while preserving order
#         seen = set()
#         unique_info = []
#         for sent in combined_info:
#             sent_lower = sent.lower()
#             if sent_lower not in seen:
#                 seen.add(sent_lower)
#                 unique_info.append(sent)
#
#         # Create a flowing narrative response
#         if len(unique_info) > 0:
#             # First paragraph
#             response += unique_info[0] + ". "
#             if len(unique_info) > 1:
#                 response += unique_info[1] + ".\n\n"
#
#             # Second paragraph
#             if len(unique_info) > 2:
#                 response += unique_info[2] + ". "
#                 if len(unique_info) > 3:
#                     response += unique_info[3] + ".\n\n"
#
#             # Third paragraph
#             if len(unique_info) > 4:
#                 remaining = ". ".join(unique_info[4:8])
#                 response += remaining + ".\n\n"
#
#         # Add information about sources
#         response += f"*This information is based on {len(relevant_docs)} relevant sources from the knowledge base.*\n\n"
#
#         # Add helpful tip about getting better responses
#         response += "---\n\n"
#         response += "💡 **Want even better answers?**\n\n"
#         response += "Add your Anthropic API key to enable ChatGPT-style conversational responses with:\n"
#         response += "• More natural and flowing explanations\n"
#         response += "• Better context understanding\n"
#         response += "• Conversation memory across questions\n"
#         response += "• More detailed and specific answers\n\n"
#         response += "Get your API key at: https://console.anthropic.com/"
#
#         return response
#
#     def clear_history(self):
#         """Clear conversation history"""
#         self.conversation_history = []
#         return "Conversation history cleared. Starting fresh!"
#
#     def get_history_summary(self):
#         """Get a summary of conversation history"""
#         num_exchanges = len(self.conversation_history) // 2
#         return f"Current conversation has {num_exchanges} exchanges (last {min(num_exchanges, 3)} are used for context)."