
```mermaid
flowchart LR
  %% ===== Client =====
  U[User<br/>Desktop / Mobile Browser]
  DNS[DNS: wopr → Studio Ingress]

  U -->|HTTPS https://wopr| DNS

  %% ===== Studio Kubernetes Cluster =====
  subgraph K8S["Studio Kubernetes Cluster"]
    ING[Ingress Controller]
    WEB[wopr-web<br/>Web UI]
    API[wopr-api<br/>FastAPI :8080<br/>Routing + Orchestration]
    CFG[wopr-config_service<br/>Central Config API]
    VSN[wopr-vision<br/>Vision / CV Engine]
    ADJ[wopr-adjudicator<br/>Rules + LLM Engine]
    %% >>> NEW: WOPR-EDM Controller <<<
    EDM[wopr-edm<br/>Edge Device Management<br/>Controller + CRD Watcher]
    %% >>> END NEW <<<
    DB[(wopr-db<br/>PostgreSQL)]
    CFGDB[(wopr-config-db)]
    OTHER[wopr-…<br/>Other Services]
  end

  DNS --> ING
  ING --> WEB
  WEB --> API

  %% ===== Config flows =====
  API --> CFG
  WEB --> CFG
  VSN --> CFG
  ADJ --> CFG
  OTHER --> CFG
  %% >>> NEW: EDM uses config too <<<
  EDM --> CFG
  %% >>> END NEW <<<

  %% ===== Core processing =====
  API --> CAM
  API --> VSN
  API --> ADJ
  ADJ --> VSN

  %% ===== Persistence =====
  API --> DB
  VSN --> DB
  ADJ --> DB
  CFG --> CFGDB
  CFGDB --- DB
  %% >>> NEW: EDM stores device state in DB <<<
  EDM --> DB
  %% >>> END NEW <<<

  %% ===== Edge Devices =====
  subgraph EDGE["Edge / Home Lab"]
    %% >>> NEW: Edge Agent managing cam container <<<
    AGENT[wopr-edge-agent<br/>Device Management Agent<br/>Polls EDM Controller]
    CAM[wopr-cam<br/>Container on Raspberry Pi<br/>4K Webcam Service]
    %% >>> END NEW <<<
    NAS[(NAS Storage)]
  end

  %% >>> NEW: Edge agent flows <<<
  AGENT -.->|Polls for updates<br/>Reports status| EDM
  AGENT -->|Manages container| CAM
  %% >>> END NEW <<<
  
  CAM --> NAS
  API --> NAS
  VSN --> NAS

```

---

## Changes Made

**ADDED:**
- `wopr-edm` service in Studio cluster - Edge Device Management controller
- `wopr-edge-agent` on Raspberry Pi - Polls EDM, manages local containers
- Connection: Edge agent polls EDM controller for updates, reports status
- EDM uses config service and database for device state management
- Edge agent manages wopr-cam container (cam is now containerized)

**PHILOSOPHY:**
- EDM = k8s-style control plane for edge infrastructure
- Reconciliation loop pattern (desired vs actual state)
- Edge agent handles: container updates, rollbacks, health checks, status reporting
