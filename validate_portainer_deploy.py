#!/usr/bin/env python3
"""
Script de validação para deploy do LangExtract API no Portainer
Verifica se todos os serviços estão funcionando corretamente
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class PortainerDeployValidator:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "ENDC": "\033[0m"
        }
        print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['ENDC']} {message}")
    
    def test_health_check(self) -> bool:
        """Test API health endpoint"""
        try:
            self.print_status("Testando health check...")
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.print_status("✓ Health check passou", "SUCCESS")
                    return True
                else:
                    self.print_status(f"✗ Health check falhou: {data}", "ERROR")
                    return False
            else:
                self.print_status(f"✗ Health check falhou: HTTP {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"✗ Erro de conexão no health check: {e}", "ERROR")
            return False
    
    def test_authentication(self, username: str = "admin", password: str = "admin") -> bool:
        """Test authentication endpoint"""
        try:
            self.print_status("Testando autenticação...")
            
            # Test token generation
            auth_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/token",
                data=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                
                if self.token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    self.print_status("✓ Autenticação bem-sucedida", "SUCCESS")
                    return True
                else:
                    self.print_status("✗ Token não encontrado na resposta", "ERROR")
                    return False
            else:
                self.print_status(f"✗ Falha na autenticação: HTTP {response.status_code}", "ERROR")
                if response.status_code == 401:
                    self.print_status("  Verifique as credenciais padrão (admin/admin)", "WARNING")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"✗ Erro de conexão na autenticação: {e}", "ERROR")
            return False
    
    def test_models_endpoint(self) -> bool:
        """Test models listing endpoint"""
        try:
            self.print_status("Testando endpoint de modelos...")
            
            if not self.token:
                self.print_status("✗ Token não disponível para teste de modelos", "ERROR")
                return False
            
            response = self.session.get(f"{self.api_url}/models", timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                if isinstance(models, list) and len(models) > 0:
                    self.print_status(f"✓ Modelos disponíveis: {len(models)}", "SUCCESS")
                    for model in models[:3]:  # Show first 3 models
                        self.print_status(f"  - {model.get('id', 'N/A')} ({model.get('provider', 'N/A')})", "INFO")
                    return True
                else:
                    self.print_status("⚠ Nenhum modelo disponível", "WARNING")
                    return False
            else:
                self.print_status(f"✗ Falha ao listar modelos: HTTP {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"✗ Erro de conexão no endpoint de modelos: {e}", "ERROR")
            return False
    
    def test_text_extraction(self) -> bool:
        """Test text extraction endpoint"""
        try:
            self.print_status("Testando extração de texto...")
            
            if not self.token:
                self.print_status("✗ Token não disponível para teste de extração", "ERROR")
                return False
            
            # Simple extraction test
            extraction_data = {
                "text": "John Doe trabalha na empresa ABC como desenvolvedor. Ele tem 30 anos e mora em São Paulo.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "empresa": {"type": "string"},
                        "cargo": {"type": "string"},
                        "idade": {"type": "integer"},
                        "cidade": {"type": "string"}
                    }
                }
            }
            
            response = self.session.post(
                f"{self.api_url}/extract/text",
                json=extraction_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                
                if job_id:
                    self.print_status(f"✓ Extração iniciada (Job ID: {job_id})", "SUCCESS")
                    
                    # Wait for completion
                    max_wait = 30
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        status_response = self.session.get(f"{self.api_url}/extract/status/{job_id}")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get("status")
                            
                            if status == "completed":
                                self.print_status("✓ Extração completada com sucesso", "SUCCESS")
                                return True
                            elif status == "failed":
                                error = status_data.get("error", "Erro desconhecido")
                                self.print_status(f"✗ Extração falhou: {error}", "ERROR")
                                return False
                            elif status in ["pending", "processing"]:
                                self.print_status(f"  Status: {status}... aguardando", "INFO")
                                time.sleep(2)
                                wait_time += 2
                            else:
                                self.print_status(f"✗ Status desconhecido: {status}", "ERROR")
                                return False
                        else:
                            self.print_status(f"✗ Erro ao verificar status: HTTP {status_response.status_code}", "ERROR")
                            return False
                    
                    self.print_status("⚠ Timeout aguardando conclusão da extração", "WARNING")
                    return False
                else:
                    self.print_status("✗ Job ID não encontrado na resposta", "ERROR")
                    return False
            else:
                self.print_status(f"✗ Falha na extração: HTTP {response.status_code}", "ERROR")
                if response.status_code == 422:
                    self.print_status("  Verifique se o schema está correto", "WARNING")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"✗ Erro de conexão na extração: {e}", "ERROR")
            return False
    
    def test_documentation_endpoints(self) -> bool:
        """Test documentation endpoints"""
        try:
            self.print_status("Testando endpoints de documentação...")
            
            # Test Swagger UI
            swagger_response = self.session.get(f"{self.api_url}/docs", timeout=10)
            if swagger_response.status_code == 200:
                self.print_status("✓ Swagger UI acessível", "SUCCESS")
            else:
                self.print_status(f"✗ Swagger UI inacessível: HTTP {swagger_response.status_code}", "ERROR")
                return False
            
            # Test ReDoc
            redoc_response = self.session.get(f"{self.api_url}/redoc", timeout=10)
            if redoc_response.status_code == 200:
                self.print_status("✓ ReDoc acessível", "SUCCESS")
            else:
                self.print_status(f"✗ ReDoc inacessível: HTTP {redoc_response.status_code}", "ERROR")
                return False
            
            return True
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"✗ Erro de conexão nos endpoints de documentação: {e}", "ERROR")
            return False
    
    def run_validation(self, username: str = "admin", password: str = "admin") -> Dict[str, bool]:
        """Run all validation tests"""
        self.print_status("=" * 60)
        self.print_status("INICIANDO VALIDAÇÃO DO DEPLOY PORTAINER")
        self.print_status(f"API URL: {self.api_url}")
        self.print_status("=" * 60)
        
        results = {}
        
        # Test 1: Health Check
        results["health_check"] = self.test_health_check()
        
        # Test 2: Authentication
        results["authentication"] = self.test_authentication(username, password)
        
        # Test 3: Models Endpoint
        results["models_endpoint"] = self.test_models_endpoint()
        
        # Test 4: Text Extraction
        results["text_extraction"] = self.test_text_extraction()
        
        # Test 5: Documentation
        results["documentation"] = self.test_documentation_endpoints()
        
        # Summary
        self.print_status("=" * 60)
        self.print_status("RESUMO DA VALIDAÇÃO")
        self.print_status("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASSOU" if result else "✗ FALHOU"
            color = "SUCCESS" if result else "ERROR"
            self.print_status(f"{test_name.replace('_', ' ').title()}: {status}", color)
        
        self.print_status("=" * 60)
        if passed == total:
            self.print_status(f"🎉 TODOS OS TESTES PASSARAM ({passed}/{total})", "SUCCESS")
            self.print_status("Deploy está funcionando corretamente!", "SUCCESS")
        else:
            self.print_status(f"⚠ ALGUNS TESTES FALHARAM ({passed}/{total})", "WARNING")
            self.print_status("Verifique os logs e configurações", "WARNING")
        
        self.print_status("=" * 60)
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validar deploy do LangExtract API no Portainer")
    parser.add_argument("--url", default="http://localhost:8000", help="URL da API")
    parser.add_argument("--username", default="admin", help="Username para autenticação")
    parser.add_argument("--password", default="admin", help="Password para autenticação")
    
    args = parser.parse_args()
    
    validator = PortainerDeployValidator(args.url)
    results = validator.run_validation(args.username, args.password)
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()