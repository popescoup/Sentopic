#!/bin/bash

# Sentopic Python Backend Build Script
# Creates standalone Python executable using PyInstaller

set -e  # Exit on any error

echo "🚀 Building Sentopic Python Backend..."
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/sentopic-env"
PYTHON_PATH="$VENV_PATH/bin/python"
BUILD_DIR="$PROJECT_ROOT/dist"
SPEC_FILE="$PROJECT_ROOT/sentopic.spec"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}🐍 Python path: $PYTHON_PATH${NC}"
echo -e "${BLUE}📋 Spec file: $SPEC_FILE${NC}"

# Verify virtual environment
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $PYTHON_PATH${NC}"
    echo -e "${YELLOW}💡 Please ensure your virtual environment is set up correctly${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment found${NC}"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Verify we're in the correct environment
CURRENT_PYTHON=$(which python)
echo -e "${BLUE}🔍 Using Python: $CURRENT_PYTHON${NC}"

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}📦 PyInstaller not found, installing...${NC}"
    pip install pyinstaller
fi

# Check and download sentence-transformer model if needed
echo -e "${BLUE}🤖 Checking sentence-transformer model...${NC}"
MODEL_CACHE="$HOME/.cache/huggingface/hub"
MODEL_NAME="models--sentence-transformers--all-MiniLM-L6-v2"
MODEL_PATH="$MODEL_CACHE/$MODEL_NAME"

if [ ! -d "$MODEL_PATH" ]; then
    echo -e "${YELLOW}📥 Downloading sentence-transformer model (this may take a few minutes)...${NC}"
    python -c "
from sentence_transformers import SentenceTransformer
print('Downloading all-MiniLM-L6-v2 model...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('✅ Model downloaded successfully')
"
    
    if [ ! -d "$MODEL_PATH" ]; then
        echo -e "${RED}❌ Failed to download model${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Model already exists at: $MODEL_PATH${NC}"
fi

# Create frozen requirements for reproducible builds
echo -e "${BLUE}📋 Creating frozen requirements...${NC}"
pip freeze > "$PROJECT_ROOT/requirements-frozen.txt"
echo -e "${GREEN}✅ Created requirements-frozen.txt${NC}"

# Clean previous builds
if [ -d "$BUILD_DIR" ]; then
    echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
    rm -rf "$BUILD_DIR"
fi

if [ -d "$PROJECT_ROOT/build" ]; then
    rm -rf "$PROJECT_ROOT/build"
fi

# Run PyInstaller
echo -e "${BLUE}🔨 Running PyInstaller...${NC}"
echo -e "${YELLOW}⏳ This may take several minutes...${NC}"

cd "$PROJECT_ROOT"
pyinstaller "$SPEC_FILE" --clean --noconfirm

# Verify build success
EXECUTABLE_PATH="$BUILD_DIR/sentopic/sentopic"
if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo -e "${RED}❌ Build failed - executable not found at: $EXECUTABLE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${BLUE}📁 Executable location: $EXECUTABLE_PATH${NC}"

# Test the executable
echo -e "${BLUE}🧪 Testing executable...${NC}"

# Start the server in background
"$EXECUTABLE_PATH" &
SERVER_PID=$!

# Wait for server to start (max 30 seconds)
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server started successfully${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Server failed to start within 30 seconds${NC}"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
done

# Test the health endpoint
if curl -s http://localhost:8000/health | grep -q '"status"'; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# Stop the server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
echo -e "${GREEN}✅ Executable test completed${NC}"

# Show build summary
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo -e "${GREEN}🎉 BUILD COMPLETE${NC}"
echo -e "${BLUE}📁 Executable: $EXECUTABLE_PATH${NC}"
echo -e "${BLUE}📊 Size: $(du -h "$EXECUTABLE_PATH" | cut -f1)${NC}"
echo -e "${BLUE}📋 Frozen requirements: $PROJECT_ROOT/requirements-frozen.txt${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "   1. Test the executable: ${BLUE}$EXECUTABLE_PATH${NC}"
echo -e "   2. The executable will start your FastAPI server"
echo -e "   3. Check http://localhost:8000/health for verification"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="