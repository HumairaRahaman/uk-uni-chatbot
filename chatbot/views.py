from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

# Set environment variable to disable tokenizers parallelism warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'chatbot', 'universities_data.txt')

# Global variables to store services (lazy initialization)
_rag_service = None
_chatbot_service = None

def get_services():
    """Initialize services lazily to avoid fork issues"""
    global _rag_service, _chatbot_service
    if _rag_service is None or _chatbot_service is None:
        from chatbot.enhanced_rag_service import EnhancedRAGService
        from chatbot.chatbot_service import ChatbotService
        _rag_service = EnhancedRAGService(DATA_FILE)
        _chatbot_service = ChatbotService(_rag_service)
    return _rag_service, _chatbot_service

def index(request):
    """Render chatbot interface"""
    return render(request, 'chatbot/index.html')

@csrf_exempt
def chat(request):
    """Handle chat requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Get services and response from chatbot
            rag_service, chatbot_service = get_services()
            response = chatbot_service.get_response(user_message)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def reload_data(request):
    """Reload data from file"""
    if request.method == 'POST':
        try:
            rag_service, chatbot_service = get_services()
            rag_service.reload_data()
            return JsonResponse({
                'status': 'success',
                'message': 'Data reloaded successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def refetch_and_reload_data(request):
    """Refetch data from Wikipedia and reload into ChromaDB"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', 'https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom')

            rag_service, chatbot_service = get_services()
            success = rag_service.refetch_and_reload_data(url)

            if success:
                stats = rag_service.get_stats()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Data successfully refetched from {url} and reloaded',
                    'stats': stats
                })
            else:
                return JsonResponse({
                    'error': 'Failed to refetch and reload data. Check if Firecrawl API key is set.'
                }, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def add_web_content(request):
    """Add web content to knowledge base using Firecrawl"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            max_pages = data.get('max_pages', 1)

            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)

            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            rag_service, chatbot_service = get_services()
            success = rag_service.add_web_content(url, max_pages=max_pages)

            if success:
                stats = rag_service.get_stats()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully added content from {url}',
                    'stats': stats
                })
            else:
                return JsonResponse({
                    'error': 'Failed to scrape content. Check if Firecrawl API key is set and URL is accessible.'
                }, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def add_search_content(request):
    """Search web and add relevant content to knowledge base"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            max_results = data.get('max_results', 3)

            if not query:
                return JsonResponse({'error': 'Search query is required'}, status=400)

            rag_service, chatbot_service = get_services()
            success = rag_service.add_search_results(query, max_results=max_results)

            if success:
                stats = rag_service.get_stats()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully added search results for "{query}"',
                    'stats': stats
                })
            else:
                return JsonResponse({
                    'error': 'Failed to search and add content. Check if Firecrawl API key is set.'
                }, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def get_knowledge_stats(request):
    """Get statistics about the knowledge base"""
    if request.method == 'GET':
        try:
            rag_service, chatbot_service = get_services()
            stats = rag_service.get_stats()
            return JsonResponse({
                'status': 'success',
                'stats': stats
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET requests allowed'}, status=405)

@csrf_exempt
def clear_web_content(request):
    """Clear all web-scraped content from knowledge base"""
    if request.method == 'POST':
        try:
            rag_service, chatbot_service = get_services()
            rag_service.clear_web_content()
            stats = rag_service.get_stats()
            return JsonResponse({
                'status': 'success',
                'message': 'Web content cleared successfully',
                'stats': stats
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

@csrf_exempt
def search_with_sources(request):
    """Search knowledge base and return results with source information"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            source_filter = data.get('source_filter')  # 'web_scrape', 'local_file', or None

            if not query:
                return JsonResponse({'error': 'Search query is required'}, status=400)

            rag_service, chatbot_service = get_services()
            sources = rag_service.get_sources(query, n_results=5)

            return JsonResponse({
                'status': 'success',
                'query': query,
                'sources': sources
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
