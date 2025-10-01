@echo off
REM Sentopic Python Backend Build Script for Windows
REM Creates standalone Python executable using PyInstaller

setlocal enabledelayedexpansion

echo 🚀 Building Sentopic Python Backend...
echo ================================================================================

REM Configuration
set "PROJECT_ROOT=%~dp0.."
set "VENV_PATH=%PROJECT_ROOT%\sentopic-env"
set "PYTHON_PATH=%VENV_PATH%\Scripts\python.exe"
set "BUILD_DIR=%PROJECT_ROOT%\dist"
set "SPEC_FILE=%PROJECT_ROOT%\sentopic.spec"

echo 📁 Project root: %PROJECT_ROOT%
echo 🐍 Python path: %PYTHON_PATH%
echo 📋 Spec file: %SPEC_FILE%

REM Verify virtual environment
if not exist "%PYTHON_PATH%" (
    echo ❌ Virtual environment not found at: %PYTHON_PATH%
    echo 💡 Please ensure your virtual environment is set up correctly
    echo    Expected Python at: %PYTHON_PATH%
    pause
    exit /b 1
)

echo ✅ Virtual environment found

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Verify we're in the correct environment
for /f %%i in ('where python') do set "CURRENT_PYTHON=%%i"
echo 🔍 Using Python: %CURRENT_PYTHON%

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 📦 PyInstaller not found, installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check and download sentence-transformer model if needed
echo 🤖 Checking sentence-transformer model...
set "MODEL_CACHE=%USERPROFILE%\.cache\huggingface\hub"
set "MODEL_NAME=models--sentence-transformers--all-MiniLM-L6-v2"
set "MODEL_PATH=%MODEL_CACHE%\%MODEL_NAME%"

if not exist "%MODEL_PATH%" (
    echo 📥 Downloading sentence-transformer model (this may take a few minutes)...
    python -c "from sentence_transformers import SentenceTransformer; print('Downloading all-MiniLM-L6-v2 model...'); model = SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Model downloaded successfully')"
    
    if not exist "%MODEL_PATH%" (
        echo ❌ Failed to download model
        pause
        exit /b 1
    )
) else (
    echo ✅ Model already exists at: %MODEL_PATH%
)

REM Create frozen requirements for reproducible builds
echo 📋 Creating frozen requirements...
pip freeze > "%PROJECT_ROOT%\requirements-frozen.txt"
echo ✅ Created requirements-frozen.txt

REM Clean previous builds
if exist "%BUILD_DIR%" (
    echo 🧹 Cleaning previous build...
    rmdir /s /q "%BUILD_DIR%"
)

if exist "%PROJECT_ROOT%\build" (
    rmdir /s /q "%PROJECT_ROOT%\build"
)

REM Run PyInstaller
echo 🔨 Running PyInstaller...
echo ⏳ This may take several minutes...

cd /d "%PROJECT_ROOT%"
pyinstaller "%SPEC_FILE%" --clean --noconfirm

if errorlevel 1 (
    echo ❌ PyInstaller build failed
    pause
    exit /b 1
)

REM Verify build success
set "EXECUTABLE_PATH=%BUILD_DIR%\sentopic\sentopic.exe"
if not exist "%EXECUTABLE_PATH%" (
    echo ❌ Build failed - executable not found at: %EXECUTABLE_PATH%
    pause
    exit /b 1
)

echo ✅ Build completed successfully!
echo 📁 Executable location: %EXECUTABLE_PATH%

REM Test the executable
echo 🧪 Testing executable...

REM Start the server in background
start /b "" "%EXECUTABLE_PATH%"

REM Wait for server to start (max 30 seconds)
echo ⏳ Waiting for server to start...
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak > nul
    curl -s http://localhost:8000/health > nul 2>&1
    if not errorlevel 1 (
        echo ✅ Server started successfully
        goto :server_started
    )
    if %%i==30 (
        echo ❌ Server failed to start within 30 seconds
        taskkill /f /im sentopic.exe > nul 2>&1
        pause
        exit /b 1
    )
)

:server_started
REM Test the health endpoint
curl -s http://localhost:8000/health | findstr "status" > nul
if not errorlevel 1 (
    echo ✅ Health check passed
) else (
    echo ❌ Health check failed
    taskkill /f /im sentopic.exe > nul 2>&1
    pause
    exit /b 1
)

REM Stop the server
taskkill /f /im sentopic.exe > nul 2>&1
echo ✅ Executable test completed

REM Show build summary
echo ================================================================================
echo 🎉 BUILD COMPLETE
echo 📁 Executable: %EXECUTABLE_PATH%

REM Get file size
for %%A in ("%EXECUTABLE_PATH%") do set "FILE_SIZE=%%~zA"
set /a "SIZE_MB=!FILE_SIZE!/1024/1024"
echo 📊 Size: !SIZE_MB! MB

echo 📋 Frozen requirements: %PROJECT_ROOT%\requirements-frozen.txt
echo.
echo 📝 Next steps:
echo    1. Test the executable: %EXECUTABLE_PATH%
echo    2. The executable will start your FastAPI server
echo    3. Check http://localhost:8000/health for verification
echo ================================================================================

pause