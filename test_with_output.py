#!/usr/bin/env python3
"""Test LangExtract functionality with JSON output."""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import langextract as lx
import textwrap

def test_extraction_with_output():
    """Test extraction functionality and save results to JSON."""
    print("Testing LangExtract with output file...")
    
    # Define the prompt and extraction rules
    prompt = textwrap.dedent("""\
        Extract characters, emotions, and relationships in order of appearance.
        Use exact text for extractions. Do not paraphrase or overlap entities.
        Provide meaningful attributes for each entity to add context.""")

    # Provide examples
    examples = [
        lx.data.ExampleData(
            text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="character",
                    extraction_text="ROMEO",
                    attributes={"emotional_state": "wonder"}
                ),
                lx.data.Extraction(
                    extraction_class="emotion",
                    extraction_text="But soft!",
                    attributes={"feeling": "gentle awe"}
                ),
                lx.data.Extraction(
                    extraction_class="relationship",
                    extraction_text="Juliet is the sun",
                    attributes={"type": "metaphor"}
                ),
            ]
        )
    ]

    # Test texts
    test_texts = [
        "Lady Juliet gazed longingly at the stars, her heart aching for Romeo",
        "The angry king shouted at his servants, demanding immediate action",
        "Maria smiled warmly at her children, feeling grateful for their love"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "examples_count": len(examples),
        "tests": []
    }
    
    # Check available providers
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print(f"OpenAI API Key available: {'Yes' if openai_key else 'No'}")
    print(f"Gemini API Key available: {'Yes' if gemini_key else 'No'}")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Input: {text}")
        
        test_result = {
            "test_number": i,
            "input_text": text,
            "extractions": {}
        }
        
        # Try OpenAI first
        if openai_key:
            print("\nTrying with OpenAI (gpt-4o-mini)...")
            try:
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=prompt,
                    examples=examples,
                    model_id="gpt-4o-mini",
                )
                
                openai_extractions = []
                for extraction in result.extractions:
                    openai_extractions.append({
                        "class": extraction.extraction_class,
                        "text": extraction.extraction_text,
                        "attributes": extraction.attributes or {}
                    })
                
                test_result["extractions"]["openai_gpt4o_mini"] = {
                    "success": True,
                    "count": len(openai_extractions),
                    "extractions": openai_extractions
                }
                
                print(f"OpenAI Success! Found {len(openai_extractions)} extractions")
                for j, ext in enumerate(openai_extractions, 1):
                    print(f"  {j}. {ext['class']}: '{ext['text']}'")
                    if ext['attributes']:
                        print(f"     Attributes: {ext['attributes']}")
                        
            except Exception as e:
                test_result["extractions"]["openai_gpt4o_mini"] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"OpenAI failed: {e}")
        
        # Try Ollama if available
        try:
            import requests
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    # Try with a lightweight model
                    model_name = 'tinyllama:1.1b'  # Use the lightest model
                    print(f"\nTrying with Ollama ({model_name})...")
                    try:
                        result = lx.extract(
                            text_or_documents=text,
                            prompt_description=prompt,
                            examples=examples,
                            model_id=model_name,
                        )
                        
                        ollama_extractions = []
                        for extraction in result.extractions:
                            ollama_extractions.append({
                                "class": extraction.extraction_class,
                                "text": extraction.extraction_text,
                                "attributes": extraction.attributes or {}
                            })
                        
                        test_result["extractions"][f"ollama_{model_name.replace(':', '_')}"] = {
                            "success": True,
                            "count": len(ollama_extractions),
                            "extractions": ollama_extractions
                        }
                        
                        print(f"Ollama Success! Found {len(ollama_extractions)} extractions")
                        for j, ext in enumerate(ollama_extractions, 1):
                            print(f"  {j}. {ext['class']}: '{ext['text']}'")
                            if ext['attributes']:
                                print(f"     Attributes: {ext['attributes']}")
                                
                    except Exception as e:
                        test_result["extractions"][f"ollama_{model_name.replace(':', '_')}"] = {
                            "success": False,
                            "error": str(e)
                        }
                        print(f"Ollama failed: {e}")
        except Exception as e:
            print(f"Ollama not available: {e}")
        
        results["tests"].append(test_result)
    
    # Save results to JSON file
    output_file = "langextract_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total tests: {len(test_texts)}")
    print(f"Results saved to: {output_file}")
    print(f"Timestamp: {results['timestamp']}")
    
    # Print summary statistics
    for test in results["tests"]:
        print(f"\nTest {test['test_number']}: '{test['input_text'][:50]}...'")
        for provider, result in test["extractions"].items():
            if result["success"]:
                print(f"  {provider}: {result['count']} extractions")
            else:
                print(f"  {provider}: FAILED - {result['error']}")

if __name__ == "__main__":
    test_extraction_with_output()