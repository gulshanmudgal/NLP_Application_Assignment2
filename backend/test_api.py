#!/usr/bin/env python3
"""
Test script for the NLP Translation API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_translation():
    """Test the translation endpoint"""
    print("Testing translation endpoint...")
    payload = {
        "text": "Hello, how are you?",
        "source_language": "en",
        "target_language": "hi"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/translate/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_languages():
    """Test the languages endpoint"""
    print("Testing languages endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/languages/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_language_pairs():
    """Test the language pairs endpoint"""
    print("Testing language pairs endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/languages/pairs")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("NLP Translation API Test Suite")
    print("=" * 40)
    
    try:
        test_health()
        test_translation()
        test_languages()
        test_language_pairs()
        print("All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8001")
    except Exception as e:
        print(f"Error: {e}")
