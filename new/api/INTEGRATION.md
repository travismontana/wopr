# WOPR API - Games, Pieces, and ML Images CRUD Integration

## Integration Steps

### 1. Add DATABASE_URL to globals

Add to `systems/wopr-api/container/app/globals.py`:

```python
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://wopr:wopr@wopr-db:5432/wopr-db'
)
```

### 2. Import and register routers in main.py

Add these imports to `systems/wopr-api/container/app/main.py`:

```python
from app.api.v1 import cameras
from app.api.v1 import config
from app.api.v1 import games      # <-- NEW
from app.api.v1 import pieces     # <-- NEW
from app.api.v1 import mlimages   # <-- NEW
```

Register the routers (add after existing router registrations):

```python
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
app.include_router(games.router, prefix="/api/v1/games", tags=["games"])          # <-- NEW
app.include_router(pieces.router, prefix="/api/v1/pieces", tags=["pieces"])       # <-- NEW
app.include_router(mlimages.router, prefix="/api/v1/mlimages", tags=["mlimages"]) # <-- NEW
```

### 3. Place router files

Move the three router files into your API structure:

```bash
systems/wopr-api/container/app/api/v1/games.py
systems/wopr-api/container/app/api/v1/pieces.py
systems/wopr-api/container/app/api/v1/mlimages.py
```

---

## API Endpoints Summary

### Games: `/api/v1/games`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/games` | List all games (paginated) |
| GET | `/api/v1/games/{game_id}` | Get specific game |
| POST | `/api/v1/games` | Create new game |
| PUT | `/api/v1/games/{game_id}` | Update game |
| DELETE | `/api/v1/games/{game_id}` | Delete game |

**Query Parameters (GET list):**
- `limit`: Max results (default: 100)
- `offset`: Skip N results (default: 0)
- `locale`: Filter by locale

### Pieces: `/api/v1/pieces`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/pieces` | List all pieces (paginated) |
| GET | `/api/v1/pieces/{piece_id}` | Get specific piece |
| POST | `/api/v1/pieces` | Create new piece |
| PUT | `/api/v1/pieces/{piece_id}` | Update piece |
| DELETE | `/api/v1/pieces/{piece_id}` | Delete piece |
| POST | `/api/v1/pieces/{piece_id}/games/{game_id}` | Link piece to game |
| DELETE | `/api/v1/pieces/{piece_id}/games/{game_id}` | Unlink piece from game |

**Query Parameters (GET list):**
- `limit`: Max results (default: 100)
- `offset`: Skip N results (default: 0)
- `locale`: Filter by locale
- `game_id`: Filter pieces by game

### ML Images: `/api/v1/mlimages`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/mlimages` | List all ML image metadata (paginated) |
| GET | `/api/v1/mlimages/{mlimage_id}` | Get specific ML image metadata |
| POST | `/api/v1/mlimages` | Create new ML image metadata |
| PUT | `/api/v1/mlimages/{mlimage_id}` | Update ML image metadata |
| DELETE | `/api/v1/mlimages/{mlimage_id}` | Delete ML image metadata |
| POST | `/api/v1/mlimages/{mlimage_id}/games/{game_id}` | Link ML image to game |
| DELETE | `/api/v1/mlimages/{mlimage_id}/games/{game_id}` | Unlink ML image from game |
| POST | `/api/v1/mlimages/{mlimage_id}/pieces/{piece_id}` | Link ML image to piece |
| DELETE | `/api/v1/mlimages/{mlimage_id}/pieces/{piece_id}` | Unlink ML image from piece |

**Query Parameters (GET list):**
- `limit`: Max results (default: 100)
- `offset`: Skip N results (default: 0)
- `locale`: Filter by locale
- `game_id`: Filter by game
- `piece_id`: Filter by piece

---

## Usage Examples

### Create a Game

```bash
curl -X POST http://localhost:8000/api/v1/games \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Warhammer 40k",
    "description": "Grimdark tabletop wargame",
    "min_players": 2,
    "max_players": 2,
    "locale": "en"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Warhammer 40k",
  "description": "Grimdark tabletop wargame",
  "min_players": 2,
  "max_players": 2,
  "locale": "en",
  "created_at": "2025-01-15T10:30:00",
  ...
}
```

### Create a Piece

```bash
curl -X POST http://localhost:8000/api/v1/pieces \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Intercessor Squad",
    "description": "Space Marine infantry unit",
    "locale": "en"
  }'
```

### Link Piece to Game

```bash
curl -X POST http://localhost:8000/api/v1/pieces/1/games/1
```

Response:
```json
{
  "piece_id": 1,
  "game_id": 1,
  "status": "linked"
}
```

### Create ML Image Metadata

```bash
curl -X POST http://localhost:8000/api/v1/mlimages \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "intercessor_001.jpg",
    "object_rotation": 45,
    "object_position": "center",
    "color_temp": "5500K",
    "light_intensity": "bright"
  }'
```

### Link ML Image to Game and Piece

```bash
# Link to game
curl -X POST http://localhost:8000/api/v1/mlimages/1/games/1

# Link to piece
curl -X POST http://localhost:8000/api/v1/mlimages/1/pieces/1
```

### List Pieces for a Game

```bash
curl "http://localhost:8000/api/v1/pieces?game_id=1"
```

### List ML Images for a Specific Piece

```bash
curl "http://localhost:8000/api/v1/mlimages?piece_id=1"
```

### Update a Game

```bash
curl -X PUT http://localhost:8000/api/v1/games/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "max_players": 4
  }'
```

### Delete a Piece

```bash
curl -X DELETE http://localhost:8000/api/v1/pieces/1
```

---

## OpenAPI Documentation

After integration, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The interactive API docs will show all endpoints with request/response schemas.

---

## Notes

1. **Database Connection**: Make sure `DATABASE_URL` points to your WOPR Strapi database
2. **Timestamps**: `create_time`, `update_time`, `created_at`, `updated_at` are auto-managed
3. **Cascade Deletes**: Deleting games/pieces will cascade delete relationships via foreign keys
4. **Error Handling**: All endpoints return proper HTTP status codes:
   - 200: Success
   - 201: Created
   - 204: No Content (successful delete)
   - 400: Bad Request
   - 404: Not Found
   - 409: Conflict (duplicate relationship)
   - 500: Internal Server Error

5. **Admin Users**: The `created_by_id` and `updated_by_id` fields reference `admin_users` table (managed by Strapi). These are currently nullable and not populated by these endpoints.

---

## Testing Workflow

1. **Create a game** → Get game_id
2. **Create pieces** → Get piece_id values
3. **Link pieces to game** using piece_id and game_id
4. **Create ML images** → Get mlimage_id values
5. **Link ML images to game and pieces**
6. **Query**: List pieces for a game, list ML images for a piece, etc.

---

## Future Enhancements

- Add authentication/authorization
- Populate `created_by_id`/`updated_by_id` from authenticated user
- Add bulk operations (create multiple pieces at once)
- Add search/filter capabilities (by name, description, etc.)
- Add image upload endpoint to store actual image files alongside metadata
- Add validation for `object_position` format (e.g., JSON coordinates)
- Add pagination metadata (total_count, has_next, etc.)
