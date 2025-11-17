from django.urls import path
from chatbot import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('reload/', views.reload_data, name='reload_data'),
    path('refetch-reload/', views.refetch_and_reload_data, name='refetch_reload_data'),
    path('add-web-content/', views.add_web_content, name='add_web_content'),
    path('add-search-content/', views.add_search_content, name='add_search_content'),
    path('knowledge-stats/', views.get_knowledge_stats, name='knowledge_stats'),
    path('clear-web-content/', views.clear_web_content, name='clear_web_content'),
    path('search-sources/', views.search_with_sources, name='search_sources'),
]
