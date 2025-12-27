# WOPR UI Layout Proposal

## Primary Navigation Structure

### 1. PLAY (Active game operations)
- Start Game
- Active Games (list with quick controls)
- Stop/Adjudicate inline per game
- Game History/Archives

### 2. SETUP (Game library & training)
- Game Collection (list view)
- Add/Remove games inline
- Training Pipeline (per-game expandable)
  - Train Model
  - Edit Training
  - Add Training Data

### 3. CAPTURE (Hardware & data acquisition)
- Cameras (list all, status, take pics)
- Image Library
- Image Properties/Metadata

### 4. SYSTEM (Config & admin)
- Configuration
- Bulk Operations

## Layout Rationale

**Play-first**: The core loop is "start game → capture → adjudicate → monitor." Keep that pathway short.

**Setup segregated**: Training and game library management are pre-game activities. Don't clutter the active gameplay space.

**Capture consolidated**: Camera and image management are tightly coupled. Splitting "get cams" from "see images" creates cognitive overhead.

**System last**: Config and bulk ops are power-user territory. Bury them appropriately.

## Anti-pattern Warning

Don't split "see active games" and "control active games" into separate nav items. That's two clicks for one conceptual task. Active games should be a **dashboard view** with inline controls.


graph TD
    WOPR[WOPR]
    
    WOPR --> PLAY[1. PLAY]
    WOPR --> SETUP[2. SETUP]
    WOPR --> CAPTURE[3. CAPTURE]
    WOPR --> SYSTEM[4. SYSTEM]
    
    PLAY --> P1[Start Game]
    PLAY --> P2[Active Games Dashboard]
    PLAY --> P3[Game History/Archives]
    
    P2 --> P2A[Stop/Adjudicate inline]
    P2 --> P2B[Quick controls per game]
    
    SETUP --> S1[Game Collection]
    SETUP --> S2[Training Pipeline]
    
    S1 --> S1A[Add/Remove games inline]
    
    S2 --> S2A[Train Model]
    S2 --> S2B[Edit Training]
    S2 --> S2C[Add Training Data]
    
    CAPTURE --> C1[Cameras]
    CAPTURE --> C2[Image Library]
    CAPTURE --> C3[Image Properties/Metadata]
    
    C1 --> C1A[List all / Status]
    C1 --> C1B[Take pics]
    
    SYSTEM --> SY1[Configuration]
    SYSTEM --> SY2[Bulk Operations]
    
    style PLAY fill:#4a9eff
    style SETUP fill:#ffa500
    style CAPTURE fill:#9370db
    style SYSTEM fill:#708090