import os
import re
from dotenv import load_dotenv

load_dotenv()


class ChatbotService:
    def __init__(self, rag_service):
        self.rag_service = rag_service
        print("✅ Chatbot initialized in FREE mode (no API required)")
        print("💡 Responses will be structured and informative")

    def _clean_text(self, text: str) -> str:
        """Remove citation links and clean text"""
        try:
            text = re.sub(r'\[\d+\]', '', text)
            text = re.sub(r'https?://[^\s]+', '', text)
            text = re.sub(r'www\.[^\s]+', '', text)
            text = re.sub(r'org/wiki/[^\s\)]+', '', text)
            text = re.sub(r'#cite[^\s\)]+', '', text)
            text = re.sub(r'\(\s*\)', '', text)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\s+([.,;:!?])', r'\1', text)
            return text.strip()
        except Exception as e:
            print(f"Error cleaning text: {e}")
            return text

    def _is_education_related(self, query: str) -> bool:
        """Check if query is about UK universities/education"""
        try:
            education_keywords = [
                'university', 'universities', 'college', 'oxford', 'cambridge',
                'student', 'admission', 'ucas', 'degree', 'tuition', 'fee',
                'russell group', 'redbrick', 'accommodation', 'campus',
                'undergraduate', 'postgraduate', 'phd', 'master', 'bachelor',
                'lecture', 'semester', 'academic', 'education', 'study',
                'scholarship', 'student loan', 'uk education', 'british university',
                'imperial', 'lse', 'ucl', 'edinburgh', 'manchester', 'warwick',
                'course', 'program', 'faculty', 'department', 'school',
                'a-level', 'gcse', 'btec', 'foundation', 'clearing',
                'student visa', 'international student', 'home student',
                'halls', 'library', 'dissertation', 'thesis',
                'exam', 'assessment', 'grade', 'gpa', 'transcript'
            ]
            query_lower = query.lower()
            return any(keyword in query_lower for keyword in education_keywords)
        except Exception as e:
            print(f"Error checking if education related: {e}")
            return False

    def get_response(self, user_query):
        """Get response - 100% FREE, no API needed"""

        try:
            print(f"📝 Processing query: {user_query[:50]}...")

            # Check if question is education-related
            is_education = self._is_education_related(user_query)
            print(f"🎓 Is education-related: {is_education}")

            if not is_education:
                # NOT education-related - decline politely
                print("❌ Non-education question - returning decline message")
                return """🎓 **UK Universities Information Bot**

I specialize in providing information about UK universities and higher education.

**I can help you with:**
• 🏛️ University information (Oxford, Cambridge, Russell Group, etc.)
• 📝 Admissions and UCAS applications
• 💰 Tuition fees and scholarships
• 🏠 Student accommodation and campus life
• 📚 Courses and degree programs
• 🎯 University rankings and comparisons
• 📊 Entry requirements and A-levels
• 🌍 International student information

**Please ask me about UK universities and education!**

**Example questions:**
• "Tell me about Oxford University"
• "What is the Russell Group?"
• "How do I apply through UCAS?"
• "Compare Oxford and Cambridge"
• "What are redbrick universities?"
• "Student accommodation in UK universities"
"""

            # Education question - search knowledge base
            print("🔍 Searching knowledge base...")
            relevant_docs = self.rag_service.search(user_query, n_results=8)
            print(f"📚 Found {len(relevant_docs)} relevant documents")

            if not relevant_docs or len(relevant_docs) == 0:
                print("⚠️ No relevant documents found")
                return """I don't have specific information about that topic in my knowledge base.

**I can help with:**
• UK university information
• Admissions processes  
• Student life and accommodation
• University rankings and comparisons
• Entry requirements

**Try asking:**
• About specific universities (Oxford, Cambridge, etc.)
• About the Russell Group
• About UCAS applications
• About student life in UK universities

Please try rephrasing your question or ask about a specific UK university!"""

            # Clean documents
            print("🧹 Cleaning documents...")
            cleaned_docs = [self._clean_text(doc) for doc in relevant_docs]

            # Generate FREE mode response
            print("✅ Generating response...")
            return self._generate_response(user_query, cleaned_docs)

        except Exception as e:
            # Log the full error
            import traceback
            print(f"❌ ERROR in get_response: {str(e)}")
            print(traceback.format_exc())

            return """Sorry, I encountered an error processing your question.

**Please try:**
• Rephrasing your question
• Asking about a specific UK university
• Making sure your question is about UK education

**Example questions that work:**
• "Tell me about Oxford University"
• "What is the Russell Group?"
• "How do I apply to UK universities?"

If the problem persists, please contact support."""

    def _generate_response(self, user_query, cleaned_docs):
        """Generate structured response from knowledge base"""

        try:
            print("📝 Building structured response...")

            # Start with title
            response = f"## 🎓 {user_query.title()}\n\n"

            # Extract sentences from documents
            all_sentences = []
            for doc in cleaned_docs[:6]:  # Use top 6 documents
                # Split by period
                sentences = doc.split('.')
                for sent in sentences:
                    sent = sent.strip()
                    # Only keep substantial sentences
                    if len(sent) > 50:
                        all_sentences.append(sent)

            print(f"📄 Extracted {len(all_sentences)} sentences")

            # Remove duplicates while preserving order
            seen = set()
            unique_sentences = []
            for sent in all_sentences:
                sent_lower = sent.lower()
                # Check if we've seen similar content
                if sent_lower not in seen and len(sent) > 50:
                    seen.add(sent_lower)
                    unique_sentences.append(sent)
                    # Limit to 10 unique sentences max
                    if len(unique_sentences) >= 10:
                        break

            print(f"✅ {len(unique_sentences)} unique sentences")

            if len(unique_sentences) == 0:
                print("⚠️ No valid sentences extracted")
                return f"I found information about {user_query}, but couldn't extract clear details. Please try rephrasing your question."

            # Build structured response
            if len(unique_sentences) >= 1:
                response += "**Overview:**\n"
                response += f"{unique_sentences[0]}.\n\n"

            if len(unique_sentences) >= 4:
                response += "**Key Information:**\n"
                for i in range(1, min(4, len(unique_sentences))):
                    response += f"• {unique_sentences[i]}.\n"
                response += "\n"

            if len(unique_sentences) >= 7:
                response += "**Additional Details:**\n"
                for i in range(4, min(7, len(unique_sentences))):
                    response += f"• {unique_sentences[i]}.\n"
                response += "\n"

            # Add helpful closing
            response += "\n💡 **Need more information?** Feel free to ask about specific aspects!"

            print("✅ Response generated successfully")
            return response

        except Exception as e:
            import traceback
            print(f"❌ ERROR in _generate_response: {str(e)}")
            print(traceback.format_exc())

            # Fallback to very simple response
            if cleaned_docs and len(cleaned_docs) > 0:
                first_doc = cleaned_docs[0]
                # Get first 400 characters
                simple_text = first_doc[:400]
                return f"""**About: {user_query}**

{simple_text}...

*This is a simplified response. Try rephrasing your question for better results.*"""
            else:
                return "I couldn't generate a proper response. Please try asking your question differently."