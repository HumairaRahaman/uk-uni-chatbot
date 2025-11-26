from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from chatbot.chatbot_service import ChatbotService
from chatbot.enhanced_rag_service import EnhancedRAGService
import os

# Initialize services
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_file = os.path.join(BASE_DIR, 'chatbot', 'universities_data.txt')

try:
    rag_service = EnhancedRAGService(data_file)
    chatbot_service = ChatbotService(rag_service)
    print("✅ Services initialized successfully")
except Exception as e:
    print(f"❌ Error initializing services: {e}")
    print(traceback.format_exc())
    rag_service = None
    chatbot_service = None


def index(request):
    """Render the chatbot interface"""
    return render(request, 'chatbot/index.html')


@csrf_exempt
def chat(request):
    """Handle chat messages - ALWAYS returns success:True"""
    if request.method == 'POST':
        try:
            # Parse request
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({
                    'response': 'Please enter a message.',
                    'success': True  # Changed to True so frontend displays it
                })

            # Check if services are initialized
            if not chatbot_service:
                return JsonResponse({
                    'response': 'Chatbot service is not available. Please restart the server.',
                    'success': True  # Changed to True so frontend displays it
                })

            # Get response from chatbot
            print(f"\n{'=' * 60}")
            print(f"💬 User asked: {user_message}")
            print(f"{'=' * 60}")

            response = chatbot_service.get_response(user_message)

            print(f"\n✅ Response ready ({len(response)} characters)")
            print(f"{'=' * 60}\n")

            # ALWAYS return success:True so the response is displayed
            return JsonResponse({
                'response': response,
                'success': True
            })

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return JsonResponse({
                'response': 'Invalid request format. Please try again.',
                'success': True  # Still True so message displays
            })

        except Exception as e:
            # Log the full error for debugging
            print(f"\n{'=' * 60}")
            print(f"❌ ERROR in chat endpoint:")
            print(f"{'=' * 60}")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print(f"{'=' * 60}\n")

            # Return user-friendly error message but with success:True
            return JsonResponse({
                'response': f'An error occurred: {str(e)}\n\nPlease check the server console for details.',
                'success': True  # Changed to True so error message displays
            })

    return JsonResponse({
        'response': 'Invalid request method. Please use POST.',
        'success': True
    })


@csrf_exempt
def reload_data(request):
    """Reload data from the text file"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'message': 'RAG service not available',
                    'success': False
                }, status=500)

            rag_service.reload_data()
            return JsonResponse({
                'message': 'Data reloaded successfully!',
                'success': True
            })

        except Exception as e:
            print(f"Error reloading data: {str(e)}")
            return JsonResponse({
                'message': f'Error reloading data: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)


@csrf_exempt
def refetch_and_reload_data(request):
    """Refetch data from Wikipedia and reload"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'message': 'RAG service not available',
                    'success': False
                }, status=500)

            data = json.loads(request.body) if request.body else {}
            url = data.get('url', 'https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom')

            success = rag_service.refetch_and_reload_data(url)

            if success:
                return JsonResponse({
                    'message': 'Data refetched and reloaded successfully!',
                    'success': True
                })
            else:
                return JsonResponse({
                    'message': 'Failed to refetch data. Check if Firecrawl API key is configured.',
                    'success': False
                }, status=500)

        except Exception as e:
            print(f"Error refetching data: {str(e)}")
            return JsonResponse({
                'message': f'Error refetching data: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)


@csrf_exempt
def add_web_content(request):
    """Add content from a web URL"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'message': 'RAG service not available',
                    'success': False
                }, status=500)

            data = json.loads(request.body)
            url = data.get('url', '').strip()

            if not url:
                return JsonResponse({
                    'message': 'URL is required',
                    'success': False
                }, status=400)

            success = rag_service.add_web_content(url)

            if success:
                return JsonResponse({
                    'message': f'Successfully added content from {url}',
                    'success': True
                })
            else:
                return JsonResponse({
                    'message': 'Failed to add web content. Check if Firecrawl API key is configured.',
                    'success': False
                }, status=500)

        except Exception as e:
            print(f"Error adding web content: {str(e)}")
            return JsonResponse({
                'message': f'Error: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)


@csrf_exempt
def add_search_content(request):
    """Add content from web search"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'message': 'RAG service not available',
                    'success': False
                }, status=500)

            data = json.loads(request.body)
            query = data.get('query', '').strip()

            if not query:
                return JsonResponse({
                    'message': 'Search query is required',
                    'success': False
                }, status=400)

            # This feature would require additional implementation
            return JsonResponse({
                'message': 'Search and add feature coming soon',
                'success': False
            }, status=501)

        except Exception as e:
            print(f"Error in search content: {str(e)}")
            return JsonResponse({
                'message': f'Error: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)


def get_knowledge_stats(request):
    """Get statistics about the knowledge base"""
    try:
        if not rag_service:
            return JsonResponse({
                'stats': {
                    'total_chunks': 0,
                    'file_chunks': 0,
                    'web_chunks': 0
                },
                'success': False
            })

        stats = rag_service.get_stats()
        return JsonResponse({
            'stats': stats,
            'success': True
        })

    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return JsonResponse({
            'stats': {
                'total_chunks': 0,
                'file_chunks': 0,
                'web_chunks': 0
            },
            'success': False
        })


@csrf_exempt
def clear_web_content(request):
    """Clear all web-scraped content"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'message': 'RAG service not available',
                    'success': False
                }, status=500)

            rag_service.clear_web_content()
            return JsonResponse({
                'message': 'Web content cleared successfully!',
                'success': True
            })

        except Exception as e:
            print(f"Error clearing web content: {str(e)}")
            return JsonResponse({
                'message': f'Error: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)


@csrf_exempt
def search_with_sources(request):
    """Search and return results with sources"""
    if request.method == 'POST':
        try:
            if not rag_service:
                return JsonResponse({
                    'sources': [],
                    'success': False
                }, status=500)

            data = json.loads(request.body)
            query = data.get('query', '').strip()
            n_results = data.get('n_results', 5)

            if not query:
                return JsonResponse({
                    'sources': [],
                    'message': 'Query is required',
                    'success': False
                }, status=400)

            sources = rag_service.get_sources(query, n_results)

            return JsonResponse({
                'sources': sources,
                'success': True
            })

        except Exception as e:
            print(f"Error in search: {str(e)}")
            return JsonResponse({
                'sources': [],
                'message': f'Error: {str(e)}',
                'success': False
            }, status=500)

    return JsonResponse({
        'message': 'Invalid request method',
        'success': False
    }, status=405)