#!/usr/bin/env python3
"""Test basic LangExtract functionality."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import langextract as lx
import textwrap

def test_basic_extraction():
    """Test basic extraction functionality."""
    print("Testing LangExtract basic functionality...")
    
    # 1. Define the prompt and extraction rules
    prompt = textwrap.dedent("""\
        Extract characters, emotions, and relationships in order of appearance.
        Use exact text for extractions. Do not paraphrase or overlap entities.
        Provide meaningful attributes for each entity to add context.""")

    # 2. Provide a high-quality example to guide the model
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

    # The input text to be processed
    input_text = "Lady Juliet gazed longingly at the stars, her heart aching for Romeo"

    print(f"Input text: {input_text}")
    print(f"Prompt: {prompt}")
    print(f"Examples provided: {len(examples)}")
    
    # Check available providers
    print("\nChecking available providers...")
    try:
        # Try to get available models/providers
        print("LangExtract modules available:", [attr for attr in dir(lx) if not attr.startswith('_')])
        
        # Check if we have API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        print(f"OpenAI API Key available: {'Yes' if openai_key else 'No'}")
        print(f"Gemini API Key available: {'Yes' if gemini_key else 'No'}")
        
        # Try extraction with available provider
        if openai_key:
            print("\nTrying extraction with OpenAI...")
            try:
                result = lx.extract(
                    text_or_documents=input_text,
                    prompt_description=prompt,
                    examples=examples,
                    model_id="gpt-4o-mini",
                )
                print("Extraction successful!")
                print(f"Number of extractions: {len(result.extractions)}")
                for i, extraction in enumerate(result.extractions):
                    print(f"  {i+1}. Class: {extraction.extraction_class}, Text: '{extraction.extraction_text}'")
                    if extraction.attributes:
                        print(f"     Attributes: {extraction.attributes}")
                        
            except Exception as e:
                print(f"OpenAI extraction failed: {e}")
                
        elif gemini_key:
            print("\nTrying extraction with Gemini...")
            try:
                result = lx.extract(
                    text_or_documents=input_text,
                    prompt_description=prompt,
                    examples=examples,
                    model_id="gemini-2.5-flash",
                )
                print("Extraction successful!")
                print(f"Number of extractions: {len(result.extractions)}")
                for i, extraction in enumerate(result.extractions):
                    print(f"  {i+1}. Class: {extraction.extraction_class}, Text: '{extraction.extraction_text}'")
                    if extraction.attributes:
                        print(f"     Attributes: {extraction.attributes}")
                        
            except Exception as e:
                print(f"Gemini extraction failed: {e}")
        else:
            print("\nNo API keys available for cloud providers.")
            print("You can still test with local Ollama models if available.")
            
        # Test Ollama if available
        print("\nTesting Ollama connection...")
        try:
            import requests
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"Ollama is available with {len(models)} models")
                if models:
                    print("Available models:", [model.get('name', 'unknown') for model in models[:3]])
                    
                    # Try extraction with first available model
                    first_model = models[0].get('name')
                    if first_model:
                        print(f"\nTrying extraction with Ollama model: {first_model}")
                        try:
                            result = lx.extract(
                                text_or_documents=input_text,
                                prompt_description=prompt,
                                examples=examples,
                                model_id=first_model,
                            )
                            print("Ollama extraction successful!")
                            print(f"Number of extractions: {len(result.extractions)}")
                            for i, extraction in enumerate(result.extractions):
                                print(f"  {i+1}. Class: {extraction.extraction_class}, Text: '{extraction.extraction_text}'")
                                if extraction.attributes:
                                    print(f"     Attributes: {extraction.attributes}")
                        except Exception as e:
                            print(f"Ollama extraction failed: {e}")
            else:
                print("Ollama not available")
        except Exception as e:
            print(f"Ollama connection failed: {e}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_extraction()