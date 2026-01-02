# WOPR Database Schema

## Overview
The WOPR database uses a CMS-style schema pattern with support for internationalization, versioning, and audit trails. Core entities are Games, Pieces, and ML Image Metadata with many-to-many relationships between them.

## Tables

### games
Stores game definitions (e.g., Warhammer 40k, Chess, etc.)

| Column | Type | Notes |
|--------|------|-------|
| id | integer | Primary key |
| document_id | varchar(255) | Document versioning identifier |
| uid | varchar(255) | Unique identifier |
| name | varchar(255) | Game name |
| description | text | Game description |
| min_players | integer | Minimum players |
| max_players | integer | Maximum players |
| create_time | timestamp(6) | |
| update_time | timestamp(6) | |
| created_at | timestamp(6) | CMS audit field |
| updated_at | timestamp(6) | CMS audit field |
| published_at | timestamp(6) | Publication timestamp |
| created_by_id | integer | FK → admin_users(id) |
| updated_by_id | integer | FK → admin_users(id) |
| locale | varchar(255) | Localization support |

**Indexes:**
- Primary key on `id`
- Composite index: `(document_id, locale, published_at)`
- Foreign key indexes on `created_by_id`, `updated_by_id`

---

### pieces
Stores game piece definitions (e.g., Space Marine, Pawn, Tank)

| Column | Type | Notes |
|--------|------|-------|
| id | integer | Primary key |
| document_id | varchar(255) | Document versioning identifier |
| name | varchar(255) | Piece name |
| uid | varchar(255) | Unique identifier |
| create_time | timestamp(6) | |
| update_time | timestamp(6) | |
| description | text | Piece description |
| created_at | timestamp(6) | CMS audit field |
| updated_at | timestamp(6) | CMS audit field |
| published_at | timestamp(6) | Publication timestamp |
| created_by_id | integer | FK → admin_users(id) |
| updated_by_id | integer | FK → admin_users(id) |
| locale | varchar(255) | Localization support |

**Indexes:**
- Primary key on `id`
- Composite index: `(document_id, locale, published_at)`
- Foreign key indexes on `created_by_id`, `updated_by_id`

---

### ml_image_metadatas
Stores metadata for training images used in computer vision ML models

| Column | Type | Notes |
|--------|------|-------|
| id | integer | Primary key |
| document_id | varchar(255) | Document versioning identifier |
| filename | varchar(255) | Image filename |
| uid | varchar(255) | Unique identifier |
| create_time | timestamp(6) | |
| update_time | timestamp(6) | |
| object_rotation | integer | Rotation angle of object |
| object_position | varchar(255) | Position coordinates |
| color_temp | varchar(255) | Color temperature |
| light_intensity | varchar(255) | Lighting conditions |
| created_at | timestamp(6) | CMS audit field |
| updated_at | timestamp(6) | CMS audit field |
| published_at | timestamp(6) | Publication timestamp |
| created_by_id | integer | FK → admin_users(id) |
| updated_by_id | integer | FK → admin_users(id) |
| locale | varchar(255) | Localization support |

**Indexes:**
- Primary key on `id`
- Composite index: `(document_id, locale, published_at)`
- Foreign key indexes on `created_by_id`, `updated_by_id`

---

## Relationships
```
admin_users (external)
    ↓
    ├─→ games (created_by_id, updated_by_id)
    ├─→ pieces (created_by_id, updated_by_id)
    └─→ ml_image_metadatas (created_by_id, updated_by_id)

games ←→ pieces
    (many-to-many via pieces_game_lnk)

games ←→ ml_image_metadatas
    (many-to-many via ml_image_metadatas_game_lnk)

pieces ←→ ml_image_metadatas
    (many-to-many via ml_image_metadatas_piece_lnk)
```

### Link Tables (inferred from foreign keys)

#### pieces_game_lnk
Links pieces to games (e.g., "Intercessor" belongs to "Warhammer 40k")
- `piece_id` → pieces(id) CASCADE DELETE
- `game_id` → games(id) CASCADE DELETE

#### ml_image_metadatas_game_lnk
Links training images to games
- `ml_image_metadata_id` → ml_image_metadatas(id) CASCADE DELETE
- `game_id` → games(id) CASCADE DELETE

#### ml_image_metadatas_piece_lnk
Links training images to specific pieces
- `ml_image_metadata_id` → ml_image_metadatas(id) CASCADE DELETE
- `piece_id` → pieces(id) CASCADE DELETE

---

## Design Notes

### CMS Pattern
The schema follows a headless CMS pattern (likely Strapi or Directus):
- **document_id**: Supports versioning/localization of content
- **published_at**: Content publication workflow
- **locale**: Multi-language support
- **created_by_id/updated_by_id**: Audit trail via admin_users

### ML Training Data
The `ml_image_metadatas` table captures environmental conditions for training images:
- Rotation, position for data augmentation
- Color temperature, light intensity for normalization
- Many-to-many with both games and pieces for flexible tagging

### Cascade Deletes
All link table foreign keys use `ON DELETE CASCADE`, ensuring referential integrity when games/pieces/images are removed.

---

## Usage Scenarios

1. **Define a game**: Insert into `games` table
2. **Define pieces for that game**: Insert into `pieces`, link via `pieces_game_lnk`
3. **Upload training images**: 
   - Insert into `ml_image_metadatas` with environmental metadata
   - Link to game via `ml_image_metadatas_game_lnk`
   - Link to specific pieces via `ml_image_metadatas_piece_lnk`
4. **Query training set**: Join through link tables to get all images for a specific game or piece

---

## Missing admin_users Table
The schema references `admin_users(id)` but that table definition wasn't included in the dump. This is likely managed by the CMS layer (Directus/Strapi) for user authentication and authorization.