#!/usr/bin/env python
"""
Test script to verify the refetch and reload functionality
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_refetch_reload():
    """Test the refetch and reload endpoint"""
    print("Testing refetch and reload functionality...")
    print("-" * 50)

    # Test the refetch endpoint
    url = f'{BASE_URL}/refetch-reload/'
    data = {
        'url': 'https://en.wikipedia.org/wiki/Universities_in_the_United_Kingdom'
    }

    print(f"Sending POST request to {url}")
    print(f"Payload: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("\nSUCCESS! Data refetched and reloaded successfully")
                stats = result.get('stats', {})
                print(f"\nKnowledge Base Statistics:")
                print(f"  Total chunks: {stats.get('total_chunks', 0)}")
                print(f"  File chunks: {stats.get('file_chunks', 0)}")
                print(f"  Web chunks: {stats.get('web_chunks', 0)}")
            else:
                print("\nFAILED! Check the error message above")
        else:
            print(f"\nFAILED with status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server. Is Django running on port 8000?")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

def test_get_stats():
    """Test the knowledge stats endpoint"""
    print("\n" + "=" * 50)
    print("Testing knowledge stats endpoint...")
    print("-" * 50)

    url = f'{BASE_URL}/knowledge-stats/'

    try:
        response = requests.get(url)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response Body:")
            print(json.dumps(result, indent=2))
            print("\nStats retrieved successfully")
        else:
            print(f"\nFAILED with status code {response.status_code}")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

def test_chat():
    """Test a simple chat query"""
    print("\n" + "=" * 50)
    print("Testing chat with refetched data...")
    print("-" * 50)

    url = f'{BASE_URL}/chat/'
    data = {
        'message': 'Tell me about Oxford University'
    }

    try:
        response = requests.post(url, json=data)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nBot Response:")
            print(result.get('response', 'No response'))
            print("\nChat test successful")
        else:
            print(f"\nFAILED with status code {response.status_code}")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == '__main__':
    print("=" * 50)
    print("TESTING REFETCH AND RELOAD FUNCTIONALITY")
    print("=" * 50)

    # Run tests
    test_refetch_reload()
    test_get_stats()
    test_chat()

    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)

