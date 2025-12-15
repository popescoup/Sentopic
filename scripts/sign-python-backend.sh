#!/bin/bash

# Sentopic Python Backend Code Signing Script
# Signs all components of the PyInstaller bundle for macOS distribution

set -e  # Exit on any error

echo "🔐 Signing Sentopic Python Backend..."
echo "================================================================"

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist/sentopic"
INTERNAL_DIR="$DIST_DIR/_internal"
EXECUTABLE="$DIST_DIR/sentopic"

# Signing configuration
SIGNING_IDENTITY="Developer ID Application: Luca Popescu (2Y4LYRR4PT)"
ENTITLEMENTS="$PROJECT_ROOT/electron/build-resources/entitlements.mac.plist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 Distribution directory: $DIST_DIR${NC}"
echo -e "${BLUE}🔑 Signing identity: $SIGNING_IDENTITY${NC}"
echo -e "${BLUE}📋 Entitlements: $ENTITLEMENTS${NC}"

# Verify distribution directory exists
if [ ! -d "$DIST_DIR" ]; then
    echo -e "${RED}❌ Distribution directory not found: $DIST_DIR${NC}"
    echo -e "${YELLOW}💡 Please build the Python backend first${NC}"
    exit 1
fi

# Verify entitlements file exists
if [ ! -f "$ENTITLEMENTS" ]; then
    echo -e "${RED}❌ Entitlements file not found: $ENTITLEMENTS${NC}"
    exit 1
fi

# Verify signing identity is available
if ! security find-identity -v -p codesigning | grep -q "$SIGNING_IDENTITY"; then
    echo -e "${RED}❌ Signing identity not found in keychain${NC}"
    echo -e "${YELLOW}💡 Available identities:${NC}"
    security find-identity -v -p codesigning
    exit 1
fi

echo -e "${GREEN}✅ Pre-flight checks passed${NC}"
echo ""

# Function to sign a file
sign_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo -e "${BLUE}  Signing: $filename${NC}"
    
    codesign \
        --sign "$SIGNING_IDENTITY" \
        --force \
        --timestamp \
        --options runtime \
        --entitlements "$ENTITLEMENTS" \
        "$file" 2>&1 | grep -v "replacing existing signature" || true
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}    ✅ Signed successfully${NC}"
        return 0
    else
        echo -e "${RED}    ❌ Failed to sign${NC}"
        return 1
    fi
}

# Step 1: Sign all .dylib files in _internal directory
echo -e "${YELLOW}📦 Step 1: Signing dynamic libraries (.dylib files)...${NC}"

if [ -d "$INTERNAL_DIR" ]; then
    DYLIB_COUNT=0
    SIGNED_COUNT=0
    
    # Find all .dylib files
    while IFS= read -r -d '' dylib; do
        ((DYLIB_COUNT++))
        if sign_file "$dylib"; then
            ((SIGNED_COUNT++))
        fi
    done < <(find "$INTERNAL_DIR" -name "*.dylib" -print0)
    
    echo -e "${GREEN}✅ Signed $SIGNED_COUNT of $DYLIB_COUNT .dylib files${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  No _internal directory found, skipping .dylib signing${NC}"
    echo ""
fi

# Step 2: Sign all .so files (Python extension modules)
echo -e "${YELLOW}📦 Step 2: Signing Python extension modules (.so files)...${NC}"

if [ -d "$INTERNAL_DIR" ]; then
    SO_COUNT=0
    SIGNED_COUNT=0
    
    # Find all .so files
    while IFS= read -r -d '' so_file; do
        ((SO_COUNT++))
        if sign_file "$so_file"; then
            ((SIGNED_COUNT++))
        fi
    done < <(find "$INTERNAL_DIR" -name "*.so" -print0)
    
    echo -e "${GREEN}✅ Signed $SIGNED_COUNT of $SO_COUNT .so files${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  No _internal directory found, skipping .so signing${NC}"
    echo ""
fi

# Step 3: Sign nested frameworks (if any)
echo -e "${YELLOW}📦 Step 3: Signing frameworks...${NC}"

if [ -d "$INTERNAL_DIR" ]; then
    FRAMEWORK_COUNT=0
    SIGNED_COUNT=0
    
    # Find all .framework bundles
    while IFS= read -r -d '' framework; do
        ((FRAMEWORK_COUNT++))
        if sign_file "$framework"; then
            ((SIGNED_COUNT++))
        fi
    done < <(find "$INTERNAL_DIR" -name "*.framework" -type d -print0)
    
    if [ $FRAMEWORK_COUNT -eq 0 ]; then
        echo -e "${BLUE}  No frameworks found${NC}"
    else
        echo -e "${GREEN}✅ Signed $SIGNED_COUNT of $FRAMEWORK_COUNT frameworks${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  No _internal directory found, skipping framework signing${NC}"
    echo ""
fi

# Step 4: Sign the main Python executable
echo -e "${YELLOW}🐍 Step 4: Signing main executable...${NC}"

if [ -f "$EXECUTABLE" ]; then
    if sign_file "$EXECUTABLE"; then
        echo -e "${GREEN}✅ Main executable signed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to sign main executable${NC}"
        exit 1
    fi
    echo ""
else
    echo -e "${RED}❌ Main executable not found: $EXECUTABLE${NC}"
    exit 1
fi

# Step 5: Verify signatures
echo -e "${YELLOW}🔍 Step 5: Verifying signatures...${NC}"

# Verify main executable
echo -e "${BLUE}  Verifying main executable...${NC}"
if codesign --verify --deep --strict --verbose=2 "$EXECUTABLE" 2>&1; then
    echo -e "${GREEN}  ✅ Main executable signature valid${NC}"
else
    echo -e "${RED}  ❌ Main executable signature verification failed${NC}"
    exit 1
fi

# Check signature details
echo ""
echo -e "${BLUE}📋 Signature details:${NC}"
codesign --display --verbose=4 "$EXECUTABLE" 2>&1 | grep -E "(Identifier|Authority|TeamIdentifier|Signature|Runtime)" | sed 's/^/  /'

echo ""
echo "================================================================"
echo -e "${GREEN}🎉 Python backend signing completed successfully!${NC}"
echo -e "${BLUE}📁 Signed bundle: $DIST_DIR${NC}"
echo "================================================================"