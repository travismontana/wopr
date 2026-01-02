# WOPR generouted Migration

This tarball contains the new file structure for migrating WOPR to use generouted for automatic file-based routing.

## What Changed

### 1. Dependencies
Add to your `package.json`:
```bash
npm install @generouted/react-router
```

### 2. File Structure
```
src/
├── main.tsx              ← Simplified (see new file)
├── pages/                ← NEW: Replaces routes/
│   ├── _app.tsx          ← Root layout (was app.tsx)
│   ├── index.tsx         ← Home page
│   ├── play/
│   │   ├── index.tsx     ← /play
│   │   └── new.tsx       ← /play/new
│   └── boh/
│       ├── _layout.tsx   ← BOH wrapper (was routes/boh/index.tsx)
│       ├── index.tsx     ← /boh landing
│       ├── games.tsx     ← /boh/games
│       ├── pieces.tsx    ← /boh/pieces
│       ├── mlimages.tsx  ← /boh/mlimages
│       ├── status.tsx    ← /boh/status
│       ├── cameras/
│       │   ├── _layout.tsx  ← Camera nav wrapper
│       │   ├── index.tsx    ← /boh/cameras
│       │   ├── capture.tsx  ← /boh/cameras/capture
│       │   ├── config.tsx   ← /boh/cameras/config
│       │   └── status.tsx   ← /boh/cameras/status
│       ├── images/
│       │   ├── _layout.tsx  ← Images nav wrapper (if needed)
│       │   ├── index.tsx    ← /boh/images
│       │   ├── view.tsx     ← /boh/images/view
│       │   ├── gallery.tsx  ← /boh/images/gallery
│       │   ├── edit.tsx     ← /boh/images/edit
│       │   └── other.tsx    ← /boh/images/other
│       └── config/
│           ├── _layout.tsx  ← Config nav wrapper (if needed)
│           ├── index.tsx    ← /boh/config
│           └── control.tsx  ← /boh/config/control
├── components/           ← NEW: Shared components like WIP
│   └── wip.tsx
└── lib/                  ← Keep as-is
    └── api.ts
```

### 3. Migration Steps

#### A. Install generouted
```bash
npm install @generouted/react-router
```

#### B. Update vite.config.ts
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import generouted from '@generouted/react-router/plugin';  // ADD THIS
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    generouted()  // ADD THIS
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@lib': path.resolve(__dirname, './src/lib'),
      '@components': path.resolve(__dirname, './src/components'),  // UPDATE THIS
      '@routes': path.resolve(__dirname, './src/routes'),  // Can remove after migration
    },
  },
  server: {
    port: 5173
  },
  base: '/',
});
```

#### C. File Mapping

For most files, you can copy them directly from `routes/` to `pages/`:

```bash
# In your wopr-web/container/src/ directory

# 1. Copy your existing routes to pages
cp -r routes pages

# 2. Rename specific files following generouted conventions:

# Layout wrappers (components with <Outlet /> that wrap nested routes)
mv pages/boh/index.tsx pages/boh/_layout.tsx
mv pages/boh/cameras/index.tsx pages/boh/cameras/_layout.tsx
mv pages/boh/config/index.tsx pages/boh/config/_layout.tsx
mv pages/boh/images/index.tsx pages/boh/images/_layout.tsx  # If it's a layout

# 3. Flatten nested index files (if they're actual content pages)
# Example: routes/boh/games/index.tsx → pages/boh/games.tsx
mv pages/boh/games/index.tsx pages/boh/games.tsx
mv pages/boh/pieces/index.tsx pages/boh/pieces.tsx
mv pages/boh/mlimages/index.tsx pages/boh/mlimages.tsx
mv pages/boh/status/index.tsx pages/boh/status.tsx

# 4. Rename play pages
mv pages/play/new-game.tsx pages/play/new.tsx

# 5. Handle special pages
mv pages/home/dashboard.tsx pages/index.tsx  # Home page
mv routes/wip.tsx components/wip.tsx  # Shared component

# 6. Update any imports in pages/ from './routes/' to './pages/' or '@/'
```

#### D. Handle Props Issue

Your current setup passes props like:
```typescript
<ImageGallery gameId="dune_imperium_uprising" />
```

With generouted, you have three options:

**Option 1: URL Params** (Recommended)
```
pages/boh/images/gallery/[gameId].tsx  → /boh/images/gallery/:gameId

// In component:
import { useParams } from 'react-router-dom';
const { gameId } = useParams();
```

**Option 2: Query Params**
```
/boh/images/gallery?gameId=dune_imperium_uprising

// In component:
import { useSearchParams } from 'react-router-dom';
const [searchParams] = useSearchParams();
const gameId = searchParams.get('gameId');
```

**Option 3: Hardcode**
Just set the default in the component itself.

#### E. Update main.tsx

Replace your entire main.tsx with:
```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { Routes } from "@generouted/react-router";
import "./themes/modern.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Routes />
  </React.StrictMode>
);
```

#### F. Create _app.tsx

Move your current `app.tsx` to `pages/_app.tsx`:
```bash
mv src/app.tsx src/pages/_app.tsx
```

### 4. Testing

After migration:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install`
3. Run `npm run dev`
4. Check console for any routing errors
5. Test each route manually

### 5. What Gets Easier

**Before (manual):**
```typescript
// 1. Create file: routes/boh/newpage.tsx
// 2. Import in main.tsx
import NewPage from "./routes/boh/newpage";
// 3. Add to route config
{ path: "newpage", element: <NewPage /> }
```

**After (automatic):**
```typescript
// 1. Create file: pages/boh/newpage.tsx
// Done. Route is automatically /boh/newpage
```

## Files Included

This tarball includes:
- `src/main.tsx` - New simplified version
- `src/pages/_app.tsx` - Root layout
- `src/pages/index.tsx` - Home page
- `src/pages/play/` - Play section structure
- `src/pages/boh/_layout.tsx` - BOH layout wrapper
- `src/components/wip.tsx` - Work in Progress component
- `vite.config.ts.example` - Updated config (rename to vite.config.ts)
- This README

## Notes

- Layout files use `_layout.tsx` naming convention
- Index routes use `index.tsx` naming convention  
- Dynamic segments use `[param].tsx` naming convention
- 404 page would be `404.tsx` in pages root
- Keep your existing `lib/`, `themes/`, etc. directories

## Rollback Plan

If something breaks:
1. Keep your old `routes/` directory intact
2. Keep your old `main.tsx` as `main.tsx.backup`
3. Can revert by removing generouted and restoring old main.tsx

## Questions?

Check generouted docs: https://github.com/oedotme/generouted
