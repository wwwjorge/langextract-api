#!/usr/bin/env python3
"""Test script for LangExtract API."""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional


class LangExtractAPITester:
    """Test client for LangExtract API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def authenticate(self, username: str = "admin", password: str = "admin") -> bool:
        """Authenticate and get access token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            print("✓ Authentication successful")
            return True
            
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def test_health(self) -> bool:
        """Test health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ Health check: {data['status']}")
            
            if "services" in data:
                for service, status in data["services"].items():
                    print(f"  - {service}: {status}")
            
            return data["status"] == "healthy"
            
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False
    
    def test_models(self) -> bool:
        """Test models endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            models = response.json()
            print(f"✓ Available models: {len(models)}")
            
            for model in models[:3]:  # Show first 3 models
                print(f"  - {model['id']} ({model['provider']})")
            
            return len(models) > 0
            
        except Exception as e:
            print(f"✗ Models test failed: {e}")
            return False
    
    def test_text_extraction(self) -> bool:
        """Test text extraction."""
        try:
            # Test data
            test_request = {
                "text": "João Silva trabalha como engenheiro de software na empresa TechCorp desde janeiro de 2020. Ele tem 28 anos e mora em São Paulo.",
                "prompt_description": "Extrair informações sobre pessoas incluindo nome, idade, profissão, empresa e localização",
                "examples": [
                    {
                        "input": "Maria Santos é médica no Hospital ABC e tem 35 anos.",
                        "output": {
                            "nome": "Maria Santos",
                            "idade": 35,
                            "profissao": "médica",
                            "empresa": "Hospital ABC",
                            "localizacao": null
                        }
                    }
                ],
                "model_id": "gemma2:2b",
                "temperature": 0.1,
                "format_type": "json",
                "debug": True
            }
            
            print("Starting text extraction...")
            response = self.session.post(
                f"{self.base_url}/extract/text",
                json=test_request
            )
            response.raise_for_status()
            
            result = response.json()
            extraction_id = result["extraction_id"]
            
            print(f"✓ Extraction started: {extraction_id}")
            print(f"  Status: {result['status']}")
            
            # Wait for completion
            max_wait = 60  # seconds
            wait_time = 0
            
            while wait_time < max_wait:
                status_response = self.session.get(
                    f"{self.base_url}/extract/status/{extraction_id}"
                )
                status_response.raise_for_status()
                
                status_data = status_response.json()
                current_status = status_data["status"]
                
                print(f"  Status: {current_status}")
                
                if current_status == "completed":
                    print("✓ Extraction completed successfully")
                    
                    # Show results
                    if "results" in status_data and status_data["results"]:
                        print("  Results:")
                        for i, result in enumerate(status_data["results"][:2]):
                            print(f"    {i+1}. {json.dumps(result, indent=6, ensure_ascii=False)}")
                    
                    # Test download
                    download_response = self.session.get(
                        f"{self.base_url}/extract/download/{extraction_id}/json"
                    )
                    if download_response.status_code == 200:
                        print("✓ Download successful")
                    
                    return True
                    
                elif current_status == "failed":
                    error = status_data.get("error", "Unknown error")
                    print(f"✗ Extraction failed: {error}")
                    return False
                
                time.sleep(2)
                wait_time += 2
            
            print(f"✗ Extraction timeout after {max_wait}s")
            return False
            
        except Exception as e:
            print(f"✗ Text extraction test failed: {e}")
            return False
    
    def test_file_upload(self) -> bool:
        """Test file upload and extraction."""
        try:
            # Create a test file
            test_file_path = Path("test_document.txt")
            test_content = """
Relatório de Funcionários - TechCorp

1. Ana Costa - Desenvolvedora Frontend
   - Idade: 26 anos
   - Departamento: Tecnologia
   - Salário: R$ 8.500
   - Email: ana.costa@techcorp.com

2. Carlos Oliveira - Gerente de Projetos
   - Idade: 34 anos
   - Departamento: Gestão
   - Salário: R$ 12.000
   - Email: carlos.oliveira@techcorp.com

3. Beatriz Santos - Designer UX/UI
   - Idade: 29 anos
   - Departamento: Design
   - Salário: R$ 7.800
   - Email: beatriz.santos@techcorp.com
"""
            
            test_file_path.write_text(test_content, encoding="utf-8")
            
            print("Testing file upload...")
            
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                data = {
                    "prompt_description": "Extrair informações de funcionários incluindo nome, cargo, idade, departamento, salário e email",
                    "model_id": "gemma2:2b",
                    "temperature": "0.1",
                    "format_type": "json"
                }
                
                response = self.session.post(
                    f"{self.base_url}/extract/file",
                    files=files,
                    data=data
                )
                response.raise_for_status()
            
            result = response.json()
            extraction_id = result["extraction_id"]
            
            print(f"✓ File upload successful: {extraction_id}")
            
            # Clean up test file
            test_file_path.unlink()
            
            # Wait for completion (simplified)
            time.sleep(5)
            
            status_response = self.session.get(
                f"{self.base_url}/extract/status/{extraction_id}"
            )
            status_response.raise_for_status()
            
            status_data = status_response.json()
            print(f"  Final status: {status_data['status']}")
            
            return status_data["status"] in ["completed", "processing"]
            
        except Exception as e:
            print(f"✗ File upload test failed: {e}")
            # Clean up test file if it exists
            if test_file_path.exists():
                test_file_path.unlink()
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("🧪 LangExtract API Test Suite")
        print("=" * 40)
        
        results = {}
        
        # Test 1: Health check (no auth required)
        print("\n1. Testing health endpoint...")
        results["health"] = self.test_health()
        
        # Test 2: Authentication
        print("\n2. Testing authentication...")
        results["auth"] = self.authenticate()
        
        if not results["auth"]:
            print("⚠️ Skipping authenticated tests due to auth failure")
            return results
        
        # Test 3: Models endpoint
        print("\n3. Testing models endpoint...")
        results["models"] = self.test_models()
        
        # Test 4: Text extraction
        print("\n4. Testing text extraction...")
        results["text_extraction"] = self.test_text_extraction()
        
        # Test 5: File upload
        print("\n5. Testing file upload...")
        results["file_upload"] = self.test_file_upload()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary."""
        print("\n" + "=" * 40)
        print("📊 Test Summary")
        print("=" * 40)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✓ PASS" if passed_test else "✗ FAIL"
            print(f"{test_name:20} {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above.")
        
        print("\n💡 Next steps:")
        print("- Check API documentation: http://localhost:8000/docs")
        print("- View logs: docker-compose logs -f langextract-api")
        print("- Test with your own data using the API endpoints")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LangExtract API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--username",
        default="admin",
        help="Username for authentication (default: admin)"
    )
    parser.add_argument(
        "--password",
        default="admin",
        help="Password for authentication (default: admin)"
    )
    
    args = parser.parse_args()
    
    # Create tester
    tester = LangExtractAPITester(args.url)
    
    # Run tests
    results = tester.run_all_tests()
    
    # Print summary
    tester.print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()