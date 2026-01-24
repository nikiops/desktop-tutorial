# SYSTEM VERIFICATION SCRIPT - ПРОВЕРКА ВСЕХ СИСТЕМ
# Для Windows PowerShell

Write-Host ""
Write-Host "🔍 OZON REVIEW SERVICE - СИСТЕМА ПРОВЕРКИ" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Счётчики
$PASSED = 0
$FAILED = 0
$WARNINGS = 0

# Функция для вывода результата
function Check-System {
    param(
        [string]$TestName,
        [bool]$Result,
        [string]$Message = ""
    )
    
    if ($Result) {
        Write-Host "✅ $TestName" -ForegroundColor Green
        $global:PASSED++
    } else {
        if ($Message -like "WARNING*") {
            Write-Host "⚠️  $TestName - $Message" -ForegroundColor Yellow
            $global:WARNINGS++
        } else {
            Write-Host "❌ $TestName" -ForegroundColor Red
            $global:FAILED++
        }
    }
}

# 1. ПРОВЕРКА PYTHON ОКРУЖЕНИЯ
Write-Host "1️⃣  ПРОВЕРКА PYTHON ОКРУЖЕНИЯ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
$pythonExists = (python --version 2>$null) -ne $null
Check-System "Python установлен" $pythonExists

# Проверка pip
$pipExists = (pip --version 2>$null) -ne $null
Check-System "pip установлен" $pipExists

Write-Host ""
Write-Host "2️⃣  ПРОВЕРКА ЗАВИСИМОСТЕЙ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка requirements.txt
$reqExists = Test-Path "requirements.txt"
Check-System "requirements.txt существует" $reqExists

# Проверка основных пакетов
$fastapi = python -c "import fastapi" 2>$null
Check-System "FastAPI установлен" ($LASTEXITCODE -eq 0)

$sqlalchemy = python -c "import sqlalchemy" 2>$null
Check-System "SQLAlchemy установлен" ($LASTEXITCODE -eq 0)

$openai = python -c "import openai" 2>$null
Check-System "OpenAI клиент установлен" ($LASTEXITCODE -eq 0)

$httpx = python -c "import httpx" 2>$null
Check-System "httpx установлен" ($LASTEXITCODE -eq 0)

Write-Host ""
Write-Host "3️⃣  ПРОВЕРКА КОНФИГУРАЦИИ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка .env файла
$envExists = Test-Path ".env"
Check-System ".env файл существует" $envExists

if ($envExists) {
    $envContent = Get-Content ".env" -Raw
    
    if ($envContent -like "*OZON_CLIENT_ID*") {
        Check-System "OZON_CLIENT_ID переменная задана" $true
    } else {
        Check-System "OZON_CLIENT_ID не заполнена" $false "WARNING"
    }
    
    if ($envContent -like "*OPENAI_API_KEY*") {
        Check-System "OPENAI_API_KEY переменная задана" $true
    } else {
        Check-System "OPENAI_API_KEY не заполнена" $false "WARNING"
    }
}

Write-Host ""
Write-Host "4️⃣  ПРОВЕРКА ФАЙЛОВОЙ СТРУКТУРЫ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка основных файлов
Check-System "main.py существует" (Test-Path "main.py")
Check-System "app/ директория существует" (Test-Path "app" -PathType Container)
Check-System "app/database.py существует" (Test-Path "app/database.py")
Check-System "app/config.py существует" (Test-Path "app/config.py")
Check-System "app/services/ директория существует" (Test-Path "app/services" -PathType Container)
Check-System "app/api/ директория существует" (Test-Path "app/api" -PathType Container)
Check-System "app/models/ директория существует" (Test-Path "app/models" -PathType Container)
Check-System "frontend/index.html существует" (Test-Path "frontend/index.html")
Check-System "Dockerfile существует" (Test-Path "Dockerfile")
Check-System "docker-compose.yml существует" (Test-Path "docker-compose.yml")

Write-Host ""
Write-Host "5️⃣  ПРОВЕРКА API ENDPOINTS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Проверка health endpoint
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/status" -ErrorAction SilentlyContinue
    if ($response.Content -like "*healthy*") {
        Check-System "GET /api/health/status" $true
    } else {
        Check-System "GET /api/health/status" $false
    }
    
    # Проверка integrations endpoint
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/integrations" -ErrorAction SilentlyContinue
    if ($response.Content -like "*ozon_api*") {
        Check-System "GET /api/health/integrations" $true
    } else {
        Check-System "GET /api/health/integrations" $false
    }
} catch {
    Check-System "API endpoints доступны" $false "WARNING: Cannot connect to server on localhost:8000"
}

Write-Host ""
Write-Host "6️⃣  ПРОВЕРКА ДОКУМЕНТАЦИИ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Check-System "README.md существует" (Test-Path "README.md")
Check-System "SETUP_GUIDE.md существует" (Test-Path "SETUP_GUIDE.md")
Check-System "VERIFICATION_CHECKLIST.md существует" (Test-Path "VERIFICATION_CHECKLIST.md")
Check-System "PROJECT_OVERVIEW.md существует" (Test-Path "PROJECT_OVERVIEW.md")
Check-System "QUICK_REFERENCE.md существует" (Test-Path "QUICK_REFERENCE.md")
Check-System "DEVELOPMENT.md существует" (Test-Path "DEVELOPMENT.md")

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "✅ Пройдено:      $PASSED" -ForegroundColor Green
Write-Host "⚠️  Предупреждения: $WARNINGS" -ForegroundColor Yellow
Write-Host "❌ Ошибок:        $FAILED" -ForegroundColor Red

Write-Host ""

if ($FAILED -eq 0) {
    Write-Host "🎉 ВСЕ СИСТЕМЫ ГОТОВЫ!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Следующие шаги:"
    Write-Host "1. Заполните .env файл с вашими API ключами:"
    Write-Host "   - OZON_CLIENT_ID"
    Write-Host "   - OZON_API_KEY"
    Write-Host "   - OPENAI_API_KEY"
    Write-Host ""
    Write-Host "2. Запустите сервер: python main.py"
    Write-Host ""
    Write-Host "3. Откройте админ-панель: http://localhost:8000"
    Write-Host ""
    Write-Host "4. Нажмите на статус-индикаторы для тестирования подключений"
    Write-Host ""
} else {
    Write-Host "⚠️  НАЙДЕНЫ ПРОБЛЕМЫ!" -ForegroundColor Red
    Write-Host "Пожалуйста, исправьте ошибки перед использованием."
}

exit $FAILED
