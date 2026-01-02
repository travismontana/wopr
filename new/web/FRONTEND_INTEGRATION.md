# WOPR Frontend - Games, Pieces, and ML Images CRUD

## New Components

Three new React/TypeScript components for managing the WOPR database:

1. **GamesManager.tsx** - Create, read, update, delete games
2. **PiecesManager.tsx** - Manage pieces and link them to games
3. **MLImagesManager.tsx** - Manage ML training image metadata and link to games/pieces

## Integration Steps

### 1. Place Component Files

Copy the three component files into your pages directory:

```bash
systems/wopr-web/container/src/pages/GamesManager.tsx
systems/wopr-web/container/src/pages/PiecesManager.tsx
systems/wopr-web/container/src/pages/MLImagesManager.tsx
```

### 2. Update app.tsx

Replace your existing `systems/wopr-web/container/src/app.tsx` with the provided version, which includes:

**New imports:**
```typescript
import GamesManager from "./pages/GamesManager";
import PiecesManager from "./pages/PiecesManager";
import MLImagesManager from "./pages/MLImagesManager";
```

**New routes:**
```typescript
<Route path="/games" element={<GamesManager />} />
<Route path="/pieces" element={<PiecesManager />} />
<Route path="/mlimages" element={<MLImagesManager />} />
```

**Updated navigation:**
The nav-grid now includes buttons for Games, Pieces, and ML Images.

### 3. Verify API URL Configuration

The components use this pattern to get the API URL:

```typescript
const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";
```

Make sure your nginx config or runtime config sets `window.ENV.WOPR_API_URL` properly, or update the fallback URL.

### 4. Rebuild and Deploy

```bash
cd systems/wopr-web/container
npm run build

# Then rebuild your Docker image and deploy via ArgoCD
```

## Component Features

### GamesManager

**Features:**
- List all games with pagination
- Create new games
- Edit existing games
- Delete games (with confirmation)
- Filter by locale
- Responsive card grid layout

**Form Fields:**
- Name (required)
- Description
- Min Players
- Max Players
- Locale

### PiecesManager

**Features:**
- List all pieces
- Create new pieces
- Edit existing pieces
- Delete pieces (with confirmation)
- Link pieces to games
- Filter pieces by game
- Responsive card grid layout

**Form Fields:**
- Name (required)
- Description
- Locale

**Linking:**
- Click "Link to Game" button
- Enter Game ID in prompt
- Creates relationship via junction table

### MLImagesManager

**Features:**
- List all ML training image metadata
- Create new ML image entries
- Edit existing entries
- Delete entries (with confirmation)
- Link images to games
- Link images to pieces
- Filter by game and/or piece
- Responsive card grid layout

**Form Fields:**
- Filename (required)
- Object Rotation (0-360 degrees)
- Object Position (e.g., "center", "top-left")
- Color Temperature (e.g., "5500K", "warm")
- Light Intensity (e.g., "bright", "dim")
- Locale

**Linking:**
- Click "→ Game" to link to a game
- Click "→ Piece" to link to a piece
- Enter ID in prompt
- Creates relationships via junction tables

## UI Patterns

All components follow existing WOPR design patterns:

### Styling
- Uses existing `theme.css` classes
- `.panel` for main container
- `.actions` for button groups
- Primary color: `#2222D6` (WOPR blue)
- Dark theme with `#111` backgrounds for cards
- Rounded borders (`border-radius: 8px` for cards, `30px` for main panels)

### Status Messages
Color-coded status messages:
- Green (`#198754`) for success
- Red (`#dc3545`) for errors
- Cyan (`#0dcaf0`) for info

### Forms
- Inline forms that toggle on/off
- Proper labels and validation
- Cancel button to close without saving
- Loading states on all buttons

### Cards
- Responsive grid: `repeat(auto-fill, minmax(300px, 1fr))`
- Shows relevant metadata for each item
- Action buttons for Edit, Delete, Link operations
- ID display for debugging/linking

## API Integration

Components make REST API calls to:

**Games:**
- `GET /api/v1/games` - List all
- `GET /api/v1/games/{id}` - Get one
- `POST /api/v1/games` - Create
- `PUT /api/v1/games/{id}` - Update
- `DELETE /api/v1/games/{id}` - Delete

**Pieces:**
- `GET /api/v1/pieces` - List all
- `GET /api/v1/pieces?game_id={id}` - Filter by game
- `POST /api/v1/pieces` - Create
- `PUT /api/v1/pieces/{id}` - Update
- `DELETE /api/v1/pieces/{id}` - Delete
- `POST /api/v1/pieces/{piece_id}/games/{game_id}` - Link

**ML Images:**
- `GET /api/v1/mlimages` - List all
- `GET /api/v1/mlimages?game_id={id}&piece_id={id}` - Filter
- `POST /api/v1/mlimages` - Create
- `PUT /api/v1/mlimages/{id}` - Update
- `DELETE /api/v1/mlimages/{id}` - Delete
- `POST /api/v1/mlimages/{image_id}/games/{game_id}` - Link to game
- `POST /api/v1/mlimages/{image_id}/pieces/{piece_id}` - Link to piece

## Error Handling

All components include:
- Try/catch blocks around all fetch calls
- HTTP status code checking
- User-friendly error messages
- Loading states to prevent double-clicks
- Confirmation dialogs for destructive operations

## Usage Workflow

### Setup a New Game

1. Navigate to `/games`
2. Click "Add Game"
3. Fill in game details (name required)
4. Click "Create"
5. Note the Game ID from the card

### Add Pieces for a Game

1. Navigate to `/pieces`
2. Click "Add Piece" for each piece type
3. Fill in piece details (name required)
4. Click "Create"
5. For each created piece, click "Link to Game"
6. Enter the Game ID from step 1.5
7. Verify by using the "Filter by Game" dropdown

### Add Training Images

1. Navigate to `/mlimages`
2. Click "Add ML Image"
3. Fill in filename and metadata
4. Click "Create"
5. Click "→ Game" and enter Game ID
6. Click "→ Piece" and enter Piece ID
7. Use filters to verify relationships

## Development Notes

### TypeScript Interfaces

Each component defines proper TypeScript interfaces for:
- API response types
- Form data types
- Status message types

### State Management

Using React hooks:
- `useState` for component state
- `useEffect` for data loading
- Proper cleanup and loading flags

### Responsive Design

All components use CSS Grid with `auto-fill` and `minmax()`:
```css
grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))
```

This automatically adjusts columns based on viewport width.

## Future Enhancements

Potential improvements:

1. **Better Linking UI**
   - Replace prompts with proper modals/dropdowns
   - Show linked games/pieces on cards
   - Add unlink buttons

2. **Bulk Operations**
   - Multi-select for batch delete
   - CSV import/export
   - Batch link operations

3. **Search/Filter**
   - Text search by name/description
   - Advanced filters (date range, etc.)
   - Saved filter presets

4. **Image Preview**
   - Show thumbnails in ML Images cards
   - Lightbox for full-size view
   - Direct image upload

5. **Validation**
   - Client-side validation before submit
   - Field-specific error messages
   - Format hints for structured fields

6. **Pagination**
   - Page controls for large datasets
   - Configurable page size
   - Total count display

## Troubleshooting

### Components not loading
- Check browser console for errors
- Verify API URL is correct
- Check network tab for failed requests

### API calls failing
- Verify wopr-api is running
- Check CORS settings in API
- Verify database connectivity

### Styling looks broken
- Ensure `theme.css` is properly imported
- Check browser console for CSS errors
- Verify class names match theme.css

### Data not refreshing
- Check if loadGames/Pieces/Images is being called
- Verify useEffect dependencies
- Look for console errors during fetch

## Testing Checklist

- [ ] Can create a new game
- [ ] Can edit game details
- [ ] Can delete a game
- [ ] Can create a new piece
- [ ] Can link piece to game
- [ ] Can filter pieces by game
- [ ] Can create ML image metadata
- [ ] Can link ML image to game
- [ ] Can link ML image to piece
- [ ] Can filter ML images by game and piece
- [ ] Status messages display correctly
- [ ] Confirmations work for deletes
- [ ] Forms validate required fields
- [ ] Loading states show during API calls
- [ ] Responsive layout works on mobile
- [ ] Error messages are user-friendly
