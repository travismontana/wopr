# C4 Model: Dynamic Diagram

## WOPR - Game Session Workflow

```mermaid
sequenceDiagram
    actor Player
    participant Web as WOPR Web UI
    participant API as WOPR API
    participant DB as PostgreSQL
    participant Cam as Camera Service
    participant NFS as NFS Storage
    participant Redis as Redis Queue
    participant Worker as Celery Worker

    Note over Player,Worker: Scenario: Complete Game Session Lifecycle

    rect rgb(200, 220, 240)
        Note over Player,DB: 1. Session Creation
        Player->>Web: Select game from catalog
        Web->>API: GET /api/v2/games
        API->>DB: SELECT * FROM games
        DB-->>API: Game list
        API-->>Web: Games data
        Web-->>Player: Display game options
        
        Player->>Web: Click "Start New Game"
        Web->>API: GET /api/v2/session/new/{game_id}
        API->>DB: INSERT INTO sessiontracker
        DB-->>API: session_id, uuid
        API-->>Web: session data {id, uuid}
        Web-->>Player: Show session started
    end

    rect rgb(220, 240, 200)
        Note over Player,NFS: 2. Round Start - Initial Capture
        Player->>Web: Click "Start Round 1"
        Web->>API: POST /api/v2/session/capture
        Note right of API: payload: {<br/>camid, filename,<br/>sessionuuid}
        API->>Cam: POST /capture {camid, filename}
        Cam->>Cam: Initialize camera
        Cam->>Cam: Capture image
        Cam->>NFS: Save image to incoming/
        NFS-->>Cam: File saved
        Cam-->>API: {status: success, path}
        
        API->>DB: INSERT INTO playtracker
        Note right of API: Record play with:<br/>sessionid, filename,<br/>timestamp, status=active
        DB-->>API: play_id
        API-->>Web: Capture complete
        Web-->>Player: Show captured image
    end

    rect rgb(240, 220, 200)
        Note over Player,NFS: 3. Player Makes Move
        Player->>Player: Physical move on game board
        Player->>Web: Enter move notes
        Player->>Web: Click "End Turn"
        
        Web->>API: POST /api/v2/session/capture
        API->>Cam: POST /capture (end-of-turn)
        Cam->>NFS: Save image
        Cam-->>API: Success
        
        API->>DB: INSERT INTO playtracker
        Note right of DB: New play record:<br/>- sessionid<br/>- playerid<br/>- note (move description)<br/>- filename
        DB-->>API: play_id
        API-->>Web: Turn recorded
        Web-->>Player: Ready for next turn
    end

    rect rgb(220, 200, 240)
        Note over Player,NFS: 4. Multiple Rounds (Repeated)
        loop Each Round
            Player->>Web: Start Round N
            Web->>API: Trigger capture
            API->>Cam: Capture start-of-round
            Cam->>NFS: Save image
            
            Player->>Player: Make moves
            
            Player->>Web: End Round N
            Web->>API: Trigger capture
            API->>Cam: Capture end-of-round
            Cam->>NFS: Save image
            API->>DB: Record plays
        end
    end

    rect rgb(240, 240, 200)
        Note over Player,Worker: 5. Session Completion & Archiving
        Player->>Web: Click "End Game"
        Web->>API: PATCH /api/v2/session/{id}
        Note right of API: Update status to 'completed'
        API->>DB: UPDATE sessiontracker SET status='completed'
        DB-->>API: Updated
        API-->>Web: Session completed
        
        Player->>Web: Click "Archive Session"
        Web->>API: POST /api/v2/tasks/archive/{session_id}
        API->>Redis: Enqueue archive_session_images task
        Redis-->>API: Task ID
        API-->>Web: Task queued {task_id}
        Web-->>Player: Archiving in progress...
        
        Redis->>Worker: Dispatch task
        Worker->>DB: Get session data (uuid)
        DB-->>Worker: session data
        Worker->>DB: Get all play filenames
        DB-->>Worker: [file1.jpg, file2.jpg, ...]
        
        loop For each file
            Worker->>NFS: Move incoming/{file} to archive/{file}
            alt Success
                NFS-->>Worker: Moved successfully
            else File not found
                NFS-->>Worker: NotFoundError
                Worker->>Worker: Log error, continue
            else Already archived
                NFS-->>Worker: ExistsError
                Worker->>Worker: Log warning, continue
            end
        end
        
        Worker->>DB: UPDATE playtracker SET status='archived'
        DB-->>Worker: Updated
        Worker->>Redis: Store result {success: [...], errors: [...]}
        
        Web->>API: GET /api/v2/tasks/{task_id}/status
        API->>Redis: Query task result
        Redis-->>API: Task result
        API-->>Web: {status: complete, results}
        Web-->>Player: Session archived (X files, Y errors)
    end
```

## Workflow Description

### 1. Session Creation (Player Initiates Game)

**Steps**:
1. Player browses available games in the web interface
2. Web UI fetches game catalog from API
3. API queries PostgreSQL for game list
4. Player selects a game and clicks "Start New Game"
5. API creates new session record with:
   - Auto-generated UUID (for filenames)
   - Game ID reference
   - Status: 'active'
   - Timestamp
6. Session data returned to player

**Key Data**:
- Session UUID: Used in all image filenames for this session
- Session ID: Database primary key for relationships

**Assumptions**:
- Player authentication happens before this flow (not shown)
- Game catalog is relatively static (cached in Web UI)

### 2. Round Start - Initial Capture

**Steps**:
1. Player clicks "Start Round N" button
2. Web UI sends capture request to API with:
   - Camera ID
   - Filename: `game-{uuid}-round{n}-start.jpg`
   - Session UUID
3. API forwards request to Camera Service
4. Camera Service:
   - Initializes camera hardware
   - Captures high-resolution image
   - Saves to NFS `/incoming/` directory
5. API creates play record in database:
   - Links to session via session_id
   - Stores filename for retrieval
   - Timestamp of capture
   - Status: 'active'
6. Web UI displays captured image via Thumbor (thumbnail)

**Error Handling**:
- Camera unavailable: Retry with exponential backoff
- NFS mount failure: Alert admin, queue for retry
- Database insert failure: Rollback, return error to user

### 3. Player Makes Move

**Steps**:
1. Player physically moves game pieces on the board
2. Player enters notes about the move in Web UI (optional)
3. Player clicks "End Turn" or "Capture Move"
4. Repeat of capture process with filename: `game-{uuid}-round{n}-play{p}.jpg`
5. Play record created with:
   - Move notes
   - Filename
   - Player ID
   - Timestamp

**Business Logic**:
- Each physical move captured for later review
- Notes provide context for automated analysis
- Timestamps enable replay of game progression

### 4. Multiple Rounds (Loop)

The capture process repeats for each round and turn:
- Start of round: Capture initial state
- Each turn: Capture after move
- End of round: Capture final state

**Typical Pattern**:
```
Round 1: start → player1-move1 → player2-move1 → ... → end
Round 2: start → player1-move1 → player2-move1 → ... → end
...
Round N: start → ... → end
```

**File Accumulation**:
- A 10-round game with 2 players and 5 moves per player per round:
  - 10 round-start images
  - 10 × 2 × 5 = 100 move images
  - 10 round-end images
  - **Total: 120 images per session**

### 5. Session Completion & Archiving

**Steps**:

**5a. Mark Session Complete**:
1. Player clicks "End Game"
2. API updates session status to 'completed'
3. Session no longer appears in "active sessions" list

**5b. Archive Files (Async)**:
1. Player or automated process triggers archiving
2. API enqueues Celery task with session ID
3. Task immediately returns task ID to player
4. Player sees "Archiving in progress..." with task ID

**5c. Background Processing** (Celery Worker):
1. Worker receives task from Redis queue
2. Queries database for session UUID and all play filenames
3. For each file:
   - Attempts to move from `/incoming/` to `/archive/`
   - Logs success or specific error (not found, already archived)
   - Continues to next file (best-effort)
4. Updates play records: status = 'archived'
5. Stores result summary in Redis:
   ```json
   {
     "success": ["file1.jpg", "file2.jpg"],
     "errors": [
       {"file": "file3.jpg", "error": "NotFoundError: already archived"},
       {"file": "file4.jpg", "error": "PermissionError: ..."}
     ]
   }
   ```

**5d. Result Polling**:
1. Web UI polls API for task status every 2-5 seconds
2. API queries Redis for task result
3. When complete, displays summary to player:
   - "120 files archived successfully"
   - "2 files had errors (see details)"

**Best-Effort Design**:
- Individual file failures don't fail entire archiving operation
- Errors logged for manual review
- Player notified of partial success

## Alternative Flow: Label Studio Export

```mermaid
sequenceDiagram
    actor DataScientist as Data Scientist
    participant Web as WOPR Web UI
    participant API as WOPR API
    participant Redis as Redis Queue
    participant Worker as Celery Worker
    participant NFS as NFS Storage
    participant LS as Label Studio API

    DataScientist->>Web: Select archived session
    DataScientist->>Web: Click "Export to Label Studio"
    
    Web->>API: POST /api/v2/tasks/export_labelstudio/{session_id}
    API->>Redis: Enqueue export task
    Redis-->>API: Task ID
    API-->>Web: Task queued
    
    Redis->>Worker: Dispatch task
    Worker->>NFS: Copy archive/{files} to labelstudio/
    Worker->>LS: Create annotation tasks
    Note right of LS: POST /api/projects/{id}/tasks<br/>with image URLs
    LS-->>Worker: Task IDs created
    Worker->>Redis: Store result
    
    Web->>API: Poll task status
    API->>Redis: Get result
    Redis-->>API: Export complete
    API-->>Web: Success, N images exported
    Web-->>DataScientist: Ready for annotation
    
    DataScientist->>LS: Open Label Studio
    DataScientist->>LS: Annotate game pieces
```

## Error Scenarios

### Camera Failure During Capture

```mermaid
sequenceDiagram
    participant Web
    participant API
    participant Cam as Camera Service

    Web->>API: POST /capture
    API->>Cam: Trigger capture
    Cam->>Cam: Camera initialization failed
    Cam-->>API: HTTPException 503 (Camera unavailable)
    API-->>Web: Error response
    Web->>Web: Display error to user
    Web->>Web: Offer "Retry" button
    
    alt User retries
        Web->>API: Retry capture (same payload)
    else User cancels
        Web->>Web: Return to game interface
    end
```

### Database Connection Lost During Play Creation

```mermaid
sequenceDiagram
    participant API
    participant DB as PostgreSQL
    participant NFS

    API->>NFS: Save image (already completed)
    API->>DB: INSERT INTO playtracker
    DB-->>API: ConnectionError
    API->>API: Catch exception
    API->>API: Log error with trace ID
    API-->>Web: HTTPException 500
    
    Note over API,DB: Image saved but orphaned<br/>(no database record)
    
    Note over API: Recovery options:<br/>1. Retry transaction<br/>2. Background reconciliation<br/>3. Manual cleanup
```

## Performance Considerations

### Concurrent Captures
Multiple players in different sessions can capture simultaneously:
- Camera Service: Queue requests or reject if busy
- NFS: Concurrent writes to different files (safe)
- Database: Concurrent inserts with different session IDs (safe)

### Large Archiving Jobs
Session with 500+ images:
- Task execution time: 5-10 minutes
- Chunked processing: 50 files at a time
- Progress updates: Store intermediate results
- Timeout protection: Celery task timeout set appropriately

### Image Retrieval
Player reviewing past games:
- Thumbnails: Generated on-demand by Thumbor, cached
- Full images: Direct NFS access via static file serving
- Pagination: Limit images per request (e.g., 20)

## Assumptions

1. **Single Camera**: System assumes one camera per deployment
2. **Synchronous Captures**: Player waits for capture to complete before continuing
3. **File System Latency**: NFS operations complete within 1-2 seconds
4. **Task Execution**: Workers process tasks within minutes, not hours
5. **Network Reliability**: Stable connections between containers
6. **Session Locking**: No concurrent modifications to same session (UI-enforced)
7. **Image Immutability**: Once captured, images never modified
8. **Archiving Idempotency**: Archiving task can be safely retried

## Missing Information

- Retry policies for failed captures
- Timeout values for camera operations
- Maximum concurrent users/sessions
- Image resolution and file sizes
- NFS performance characteristics
- Database transaction isolation levels
- Celery worker concurrency settings
- Task priority and routing
- Rollback procedures for failed operations
- Monitoring and alerting thresholds