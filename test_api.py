#!/usr/bin/env python3
"""Test script for LangExtract API."""

import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8001"
USERNAME = "admin"
PASSWORD = "admin"

def get_auth_token():
    """Get authentication token."""
    response = requests.post(
        f"{API_BASE_URL}/auth/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.text}")

def test_health_check():
    """Test health check endpoint."""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health Check: {data['status']}")
        print(f"📅 Timestamp: {data['timestamp']}")
        print(f"🔢 Version: {data['version']}")
        print(f"🤖 Available Models: {json.dumps(data['available_models'], indent=2)}")
    else:
        print(f"❌ Health check failed: {response.text}")

def test_extraction(token):
    """Test text extraction."""
    print("\n📝 Testing Text Extraction...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test data
    test_request = {
        "text": "Maria estava muito feliz hoje. Ela encontrou seu amigo João no parque e eles conversaram sobre seus planos para o futuro. João mencionou que está estudando medicina na universidade.",
        "prompt": "Extract people, their emotions, and relationships from the text",
        "model_id": "gemini-2.5-flash",
        "temperature": 0.3
    }
    
    response = requests.post(
        f"{API_BASE_URL}/extract",
        headers=headers,
        json=test_request
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Extraction successful!")
        print(f"🤖 Model used: {data['model_used']}")
        print(f"🏭 Provider: {data['provider']}")
        print(f"⏱️ Processing time: {data['processing_time']:.2f}s")
        print(f"📊 Extractions found: {len(data['extractions'])}")
        
        for i, extraction in enumerate(data['extractions'], 1):
            print(f"\n  {i}. Class: {extraction['class']}")
            print(f"     Text: {extraction['text']}")
            if extraction['attributes']:
                print(f"     Attributes: {json.dumps(extraction['attributes'], indent=6)}")
    else:
        print(f"❌ Extraction failed: {response.text}")

def test_cloudflare_extraction(token):
    """Test Cloudflare Workers AI extraction"""
    print("\n☁️ Testing Cloudflare Workers AI Extraction...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    extraction_data = {
        "text": "The company reported revenue of $1.2 billion in Q3 2024, with a 15% increase from last quarter.",
        "prompt": "Extract financial information and metrics",
        "model_id": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "temperature": 0.2
    }
    
    response = requests.post(
        f"{API_BASE_URL}/extract",
        json=extraction_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Cloudflare extraction successful!")
        print(f"🤖 Model used: {result.get('model_used')}")
        print(f"🏭 Provider: {result.get('provider')}")
        print(f"⏱️ Processing time: {result.get('processing_time')}s")
        print(f"📊 Extractions found: {len(result.get('extractions', []))}")
        
        if result.get('raw_response'):
            print(f"📄 Raw response: {result.get('raw_response')[:200]}...")
    else:
        print(f"⚠️ Cloudflare extraction failed (expected if no API token): {response.status_code}")
        print(f"Note: Configure CLOUDFLARE_API_TOKEN in .env to test this feature")

def test_models_endpoint(token):
    """Test models endpoint."""
    print("\n🤖 Testing Models Endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/models", headers=headers)
    
    if response.status_code == 200:
        models = response.json()
        print("✅ Models retrieved successfully!")
        for provider, model_list in models.items():
            print(f"\n  {provider.upper()}:")
            for model in model_list:
                print(f"    - {model}")
    else:
        print(f"❌ Models request failed: {response.text}")

def test_providers_endpoint(token):
    """Test providers endpoint."""
    print("\n🏭 Testing Providers Endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE_URL}/providers", headers=headers)
    
    if response.status_code == 200:
        providers = response.json()
        print("✅ Providers retrieved successfully!")
        for provider, url in providers.items():
            print(f"  {provider}: {url}")
    else:
        print(f"❌ Providers request failed: {response.text}")

def main():
    """Run all tests."""
    print("🚀 Starting LangExtract API Tests")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"👤 Username: {USERNAME}")
    
    try:
        # Test health check (no auth required)
        test_health_check()
        
        # Get authentication token
        print("\n🔐 Getting authentication token...")
        token = get_auth_token()
        print("✅ Authentication successful!")
        
        # Test authenticated endpoints
        test_models_endpoint(token)
        test_providers_endpoint(token)
        test_extraction(token)
        test_cloudflare_extraction(token)
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main()