#!/bin/bash

# Sentopic Icon Creation Script
# Creates app icons in all required formats from SVG source

set -e

echo "🎨 Creating Sentopic App Icons..."
echo "=================================="

# Check if we're in the electron directory
if [ ! -d "build-resources" ]; then
    echo "❌ Error: build-resources directory not found"
    echo "Please run this script from the electron/ directory"
    exit 1
fi

# Create the base SVG icon file
cat > build-resources/icon.svg << 'EOF'
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <!-- Dark grey background with rounded corners -->
  <rect width="1024" height="1024" fill="#2a2a2a" rx="128" ry="128"/>
  
  <!-- ASCII-style "S" based on your logo -->
  <!-- Top horizontal line -->
  <rect x="200" y="250" width="624" height="80" fill="#f0f0f0"/>
  
  <!-- Top vertical line (left side) -->
  <rect x="200" y="250" width="80" height="200" fill="#f0f0f0"/>
  
  <!-- Middle horizontal line -->
  <rect x="200" y="450" width="544" height="80" fill="#f0f0f0"/>
  
  <!-- Bottom vertical line (right side) -->
  <rect x="744" y="450" width="80" height="200" fill="#f0f0f0"/>
  
  <!-- Bottom horizontal line -->
  <rect x="200" y="650" width="624" height="80" fill="#f0f0f0"/>
  
  <!-- Top left corner block -->
  <rect x="200" y="330" width="80" height="40" fill="#2a2a2a"/>
  
  <!-- Bottom right corner adjustment -->
  <rect x="744" y="610" width="80" height="40" fill="#2a2a2a"/>
</svg>
EOF

echo "✅ Created base SVG icon"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
MISSING_TOOLS=""

if ! command_exists convert; then
    MISSING_TOOLS="$MISSING_TOOLS imagemagick"
fi

if ! command_exists sips; then
    echo "⚠️  sips not found (macOS only tool)"
fi

if [ ! -z "$MISSING_TOOLS" ]; then
    echo "❌ Missing required tools:$MISSING_TOOLS"
    echo ""
    echo "To install missing tools:"
    echo "  brew install imagemagick"
    echo ""
    echo "Or manually create icons using the SVG file at: build-resources/icon.svg"
    exit 1
fi

echo "✅ Required tools found"

# Create PNG files for various sizes
echo "🖼️  Creating PNG files..."

SIZES=(16 32 64 128 256 512 1024)

for size in "${SIZES[@]}"; do
    echo "  Creating ${size}x${size} PNG..."
    convert build-resources/icon.svg -resize ${size}x${size} build-resources/icon-${size}.png
done

# Create high-resolution PNG for Linux
cp build-resources/icon-512.png build-resources/icon.png

echo "✅ Created PNG files"

# Create Windows ICO file (if on macOS or with ImageMagick)
echo "🪟 Creating Windows ICO file..."
convert build-resources/icon-256.png build-resources/icon-128.png build-resources/icon-64.png build-resources/icon-32.png build-resources/icon-16.png build-resources/icon.ico

echo "✅ Created Windows ICO file"

# Create macOS ICNS file (macOS only)
if command_exists sips && command_exists iconutil; then
    echo "🍎 Creating macOS ICNS file..."
    
    # Create iconset directory
    mkdir -p build-resources/icon.iconset
    
    # Copy and rename files for iconset
    cp build-resources/icon-16.png build-resources/icon.iconset/icon_16x16.png
    cp build-resources/icon-32.png build-resources/icon.iconset/icon_16x16@2x.png
    cp build-resources/icon-32.png build-resources/icon.iconset/icon_32x32.png
    cp build-resources/icon-64.png build-resources/icon.iconset/icon_32x32@2x.png
    cp build-resources/icon-128.png build-resources/icon.iconset/icon_128x128.png
    cp build-resources/icon-256.png build-resources/icon.iconset/icon_128x128@2x.png
    cp build-resources/icon-256.png build-resources/icon.iconset/icon_256x256.png
    cp build-resources/icon-512.png build-resources/icon.iconset/icon_256x256@2x.png
    cp build-resources/icon-512.png build-resources/icon.iconset/icon_512x512.png
    cp build-resources/icon-1024.png build-resources/icon.iconset/icon_512x512@2x.png
    
    # Convert to ICNS
    iconutil -c icns build-resources/icon.iconset
    
    # Clean up iconset directory
    rm -rf build-resources/icon.iconset
    
    echo "✅ Created macOS ICNS file"
else
    echo "⚠️  Skipping ICNS creation (macOS tools not available)"
    echo "   You can create it manually later or on macOS"
fi

# Create basic entitlements file for macOS
cat > build-resources/entitlements.mac.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Created macOS entitlements file"

# Clean up individual PNG files (optional)
# rm build-resources/icon-*.png

echo ""
echo "🎉 Icon creation complete!"
echo "=================================="
echo "Created files:"
echo "  📁 build-resources/icon.svg     - Source SVG file"
echo "  🖼️  build-resources/icon.png     - Linux PNG (512x512)"
echo "  🪟 build-resources/icon.ico     - Windows ICO (multi-size)"
if [ -f "build-resources/icon.icns" ]; then
    echo "  🍎 build-resources/icon.icns    - macOS ICNS (multi-size)"
else
    echo "  ⚠️  build-resources/icon.icns    - Not created (macOS tools required)"
fi
echo "  📄 build-resources/entitlements.mac.plist - macOS entitlements"
echo ""
echo "Next steps:"
echo "1. Your package.json is already configured to use these icons"
echo "2. Ready to proceed with Step 2b (updating main.js)"
echo "3. Test icon appearance: npm run pack"