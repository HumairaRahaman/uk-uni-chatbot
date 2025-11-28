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
            # Remove citation numbers like [1], [2], [183]
            text = re.sub(r'\[\d+\]', '', text)

            # Remove escaped citation brackets like [\[183\]]
            text = re.sub(r'\[\\?\[\\?\d+\\?\]\\?\]', '', text)

            # Remove Wikipedia editorial markers like [citation needed], [self-published source], etc.
            text = re.sub(r'\[\\?_\[?[^\]]+_?\\?\]\\?\]', '', text)
            text = re.sub(r'\(_\[[^\]]+\]_?\)', '', text)
            text = re.sub(r'\[_[^\]]+_\]', '', text)

            # Remove Wikipedia tags like [update], [clarification needed], etc.
            text = re.sub(r'\[\\?update\\?\]', '', text)
            text = re.sub(r'\[\\?needs update\\?\]', '', text)
            text = re.sub(r'\[\\?clarification needed\\?\]', '', text)
            text = re.sub(r'\[\\?citation needed\\?\]', '', text)
            text = re.sub(r'\[\\?failed verification\\?\]', '', text)
            text = re.sub(r'\[\\?when\?\\?\]', '', text)
            text = re.sub(r'\[\\?who\?\\?\]', '', text)
            text = re.sub(r'\[\\?which\?\\?\]', '', text)

            # Remove any remaining [word] patterns (Wikipedia tags)
            text = re.sub(r'\[\\?[a-zA-Z\s]+\\?\]', '', text)

            # Remove standalone _] or _[
            text = re.sub(r'_\\?\]', '', text)
            text = re.sub(r'\\?\[_', '', text)

            # Remove backslashes and underscores (but keep normal brackets and parentheses)
            text = re.sub(r'\\', '', text)  # Remove all backslashes
            text = re.sub(r'_', '', text)  # Remove all underscores

            # Remove any remaining escaped brackets
            text = re.sub(r'\[\\?\]', '', text)

            # Remove URLs
            text = re.sub(r'https?://[^\s]+', '', text)
            text = re.sub(r'www\.[^\s]+', '', text)
            text = re.sub(r'org/wiki/[^\s\)]+', '', text)

            # Remove citation markers like #cite_note-211
            text = re.sub(r'#cite[^\s\)]+', '', text)

            # Remove empty parentheses and brackets left after removing citations
            text = re.sub(r'\(\s*\)', '', text)
            text = re.sub(r'\[\s*\]', '', text)

            # Remove multiple spaces
            text = re.sub(r'\s+', ' ', text)

            # Remove spaces before punctuation
            text = re.sub(r'\s+([.,;:!?])', r'\1', text)

            return text.strip()
        except Exception as e:
            print(f"Error cleaning text: {e}")
            return text

    def _is_education_related(self, query: str) -> bool:
        """Check if query is about UK universities/education - with fuzzy matching for spelling mistakes"""
        try:
            education_keywords = [
                'university', 'universities', 'college', 'oxford', 'cambridge',
                'student', 'admission', 'ucas', 'degree', 'tuition', 'fee',
                'russell group', 'redbrick', 'accommodation', 'campus',
                'undergraduate', 'postgraduate', 'phd', 'master', 'bachelor',
                'lecture', 'semester', 'academic', 'education', 'study',
                'scholarship', 'student loan', 'uk education', 'british university',
                'imperial', 'lse', 'ucl', 'edinburgh', 'manchester', 'warwick',
                'course', 'program', 'programme', 'faculty', 'department', 'school',
                'a-level', 'gcse', 'btec', 'foundation', 'clearing',
                'student visa', 'international student', 'home student',
                'halls', 'library', 'dissertation', 'thesis',
                'exam', 'assessment', 'grade', 'gpa', 'transcript',
                # More UK universities
                'durham', 'bristol', 'nottingham', 'leeds', 'liverpool',
                'birmingham', 'glasgow', 'exeter', 'york', 'bath',
                'st andrews', 'kings college', 'queen mary', 'southampton',
                'newcastle', 'cardiff', 'sheffield', 'leicester',
                # University types
                'ancient', 'plate glass', 'civic', 'new university',
                'russell', 'group of universities'
            ]

            query_lower = query.lower()

            # First check exact matches
            if any(keyword in query_lower for keyword in education_keywords):
                return True

            # If no exact match, try fuzzy matching for spelling mistakes
            query_words = query_lower.split()
            for word in query_words:
                # Only check words longer than 3 characters
                if len(word) <= 3:
                    continue

                for keyword in education_keywords:
                    # Only fuzzy match single-word keywords
                    if ' ' in keyword:
                        continue

                    # Calculate similarity
                    if self._is_similar(word, keyword):
                        print(f"🔍 Fuzzy match: '{word}' matched with '{keyword}'")
                        return True

            return False

        except Exception as e:
            print(f"Error checking if education related: {e}")
            return False

    def _is_similar(self, word1: str, word2: str, threshold: int = 2) -> bool:
        """Check if two words are similar using Levenshtein distance (allows typos)"""
        # If lengths differ by more than threshold, not similar
        if abs(len(word1) - len(word2)) > threshold:
            return False

        # Calculate Levenshtein distance (edit distance)
        distance = self._levenshtein_distance(word1, word2)

        # Allow up to 2 character differences for words 5+ chars
        # Allow 1 character difference for words 4 chars
        max_distance = 2 if len(word2) >= 5 else 1

        return distance <= max_distance

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

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
        """Generate conversational, ChatGPT-style response from knowledge base"""

        try:
            print("📝 Building conversational response...")

            # Extract sentences from documents
            all_sentences = []
            for doc in cleaned_docs[:8]:  # Use top 8 documents for more content
                sentences = doc.split('.')
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 50:
                        all_sentences.append(sent)

            print(f"📄 Extracted {len(all_sentences)} sentences")

            # Remove duplicates while preserving order
            seen = set()
            unique_sentences = []
            for sent in all_sentences:
                sent_lower = sent.lower()
                if sent_lower not in seen and len(sent) > 50:
                    seen.add(sent_lower)
                    unique_sentences.append(sent)
                    if len(unique_sentences) >= 12:  # Get more sentences for better answers
                        break

            print(f"✅ {len(unique_sentences)} unique sentences")

            if len(unique_sentences) == 0:
                return "I don't have specific information about that in my knowledge base. Could you try rephrasing your question or ask about a specific UK university?"

            # Build natural, conversational response like ChatGPT/Gemini
            response = self._create_conversational_response(user_query, unique_sentences)

            print("✅ Conversational response generated")
            return response

        except Exception as e:
            import traceback
            print(f"❌ ERROR in _generate_response: {str(e)}")
            print(traceback.format_exc())

            # Fallback
            if cleaned_docs and len(cleaned_docs) > 0:
                return cleaned_docs[0][:500] + "..."
            else:
                return "I couldn't generate a proper response. Please try asking your question differently."

    def _create_conversational_response(self, query, sentences):
        """Create a natural, flowing response like ChatGPT/Gemini"""

        # Determine query type and create appropriate intro
        query_lower = query.lower()

        # Opening based on question type
        if any(word in query_lower for word in ['what is', 'what are', 'what\'s']):
            # Definitional question
            intro = sentences[0] if len(sentences) > 0 else ""
            response = f"{intro}."
        elif any(word in query_lower for word in ['tell me about', 'tell about', 'info about', 'information about']):
            # General information request
            response = f"{sentences[0]}." if len(sentences) > 0 else ""
        elif any(word in query_lower for word in ['how', 'why', 'when', 'where', 'who']):
            # Specific question
            response = f"{sentences[0]}." if len(sentences) > 0 else ""
        else:
            # General query
            response = f"{sentences[0]}." if len(sentences) > 0 else ""

        # Add supporting details in natural paragraphs
        if len(sentences) >= 4:
            # Second paragraph - add 2-3 supporting sentences
            response += f"\n\n{sentences[1]}. {sentences[2]}."
            if len(sentences) > 3:
                response += f" {sentences[3]}."

        if len(sentences) >= 7:
            # Third paragraph - add more context
            response += f"\n\n{sentences[4]}. {sentences[5]}."
            if len(sentences) > 6:
                response += f" {sentences[6]}."

        if len(sentences) >= 10:
            # Fourth paragraph - additional details
            response += f"\n\n{sentences[7]}. {sentences[8]}."
            if len(sentences) > 9:
                response += f" {sentences[9]}."

        # Add a natural closing if we have enough content
        if len(sentences) >= 6:
            # Add a helpful closing
            closing_phrases = [
                "\n\nLet me know if you'd like to know more about any specific aspect.",
                "\n\nFeel free to ask if you need more details about this topic.",
                "\n\nI can provide more information if you have specific questions.",
                "\n\nWould you like to know more about any particular area?"
            ]
            # Pick based on query length to add variety
            closing_index = len(query) % len(closing_phrases)
            response += closing_phrases[closing_index]

        return response