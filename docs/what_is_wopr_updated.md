# WOPR - Wargaming Oversight & Position Recognition

## What is WOPR?

WOPR tracks tabletop game state through computer vision.  Players use a web interface to capture overhead images of their game board. WOPR analyzes the images, detects game pieces, validates moves against rules, and maintains a complete game history.

when playing a game, the idea is that you get setup, then start the game in WOPR, it'll ask when you're ready for the first image to be taken, and when yes, it'll take it.  The system should be able to take that image and identify to within 90% accuracy as to what's on the board, note where the pieces are, who has what cards, etc...., then after each round, a pic is taken, and is compared to what it was before, and maybe some questions are asked if the model isnt sure, but ultimatly, the user and wopr agree to the state (the user can adjust the game in wopr as necessary), then the next round is played, the process repeated.

## User Flow

1. User browses to [https://wopr](https://wopr/) (resolves to k8s ingress)
2. Select game type (Dune Imperium, Star Wars Legion, etc.)
3. Enter game details (players, initial setup)
4. Click "Capture" after each move
5. WOPR analyzes board state, validates rules
6. View game history, replay moves, export state

## Architecture

### Frontend

**wopr-web** - React 18 SPA

- Game selection and setup
- Live capture triggering
- Real-time analysis results display
- Game history/replay viewer
- Config editor (admin)
- Responsive: mobile/desktop, light/dark mode

### API Layer

**wopr-api** - FastAPI (Python 3.11+)

- Port: 8000
- Handles routing and orchestration
- Synchronous endpoints: game CRUD, status queries
- Async task queueing: vision analysis, rule validation
- Direct database access for reads/writes

### Storage & Config

**wopr-config-service** - FastAPI

- Port: 8080
- Centralized configuration service
- PostgreSQL backend (wopr_config database)
- HTTP API: GET/SET config values
- Change history and audit trail
- See Appendix A for schema

**wopr-db** - PostgreSQL 16 StatefulSet

- Databases:
    - wopr_main: game data, captures, analysis
    - wopr_config: configuration store
    - wopr_edm: edge device management state **(NEW)**
- 20Gi PVC, single replica (HA later)
- Backups: pg_dump to NAS nightly (TBD)

**wopr-redis** - Redis 7

- Celery task broker
- Config value caching
- Session storage (future)

**NFS Storage** - /mnt/nas/wopr

- Mounted by all pods
- Images: /mnt/nas/wopr/games/{game_id}/
- Backed by existing NAS infrastructure

### Processing Services

**wopr-worker** - Celery workers (Python 3.11+)

- Async task processing
- Multiple replicas for scaling
- Tasks:
    - Vision analysis (30-60s per image)
    - Board state validation
    - Thumbnail generation
    - Historical game replay

**wopr-vision** - Vision processing service

- Ollama + Qwen2-VL:7b for image understanding
- OpenCV for change detection, segmentation
- Future: YOLOv8 custom models per game
- Runs on nodes with GPU access (desktop: 4080 Super)

**wopr-adjudicator** - Rules engine service

- Validates moves against game rules
- Detects illegal plays/cheating
- LLM-based rule interpretation for edge cases
- Coordinates re-analysis requests to wopr-vision
- Rule definitions per game type in config

### Edge Services

<!-- ========== NEW SECTION: WOPR-EDM ========== -->
**wopr-edm** - Edge Device Management **(NEW)**

- Kubernetes-based edge infrastructure orchestration platform
- Manages full lifecycle of edge devices (Raspberry Pis, cameras, sensors, etc.)
- **Architecture Pattern**: Custom Resource Definition (CRD) + Controller
  - `wopr_device` CRD defines desired device state
  - Controller watches for changes, reconciles actual state
  - Edge agents poll controller, report status back
- **Capabilities** (current + future):
  - Container orchestration: Docker/Podman compose management
  - Infrastructure provisioning: OpenTofu/Terraform
  - Configuration management: Ansible playbooks
  - Database operations: PostgreSQL management, migrations
  - Remote access: SSH key distribution, secure tunneling
  - Network management: DNS, firewall rules, service discovery
  - Version control: Automatic updates with health checks + rollback
  - Telemetry: Device health, resource utilization, connectivity status
- **Reconciliation Loop**:
  - Compare desired_version vs current_version
  - Deploy updates when drift detected
  - 60s health check window
  - Automatic rollback on failure
  - Report status back to CRD
- **Degraded State Handling**:
  - Edge devices cache config locally (72h TTL)
  - Continue operation when disconnected from mothership
  - Flag as degraded after cache expiration
  - Auto-recover when connectivity restored
- **Future Vision**: Full fleet management for distributed edge infrastructure

**wopr-edge-agent** - Edge Device Agent **(NEW)**

- Python service running on edge devices (Raspberry Pi, NUC, etc.)
- **Responsibilities**:
  - Poll wopr-edm controller for updates (config, versions, tasks)
  - Manage local Docker Compose services
  - Execute infrastructure changes (ansible, tofu, etc.)
  - Health monitoring and reporting
  - Local config caching with 72h TTL
  - Graceful degradation when disconnected
- **Deployment**: Runs as systemd service, manages itself after bootstrap
- **Auth**: TBD (ServiceAccount token, cert-based, or API gateway)
- **Local State**: Maintains "last known good" config and version tags
- **Telemetry**: Reports device health, service status, resource usage back to EDM

<!-- ========== END NEW SECTION ========== -->

**wopr-cam** - Camera service (Raspberry Pi) **(UPDATED: Now containerized)**

- Flask API, port 5000
- Camera Module 3 (12MP, 4K capable)
- Endpoint: POST /capture
- Saves to NFS, returns image path
- **Deployment**: Docker container managed by wopr-edge-agent **(NEW)**
- 3D printed overhead mount

## Data Flows

### Capture & Analyze (Async)

```
User → wopr-web → wopr-api
                    ↓
              HTTP → wopr-cam → image saved to NFS
                    ↓
              Celery task queued
                    ↓
              wopr-worker picks up task
                    ↓
              calls wopr-vision → analysis
                    ↓
              calls wopr-adjudicator → validation
                    ↓
              saves to wopr-db
                    ↓
              wopr-web polls/WebSocket → displays results

```

### Manual Analysis (User triggered later)

```
User → "Analyze capture #5" → wopr-api
                                ↓
                          Celery task queued
                                ↓
                          (same as above)

```

### Config Updates

```
User → wopr-web config editor → wopr-api
                                   ↓
                            wopr-config-service
                                   ↓
                            PostgreSQL update
                                   ↓
                          All services fetch new value

```

<!-- ========== NEW DATA FLOW ========== -->
### Edge Device Management (NEW)

```
Admin → Update wopr_device CRD → Kubernetes API
                                      ↓
                              wopr-edm controller detects change
                                      ↓
                              Updates desired state in DB
                                      ↓
wopr-edge-agent polls (30-60s interval)
                ↓
        Detects version drift
                ↓
        Pulls new container image
                ↓
        Health check (60s window)
                ↓
        Success: Update CRD status
        Failure: Rollback + alert
                ↓
        Continue polling loop

```

**Disconnected Operation:**
```
Edge agent loses connectivity
        ↓
Uses cached config (72h TTL valid)
        ↓
Continues normal operation
        ↓
After 72h: Flags self as degraded
        ↓
Reconnects: Syncs state, clears degraded flag

```
<!-- ========== END NEW DATA FLOW ========== -->

## Tech Stack

- **K8s Cluster**: studio (on-prem)
- **Ingress**: Traefik with cert-manager (TLS)
- **Languages**: Python 3.11+, JavaScript/React
- **Frameworks**: FastAPI, React 18
- **Databases**: PostgreSQL 16, Redis 7
- **Vision**: Ollama (Qwen2-VL), OpenCV, YOLOv8
- **Task Queue**: Celery + Redis
- **Storage**: NFS (existing NAS)
- **GitOps**: ArgoCD
- **IaC**: OpenTofu, Ansible **(NEW)**
- **Edge Orchestration**: Custom CRD + Controller **(NEW)**
- **Monitoring**: Prometheus, Grafana, Loki

## Future Services

- **wopr-notifier**: WebSocket/SSE for real-time updates
- **wopr-replay**: Game replay and video generation
- **wopr-tournament**: Multi-game tournament tracking
- **wopr-ml-trainer**: Custom model training pipeline
- **wopr-edm-ui**: Web UI for fleet management and device provisioning **(NEW)**

---

## Changes Made

**ADDED:**
- `wopr-edm` service: Full edge infrastructure lifecycle management
- `wopr-edge-agent`: Runs on Pis, polls for updates, manages containers
- New database: `wopr_edm` for device state tracking
- Edge device management data flows (reconciliation + disconnected operation)
- Tech stack additions: OpenTofu, Ansible, CRD/Controller pattern
- Future service: wopr-edm-ui for fleet management

**UPDATED:**
- `wopr-cam` now runs as Docker container managed by edge agent
- Architecture now includes edge device management layer
