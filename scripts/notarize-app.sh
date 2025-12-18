#!/bin/bash

# Sentopic Notarization Script
# Submits the DMG to Apple for notarization and staples the ticket

set -e  # Exit on any error

echo "🔔 Notarizing Sentopic DMG..."
echo "================================================================"

# Configuration
KEYCHAIN_PROFILE="sentopic-notarize"
DMG_PATH="$1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if DMG path was provided
if [ -z "$DMG_PATH" ]; then
    echo -e "${RED}❌ Error: No DMG path provided${NC}"
    echo -e "${YELLOW}Usage: ./notarize-app.sh path/to/your-app.dmg${NC}"
    echo -e "${YELLOW}Example: ./notarize-app.sh electron/dist/Sentopic-1.0.0-arm64.dmg${NC}"
    exit 1
fi

# Check if DMG exists
if [ ! -f "$DMG_PATH" ]; then
    echo -e "${RED}❌ Error: DMG not found at: $DMG_PATH${NC}"
    exit 1
fi

echo -e "${BLUE}📦 DMG: $DMG_PATH${NC}"
echo -e "${BLUE}🔑 Keychain Profile: $KEYCHAIN_PROFILE${NC}"
echo ""

# Step 1: Submit for notarization
echo -e "${YELLOW}Step 1: Submitting to Apple for notarization...${NC}"
echo -e "${BLUE}⏳ This will take 2-15 minutes (usually ~5 minutes)${NC}"
echo ""

SUBMIT_OUTPUT=$(xcrun notarytool submit "$DMG_PATH" \
    --keychain-profile "$KEYCHAIN_PROFILE" \
    --wait 2>&1)

echo "$SUBMIT_OUTPUT"

# Check if submission was successful
if echo "$SUBMIT_OUTPUT" | grep -q "status: Accepted"; then
    echo ""
    echo -e "${GREEN}✅ Notarization successful!${NC}"
    
    # Step 2: Staple the notarization ticket
    echo ""
    echo -e "${YELLOW}Step 2: Stapling notarization ticket to DMG...${NC}"
    
    xcrun stapler staple "$DMG_PATH"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Ticket stapled successfully!${NC}"
        
        # Step 3: Verify
        echo ""
        echo -e "${YELLOW}Step 3: Verifying notarization...${NC}"
        
        xcrun stapler validate "$DMG_PATH"
        
        echo ""
        echo "================================================================"
        echo -e "${GREEN}🎉 NOTARIZATION COMPLETE!${NC}"
        echo ""
        echo -e "${BLUE}Your DMG is now fully signed and notarized.${NC}"
        echo -e "${BLUE}Users can download and open it without any warnings.${NC}"
        echo ""
        echo -e "${BLUE}📦 Notarized DMG: $DMG_PATH${NC}"
        echo "================================================================"
        
    else
        echo -e "${RED}❌ Failed to staple ticket${NC}"
        exit 1
    fi
    
elif echo "$SUBMIT_OUTPUT" | grep -q "status: Invalid"; then
    echo ""
    echo -e "${RED}❌ Notarization failed: Invalid${NC}"
    echo -e "${YELLOW}This usually means there's an issue with the app signature or entitlements.${NC}"
    echo ""
    echo "Common issues:"
    echo "  - App not properly signed"
    echo "  - Missing or incorrect entitlements"
    echo "  - Hardened runtime not enabled"
    echo ""
    echo "To see detailed error information, run:"
    echo -e "${BLUE}  xcrun notarytool log <submission-id> --keychain-profile $KEYCHAIN_PROFILE${NC}"
    echo ""
    exit 1
    
elif echo "$SUBMIT_OUTPUT" | grep -q "status: Rejected"; then
    echo ""
    echo -e "${RED}❌ Notarization rejected${NC}"
    echo -e "${YELLOW}Apple's automated scan found an issue with your app.${NC}"
    echo ""
    
    # Try to extract submission ID for detailed logs
    SUBMISSION_ID=$(echo "$SUBMIT_OUTPUT" | grep "id:" | head -1 | awk '{print $2}')
    
    if [ -n "$SUBMISSION_ID" ]; then
        echo "To see detailed rejection reasons, run:"
        echo -e "${BLUE}  xcrun notarytool log $SUBMISSION_ID --keychain-profile $KEYCHAIN_PROFILE${NC}"
    fi
    echo ""
    exit 1
    
else
    echo ""
    echo -e "${RED}❌ Notarization failed with unknown status${NC}"
    echo "Output:"
    echo "$SUBMIT_OUTPUT"
    exit 1
fi