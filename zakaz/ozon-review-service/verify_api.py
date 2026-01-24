#!/usr/bin/env python
"""API VERIFICATION SCRIPT - Проверка всех endpoints"""

import requests
import json
import sys
from typing import Tuple
import time
from openai import OpenAI, AuthenticationError, RateLimitError, APIError

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# API base URL
API_BASE = "http://localhost:8000"

# Statistics
tests_passed = 0
tests_failed = 0
tests_warning = 0

def print_header(title: str):
    """Print section header"""
    print(f"\n{CYAN}{BOLD}{title}{RESET}")
    print("=" * 50)

def check_test(test_name: str, result: bool, message: str = ""):
    """Print test result"""
    global tests_passed, tests_failed, tests_warning
    
    if result:
        print(f"{GREEN}✅{RESET} {test_name}")
        tests_passed += 1
    else:
        if message and message.startswith("WARNING"):
            print(f"{YELLOW}⚠️{RESET} {test_name} - {message}")
            tests_warning += 1
        else:
            print(f"{RED}❌{RESET} {test_name}")
            if message:
                print(f"   └─ Error: {message}")
            tests_failed += 1

def test_endpoint(method: str, endpoint: str, name: str, data=None) -> Tuple[bool, str]:
    """Test an API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return False, f"Unknown method: {method}"
        
        if response.status_code in [200, 201, 202]:
            return True, response.text
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - is server running?"
    except Exception as e:
        return False, str(e)

def main():
    print(f"\n{CYAN}{BOLD}🔍 OZON REVIEW SERVICE - ПРОВЕРКА API{RESET}")
    print("=" * 50)
    
    # 1. Check server connectivity
    print_header("1️⃣  ПРОВЕРКА ПОДКЛЮЧЕНИЯ К СЕРВЕРУ")
    
    try:
        response = requests.get(f"{API_BASE}/api/health/status", timeout=5)
        if response.status_code == 200:
            check_test("Server is responding", True)
        else:
            check_test("Server is responding", False, f"HTTP {response.status_code}")
    except Exception as e:
        print(f"{RED}❌ CRITICAL: Cannot connect to server on {API_BASE}{RESET}")
        print(f"   Please start the server: python main.py")
        sys.exit(1)
    
    # Wait a moment for server to fully initialize
    time.sleep(1)
    
    # 2. Test Health endpoints
    print_header("2️⃣  ПРОВЕРКА HEALTH ENDPOINTS")
    
    success, response = test_endpoint("GET", "/api/health/status", "GET /api/health/status")
    check_test("GET /api/health/status", success, response if not success else "")
    
    success, response = test_endpoint("GET", "/api/health/integrations", "GET /api/health/integrations")
    check_test("GET /api/health/integrations", success, response if not success else "")
    
    # Parse and display integrations status
    if success:
        try:
            data = json.loads(response)
            
            # Check Ozon status
            ozon_configured = data.get('ozon_api', {}).get('configured', False)
            ozon_status = "✅ Configured" if ozon_configured else "❌ Not configured"
            print(f"   └─ Ozon API: {ozon_status}")
            
            # Check OpenAI status
            openai_configured = data.get('openai_api', {}).get('configured', False)
            openai_status = "✅ Configured" if openai_configured else "❌ Not configured"
            print(f"   └─ OpenAI API: {openai_status}")
            
            # Check Database status
            db_configured = data.get('database', {}).get('configured', False)
            db_status = "✅ Configured" if db_configured else "❌ Not configured"
            print(f"   └─ Database: {db_status}")
        except json.JSONDecodeError:
            pass
    
    # 3. Test Review endpoints
    print_header("3️⃣  ПРОВЕРКА REVIEW ENDPOINTS")
    
    success, response = test_endpoint("GET", "/api/reviews", "GET /api/reviews")
    check_test("GET /api/reviews", success, response if not success else "")
    
    success, response = test_endpoint("GET", "/api/reviews?limit=5", "GET /api/reviews?limit=5")
    check_test("GET /api/reviews (with pagination)", success, response if not success else "")
    
    # 4. Test Response endpoints
    print_header("4️⃣  ПРОВЕРКА RESPONSE ENDPOINTS")
    
    success, response = test_endpoint("GET", "/api/responses/history/recent", "GET /api/responses/history/recent")
    check_test("GET /api/responses/history/recent", success, response if not success else "")
    
    # 5. Test Settings endpoints
    print_header("5️⃣  ПРОВЕРКА SETTINGS ENDPOINTS")
    
    success, response = test_endpoint("GET", "/api/settings", "GET /api/settings")
    check_test("GET /api/settings", success, response if not success else "")
    
    # 6. Test Integration test endpoints
    print_header("6️⃣  ПРОВЕРКА TEST ENDPOINTS")
    
    # Test Ozon connection with dummy credentials
    print("Testing Ozon API endpoint...")
    success, response = test_endpoint("POST", "/api/health/test-ozon", "POST /api/health/test-ozon", {
        "client_id": "test",
        "api_key": "test"
    })
    check_test("POST /api/health/test-ozon (accepts requests)", success, response if not success else "")
    
    # Test OpenAI connection with dummy credentials
    print("Testing OpenAI API endpoint...")
    success, response = test_endpoint("POST", "/api/health/test-openai", "POST /api/health/test-openai", {
        "api_key": "test"
    })
    check_test("POST /api/health/test-openai (accepts requests)", success, response if not success else "")
    
    # 7. Summary
    print_header("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    
    print(f"{GREEN}✅ Пройдено:      {tests_passed}{RESET}")
    print(f"{YELLOW}⚠️  Предупреждения: {tests_warning}{RESET}")
    print(f"{RED}❌ Ошибок:        {tests_failed}{RESET}")
    
    print()
    
    if tests_failed == 0:
        print(f"{GREEN}{BOLD}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!{RESET}")
        print("\nСистема полностью готова к использованию.")
        print("Следующие шаги:")
        print("1. Заполните .env файл с вашими API ключами")
        print("2. Откройте админ-панель: http://localhost:8000")
        print("3. Кликните на статус-индикаторы для настройки")
        return 0
    else:
        print(f"{RED}{BOLD}⚠️  НАЙДЕНЫ ПРОБЛЕМЫ!{RESET}")
        print("Пожалуйста, проверьте ошибки выше перед использованием.")
        return 1

def check_openai_key(api_key: str):
    """Detaily check OpenAI API key and diagnose issues"""
    print(f"\n{CYAN}{BOLD}🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА OPENAI КЛЮЧА{RESET}")
    print("=" * 50)
    
    if not api_key:
        print(f"{RED}❌ API ключ не установлен в .env файле{RESET}")
        print("   Установите OPENAI_API_KEY в файле .env")
        return False
    
    # Check key format
    if not api_key.startswith("sk-proj-"):
        print(f"{YELLOW}⚠️  Ключ не имеет стандартного формата sk-proj-...{RESET}")
        print(f"   Ваш ключ начинается с: {api_key[:20]}...")
    else:
        print(f"{GREEN}✅ Формат ключа верный (sk-proj-){RESET}")
    
    # Try to connect
    client = OpenAI(api_key=api_key)
    
    try:
        print("\n📡 Попытка подключения к OpenAI API...")
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'test'}],
            max_tokens=5
        )
        print(f"{GREEN}✅ УСПЕШНО! Ключ работает!{RESET}")
        print(f"   Модель: {response.model}")
        print(f"   Использовано токенов: {response.usage.total_tokens}")
        return True
    
    except AuthenticationError as e:
        print(f"{RED}❌ ОШИБКА АУТЕНТИФИКАЦИИ (401){RESET}")
        print(f"   Причины:")
        print(f"   1. Ключ неправильный или неполный")
        print(f"   2. Ключ был удален / отозван")
        print(f"   3. Ключ скопирован неправильно (могут быть обрезаны концы)")
        print(f"\n   Деталь: {str(e)}")
        return False
    
    except RateLimitError as e:
        print(f"{RED}❌ ОШИБКА RATE LIMIT (429){RESET}")
        print(f"   Причина: слишком много запросов за короткое время")
        print(f"   Подождите несколько минут и попробуйте снова")
        print(f"\n   Деталь: {str(e)}")
        return False
    
    except APIError as e:
        error_str = str(e).lower()
        
        if "insufficient_quota" in error_str or "quota" in error_str:
            print(f"{RED}❌ ОШИБКА КВОТЫ (429){RESET}")
            print(f"   Причины:")
            print(f"   1. На аккаунте закончились деньги")
            print(f"   2. Нет активной подписки")
            print(f"   3. Исчерпана месячная квота")
            print(f"\n   Решение:")
            print(f"   → Перейдите на https://platform.openai.com/account/billing/overview")
            print(f"   → Добавьте платежный метод")
            print(f"   → Пополните баланс (минимум $5)")
            print(f"\n   Деталь: {str(e)}")
            return False
        
        elif "model" in error_str and "not found" in error_str:
            print(f"{RED}❌ МОДЕЛЬ НЕ НАЙДЕНА{RESET}")
            print(f"   Ключ работает, но модель gpt-3.5-turbo недоступна")
            print(f"   Попробуйте другую модель в настройках")
            print(f"\n   Деталь: {str(e)}")
            return False
        
        else:
            print(f"{RED}❌ ОШИБКА API: {type(e).__name__}{RESET}")
            print(f"\n   Деталь: {str(e)}")
            return False
    
    except Exception as e:
        print(f"{RED}❌ НЕИЗВЕСТНАЯ ОШИБКА{RESET}")
        print(f"   Тип: {type(e).__name__}")
        print(f"   Деталь: {str(e)}")
        return False


if __name__ == "__main__":
    # Если передан аргумент - проверить конкретный ключ
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        success = check_openai_key(api_key)
        sys.exit(0 if success else 1)
    else:
        # Иначе запустить полную проверку
        sys.exit(main())
