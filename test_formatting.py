#!/usr/bin/env python
"""
Test the improved formatting of chatbot responses
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_formatted_response():
    """Test chat with formatted response"""
    print("=" * 60)
    print("TESTING FORMATTED CHATBOT RESPONSES")
    print("=" * 60)

    queries = [
        "What is the major part of university life for students?",
        "Tell me about Oxford University",
        "What are student accommodations like?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 60)

        try:
            response = requests.post(
                f'{BASE_URL}/chat/',
                json={'message': query}
            )

            data = response.json()

            if data['status'] == 'success':
                print("\nResponse received:")
                print(data['response'])
                print("\n" + "=" * 60)
            else:
                print(f"Error: {data.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"Error: {e}")

    print("\nTest complete! Check your browser to see the beautifully formatted responses.")
    print("\nFormatting features:")
    print("  Bold text for emphasis")
    print("  Source badges with icons")
    print("  Horizontal dividers")
    print("  Highlighted tip sections")
    print("  Clickable links")
    print("  Better spacing and typography")

if __name__ == '__main__':
    test_formatted_response()

