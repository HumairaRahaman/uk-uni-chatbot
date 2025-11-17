# How to Use the Refetch Wikipedia Data Feature

## Quick Start Guide

### Using the Web Interface

1. **Open the chatbot in your browser**
   - Navigate to: http://localhost:8000
   - You should see the chatbot interface with a header containing buttons

2. **Click the "Refetch Wikipedia Data" button**
   - Located in the header section
   - Green button with text "Refetch Wikipedia Data"

3. **Confirm the action**
   - A confirmation dialog will appear
   - Click "OK" to proceed or "Cancel" to abort

4. **Wait for completion**
   - The stats display will show "🔄 Fetching data from Wikipedia..."
   - This typically takes 10-30 seconds
   - Do not close the browser during this time

5. **Check the results**
   - Success alert will appear: "✅ Data successfully refetched from ... and reloaded"
   - Statistics will update showing the number of chunks loaded
   - Example: "📊 Knowledge Base: 127 chunks (📁 127 from files, 🌐 0 from web)"

6. **Test the new data**
   - Ask questions in the chat
   - The bot will use the freshly fetched Wikipedia data

### Using the API (curl)

```bash
# Basic usage (uses default Wikipedia URL)
curl -X POST http://localhost:8000/refetch-reload/ \
  -H "Content-Type: application/json" \
  -d '{}'

# With custom URL
curl -X POST http://localhost:8000/refetch-reload/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom"}'
```

### Using Python

```python
import requests

# Refetch data
response = requests.post(
    'http://localhost:8000/refetch-reload/',
    json={'url': 'https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom'}
)

result = response.json()
if result['status'] == 'success':
    print(f"Success! {result['message']}")
    print(f"Stats: {result['stats']}")
else:
    print(f"Error: {result['error']}")
```

## What Happens Behind the Scenes

1. **Firecrawl API Call**
   - Connects to Firecrawl service using your API key
   - Scrapes the Wikipedia page
   - Extracts clean markdown content

2. **File Save**
   - Saves scraped content to: `chatbot/universities_data.txt`
   - Includes title and source URL
   - Overwrites previous content

3. **ChromaDB Update**
   - Deletes old file-based chunks from vector database
   - Chunks the new content (approximately 500 characters per chunk)
   - Creates vector embeddings using sentence-transformers
   - Stores in ChromaDB for semantic search

4. **Response**
   - Returns success status
   - Includes updated statistics
   - Ready for immediate use in chat

## Troubleshooting

### Error: "Failed to refetch and reload data. Check if Firecrawl API key is set."

**Solution:** 
- Check your `.env` file has `FIRECRAWL_API_KEY=your_key_here`
- Make sure the API key is valid
- Verify the key has sufficient credits

### Error: "Could not connect to server"

**Solution:**
- Make sure Django server is running: `python manage.py runserver 8000`
- Check the URL is correct: http://localhost:8000

### Slow Performance

**Normal behavior:**
- First fetch takes 15-30 seconds (Wikipedia page is large)
- Subsequent refetches are similar duration
- This is normal for web scraping + vector embedding creation

### No New Data in Chat

**Solution:**
- Verify the refetch completed successfully (check alert message)
- Check the statistics updated (file_chunks should be > 0)
- Try a different query
- Check the browser console for JavaScript errors

## Benefits of This Feature

✅ **Fresh Data**: Get the latest information from Wikipedia
✅ **Persistent Storage**: Data saved locally in `universities_data.txt`
✅ **Vector Search**: Automatic embedding creation for semantic search
✅ **User-Friendly**: Simple button click interface
✅ **API Available**: Can be automated or integrated into other tools
✅ **Error Handling**: Clear error messages and status updates

## Technical Details

- **Endpoint**: `POST /refetch-reload/`
- **Default URL**: https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom
- **Data File**: `chatbot/universities_data.txt`
- **Vector DB**: ChromaDB (in-memory)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Chunk Size**: ~500 characters
- **API Requirements**: Firecrawl API key

## Example Usage Scenarios

1. **Daily Updates**: Refetch data daily to keep information current
2. **Different Topics**: Change URL to scrape different Wikipedia pages
3. **Backup**: The local file serves as a backup of scraped data
4. **Development**: Quickly test with fresh data without manual copying
5. **Integration**: Automate refetching via API in cron jobs or scripts

---

**Need Help?**
- Check the logs in your terminal where Django is running
- Look for error messages in the browser console (F12)
- Verify all environment variables are set correctly
- Check that the Firecrawl API is accessible

