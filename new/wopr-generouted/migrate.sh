#!/bin/bash
# WOPR generouted Migration Script
# Run this from your wopr-web/container/ directory

set -e

echo "========================================="
echo "WOPR generouted Migration"
echo "========================================="
echo ""
echo "This script will:"
echo "1. Copy routes/ to pages/"
echo "2. Rename layout files to _layout.tsx"
echo "3. Flatten single-file directories"
echo "4. Move shared components"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled."
    exit 1
fi

cd src

echo "Step 1: Copying routes/ to pages/..."
cp -r routes pages

echo "Step 2: Renaming layout files..."
# BOH main layout
if [ -f pages/boh/index.tsx ]; then
    mv pages/boh/index.tsx pages/boh/_layout.tsx
    echo "  ✓ pages/boh/_layout.tsx"
fi

# Camera layout
if [ -f pages/boh/cameras/index.tsx ]; then
    mv pages/boh/cameras/index.tsx pages/boh/cameras/_layout.tsx
    echo "  ✓ pages/boh/cameras/_layout.tsx"
fi

# Config layout
if [ -f pages/boh/config/index.tsx ]; then
    mv pages/boh/config/index.tsx pages/boh/config/_layout.tsx
    echo "  ✓ pages/boh/config/_layout.tsx"
fi

# Images layout (if it's actually a layout)
# Check manually if this has <Outlet /> before uncommenting
# if [ -f pages/boh/images/index.tsx ]; then
#     mv pages/boh/images/index.tsx pages/boh/images/_layout.tsx
#     echo "  ✓ pages/boh/images/_layout.tsx"
# fi

echo "Step 3: Flattening single-file directories..."
# Games
if [ -f pages/boh/games/index.tsx ]; then
    mv pages/boh/games/index.tsx pages/boh/games.tsx
    rmdir pages/boh/games 2>/dev/null || true
    echo "  ✓ pages/boh/games.tsx"
fi

# Pieces
if [ -f pages/boh/pieces/index.tsx ]; then
    mv pages/boh/pieces/index.tsx pages/boh/pieces.tsx
    rmdir pages/boh/pieces 2>/dev/null || true
    echo "  ✓ pages/boh/pieces.tsx"
fi

# ML Images
if [ -f pages/boh/mlimages/index.tsx ]; then
    mv pages/boh/mlimages/index.tsx pages/boh/mlimages.tsx
    rmdir pages/boh/mlimages 2>/dev/null || true
    echo "  ✓ pages/boh/mlimages.tsx"
fi

# Status
if [ -f pages/boh/status/index.tsx ]; then
    mv pages/boh/status/index.tsx pages/boh/status.tsx
    rmdir pages/boh/status 2>/dev/null || true
    echo "  ✓ pages/boh/status.tsx"
fi

# ML
if [ -f pages/boh/ml/index.tsx ]; then
    mv pages/boh/ml/index.tsx pages/boh/ml.tsx
    rmdir pages/boh/ml 2>/dev/null || true
    echo "  ✓ pages/boh/ml.tsx"
fi

echo "Step 4: Renaming play pages..."
if [ -f pages/play/new-game.tsx ]; then
    mv pages/play/new-game.tsx pages/play/new.tsx
    echo "  ✓ pages/play/new.tsx"
fi

echo "Step 5: Moving home page..."
if [ -f pages/home/dashboard.tsx ]; then
    mv pages/home/dashboard.tsx pages/index.tsx
    rmdir pages/home 2>/dev/null || true
    echo "  ✓ pages/index.tsx"
fi

echo "Step 6: Moving shared components..."
mkdir -p components
if [ -f pages/wip.tsx ]; then
    mv pages/wip.tsx components/wip.tsx
    echo "  ✓ components/wip.tsx"
fi

echo "Step 7: Moving root layout..."
if [ -f app.tsx ]; then
    mv app.tsx pages/_app.tsx
    echo "  ✓ pages/_app.tsx"
fi

echo ""
echo "========================================="
echo "Migration Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Update vite.config.ts (see vite.config.ts.example)"
echo "2. Update main.tsx (see src/main.tsx in tarball)"
echo "3. Install generouted: npm install @generouted/react-router"
echo "4. Fix any import paths in pages/ that reference ./routes/"
echo "5. Test: npm run dev"
echo ""
echo "NOTE: Your old routes/ directory is still intact."
echo "      You can delete it after verifying everything works."
