# WOPR Project Status

**Last Updated:** 2025-12-18
**Current Phase:** Phase 1 - Infrastructure

---

**Things I'd like now that I've had time to process things**
- on wopr_config - needs a UI that can edit the thing like yaml.
- local config cache, cache invalidation, config versioning in the DB, auto config rollback if a problem detected, problem detection. 
- status page *
- telemetry **
- add telemetry to config and core module *
- centralize the core module **
- installer
- be able to rollout services via installer
<!-- >>> NEW >>> -->
- **WOPR-EDM**: Edge device management platform for full infrastructure lifecycle (containers, tofu, ansible, psql, ssh, etc.)
- Edge agent with 72h config cache + graceful degradation
- in the Dockerfile's:  
- Pull what they are from a central service and have wopr-edm start it.
<!-- >>> END NEW >>> -->

---

**20251226 - 2025, Dev 26**
* Prompt for status checks:
```
In wopr-api, I want to add a /api/v1/status.py, You do db-up, show me the python/fastapi you would do to check if the db is up.  I'll do the rest, so you do just db-up, and recommend how to do the db thing.

DB to use:
kubectl -n wopr get secret wopr-config-db-cluster-app -o jsonpath='{.data.uri}' | base64 -d

I guess create a new table? or a new database? not sure how to do that or which.

Tests:

- Timestamps before and after ()
- "db-up" : bool - Can i connect to the port/see a prompt to login or SELECT 1
  "db-queriable" : bool - Can I query something I care about?
  "db-writable": bool - Are the disks alive?
  "wopr-web-up" : boo - Can I get to the web page and get some html?
  "wopr-web-functional" : bool - Can I get soem dynamic content on the page?
  "wopr-api-up" : bool - Can I connect and see things?
  "wopr-api-functional" : bool - Can I connect and write thing?
  "wopr-cam-up" : bool - Can I connect to the cam service?
  "wopr-cam-functional" : bool - Does it tell me the cam status?

Each test will report {"test-start-timestamp" : timestamp, "test-result" : pass|fail|norun, "test-end-timestamp"}, 
then the test master will write that to the database.

GET /
- Shows the current status of teh environment in json, the format will be:
{
  "timestamp_right_before_data_pull": "standardformat_precision_tdb",
  "db-up" : bool,
  "db-queriable" : bool,
  "db-writable": bool,
  "wopr-web-up" : bool,
  "wopr-web-functional" : bool,
  "wopr-api-up" : bool,
  "wopr-api-functional" : bool,
  "wopr-cam-up" : bool,
  "wopr-cam-functional" : bool,
  "wopr-config-map-present" : bool,
  "timestamp_right_after_data_pull": "standardformat_precision_tdb"
}

GET /{one-of-the-things-from-above}

To run the tests, writes to a database.
POST /
{
  "all": "true",
  "specific" : [
    {
      "test-standard-name" : bool
    }
  ]
}

There will be a prefect that will administer the tests.


**20251218 - 2025, Dec 18** <!-- NEW -->
* Conceptualized WOPR-EDM (Edge Device Management) service
* Architecture: CRD + Controller pattern for edge fleet management
* Edge agent design: polling, reconciliation, rollback, degraded state
* Future capabilities: tofu, ansible, psql, ssh, remote docker control

**20251217 - 2025, Dec 17**
* Grafana/loki/prom up and running.
* all 3 clusters reporting in.
* tagged v0.1.0
* going to enable tracing in the config

**20251216 - 2025, Dec 16**
Stuff....

**20251215 - 2025, Dec 15**
What I got done:
* wopr-config.studio is running in the cluster and works.
* Next: webui + api
* and fire the new ai, go back to reggie claude.

## 🎯 Current Focus

**20251218 - 2025, Dec 18** <!-- UPDATED DATE -->
**What I'm actively working on right now:**
- [ ] Setting up config service in k8s cluster
- [X] rpi + webcam (Bus 001 Device 003: ID 328f:00ec EMEET EMEET SmartCam C960 4K)
- [X] have a python script to caputre the images using the wopr-config python module.
- [X] writing a service to run on woprcam (the pi) and take the image.
- [X] Decision: naming convention, so wopr-config_service not wopr-config-service, because the thing is "config_service" and wopr is the "app" or "env" or whatever. - seperates major things, _ is spaces in names in names of services or apps, so app-service_name.
- [ ] want to see how to integrate a proper project mangement system easily into claude and my github so I can use 1 ui for code and pm tracking, and claude is updated.  Or if I can just do diffs like this, where I update this section, and paste it into claude, that'd work, but I'd like him to at least see my code and keep updated of what's going on. Do this:
```
git commit -m "feat: wopr-cam_service flask endpoint"

# Update STATUS.md
# Add commit message to "Recently Completed"

# When chatting with Claude
git log --oneline -10 > recent_work.txt
# Paste STATUS.md + recent_work.txt
```
<!-- >>> NEW >>> -->
- [ ] **WOPR-EDM Design**: Flesh out CRD spec, controller logic, edge agent architecture
- [ ] Containerize wopr-cam for edge agent management
<!-- >>> END NEW >>> -->

**Where to pick up:**
- Get wopr_config in k8s (done)
- python module distribution
- Logging
<!-- >>> NEW >>> -->
- WOPR-EDM CRD definition
- Edge agent prototype
<!-- >>> END NEW >>> -->

**Time estimate to complete current tasks:** 

---

## ✅ Recently Completed (Last 7 Days)

- [x] 2025-12-18: Conceptualized WOPR-EDM edge device management platform <!-- NEW -->
- [x] 2025-12-14: Config system built (wopr-config-service)
- [x] 2025-12-14: WOPR core library created
- [x] 2025-12-14: Documentation framework started
- [x] 2025-12-14: Milestones defined

---

## 🚧 Blockers / Issues

**Active blockers:**
- None currently

**Questions/Decisions needed:**
- Should wopr-vision and wopr-adjudicator be separate services or combined?
<!-- >>> NEW >>> -->
- **WOPR-EDM Auth**: Edge agent → k8s API direct, or via gateway/proxy service?
- **CRD Scope**: Namespace-scoped or cluster-scoped for wopr_device?
- **Edge Agent Bootstrap**: How does new Pi discover mothership? (mDNS, hardcoded, USB config?)
<!-- >>> END NEW >>> -->

**Waiting on:**
- Hardware: RPi Camera Module 3 (ETA: )
- 

---

## 📋 Next Steps (Prioritized)

1. Deploy config service to k8s
2. Set up PostgreSQL (wopr-db)
3. Configure NFS mounts on k8s nodes
<!-- >>> NEW >>> -->
4. **Design WOPR-EDM CRD spec** (desiredVersion, currentVersion, healthStatus, etc.)
5. **Build wopr-edge-agent prototype** (polling loop, config cache, container mgmt)
6. **Containerize wopr-cam** for edge agent management
<!-- >>> END NEW >>> -->
7. Build wopr-cam service skeleton <!-- KEPT, but now means containerizing it -->

---

## 📊 Quick Stats

| Metric | Status |
|--------|--------|
| Services Deployed | 0/10 | <!-- UPDATED: was 0/9, now 0/10 with EDM -->
| Tests Passing | N/A |
| Database Migrations | 0 created |
| Last Successful Capture | N/A |
| Total Games Tracked | 0 |
| Config Service | Local only |
| **Edge Devices Managed** | **0** | <!-- NEW -->

---

## 🔧 Environment Status

**What's running where:**
- **Local (docker-compose):**
  - [x] wopr-config-service (port 8080)
  - [x] wopr-config-db (PostgreSQL)
  
- **K8s Cluster (studio):**
  - [ ] Nothing deployed yet
  
- **Raspberry Pi:**
  - [ ] Not set up yet
  <!-- >>> NEW >>> -->
  - [ ] wopr-edge-agent (planned)
  - [ ] wopr-cam (containerized, managed by edge agent)
  <!-- >>> END NEW >>> -->
  
- **Desktop (Ollama):**
  - [ ] Not configured yet

---

## 📝 Technical Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-18 | **WOPR-EDM: CRD + Controller pattern** | **k8s-native edge management, declarative desired state** | <!-- NEW -->
| 2025-12-18 | **Edge agent: 72h config cache + degraded flag** | **Graceful degradation when disconnected from mothership** | <!-- NEW -->
| 2025-12-18 | **Containerize wopr-cam** | **Managed by edge agent for automated updates + rollback** | <!-- NEW -->
| 2025-12-14 | Use database-backed config service | Dynamic updates without redeployment |
| 2025-12-14 | Celery for async processing | Vision analysis takes 30-60s, can't block API |
| 2025-12-14 | FastAPI for wopr-api | Modern, async-capable, good docs |

---

## 🐛 Known Issues

- None yet

---

## 💡 Ideas / Future Enhancements

- Consider WebSocket for real-time UI updates instead of polling
- Look into persistent volume claims for PostgreSQL HA
<!-- >>> NEW >>> -->
- **WOPR-EDM UI**: Web interface for fleet management, device provisioning, bulk operations
- **WOPR-EDM capabilities expansion**: tofu provisioning, ansible orchestration, psql migrations, SSH key management
- **Multi-site edge deployments**: Handle devices across different networks/locations
- **Certificate-based auth** for edge agents (cert-manager integration)
<!-- >>> END NEW >>> -->

---

## 📚 Resources / Links

**Documentation:**
- Architecture doc: `~/Documents/wopr/files/TWAT_2.0_Architecture_Guide.md`
- Config system: `~/Documents/wopr/files/wopr-config-system/`
- This status: `~/Documents/wopr/STATUS.md`

**External:**
- Qwen2-VL docs: https://github.com/QwenLM/Qwen2-VL
- FastAPI docs: https://fastapi.tiangolo.com/
- Celery docs: https://docs.celeryq.dev/
<!-- >>> NEW >>> -->
- Kubernetes CRD docs: https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/
- Operator Pattern: https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
<!-- >>> END NEW >>> -->

---

## 🗂️ Phase Tracking

### Phase 0: Foundation ✅
- [x] Architecture design
- [x] Tech stack decisions
- [x] Config system implementation
- [x] Documentation started

### Phase 1: Infrastructure (IN PROGRESS)
**Config & Storage**
- [x] wopr-config-service - HTTP API
- [x] wopr-config-db - PostgreSQL schema
- [x] wopr-core library - Python client
- [ ] Deploy config service to k8s ← CURRENT
- [ ] Test config service from all hosts
- [ ] NFS mount on k8s nodes
- [ ] Directory structure: `/mnt/nas/wopr/games/`

**Database**
- [ ] PostgreSQL StatefulSet deployed
- [ ] wopr_main database schema
<!-- >>> NEW >>> -->
- [ ] wopr_edm database schema (edge device state)
<!-- >>> END NEW >>> -->
- [ ] Database migrations (Alembic)
- [ ] Backup strategy

**Message Queue**
- [ ] Redis deployed
- [ ] Celery configured
- [ ] Test task queue

<!-- >>> NEW PHASE >>> -->
### Phase 1.5: Edge Device Management (WOPR-EDM) - NEW
**Design & Planning**
- [x] Conceptualize WOPR-EDM architecture
- [ ] Define wopr_device CRD spec
- [ ] Design controller reconciliation loop
- [ ] Design edge agent polling/caching logic
- [ ] Document auth strategy (k8s API vs gateway)

**Implementation**
- [ ] Create wopr_device CRD YAML
- [ ] Build wopr-edm controller (Python + kopf or Go + controller-runtime)
- [ ] Build wopr-edge-agent (Python service)
- [ ] Containerize wopr-cam
- [ ] Deploy EDM to k8s cluster
- [ ] Bootstrap first Pi with edge agent
- [ ] Test: version update → rollback flow
- [ ] Test: disconnected operation + 72h cache
- [ ] Test: degraded state flagging

**Future Capabilities**
- [ ] OpenTofu integration
- [ ] Ansible playbook execution
- [ ] PostgreSQL remote management
- [ ] SSH key distribution
- [ ] Remote docker control
- [ ] WOPR-EDM web UI
<!-- >>> END NEW PHASE >>> -->

### Phase 2: Camera & Capture
- [ ] Hardware acquired
- [ ] Camera mounted
- [x] wopr-cam service built (now containerized) <!-- UPDATED -->
- [ ] Test captures

### Phase 3: API Layer
- [ ] wopr-api scaffolded
- [ ] Database models
- [ ] Endpoints implemented
- [ ] Deployed to k8s

### Phase 4: Vision Processing
- [ ] Ollama setup
- [ ] OpenCV implementation
- [ ] wopr-worker deployed

### Phase 5: Frontend
- [ ] wopr-web scaffolded
- [ ] UI components built
- [ ] Deployed

### Phase 6-10: (See full milestone doc)

---

## 📅 Timeline / Milestones

**Target Dates:**
- [ ] 2025-12-21: Phase 1 complete (Infrastructure)
<!-- >>> NEW >>> -->
- [ ] 2025-12-28: Phase 1.5 complete (WOPR-EDM basics)
<!-- >>> END NEW >>> -->
- [ ] 2025-12-28: Phase 2 complete (Camera working) <!-- UPDATED: adjusted for EDM -->
- [ ] 2026-01-11: Phase 3-4 complete (API + Vision)
- [ ] 2026-01-18: MVP complete (Phases 1-7)

**Actual Completion:**
- 

---

## 📖 Session Notes

**2025-12-18 - WOPR-EDM Design Session** <!-- NEW -->
- Conceptualized edge device management platform
- CRD + Controller pattern for declarative device management
- Edge agent with polling, reconciliation, health checks, rollback
- 72h config cache with graceful degradation
- Future: Full infrastructure lifecycle (tofu, ansible, psql, ssh, docker)

**2025-12-14 - Initial Setup**
- Created config system with Claude
- Decided on architecture
- Got all files packaged up
- Ready to start implementation

**[DATE] - [What you worked on]**
- 
- 
- 

---

## 🆘 Help Needed From Claude

**Next time we chat, I need help with:**
1. Deploying config service to k8s (ArgoCD vs kubectl)
2. Database schema design for wopr_main
<!-- >>> NEW >>> -->
3. **WOPR-EDM CRD spec structure** (fields, validation, status subresource)
4. **Edge agent implementation** (polling loop, docker compose management, rollback logic)
<!-- >>> END NEW >>> -->

**Questions to ask:**
- 
- 

---

## 🎓 Things I Learned

- Database-backed config is way more flexible than files
- Celery isn't as scary as it sounds
<!-- >>> NEW >>> -->
- CRD + Controller pattern is cleaner than custom APIs for cluster-managed resources
- Edge agents need thoughtful degradation strategies for offline operation
<!-- >>> END NEW >>> -->

---

## Usage Instructions

**How to update this file:**
1. Update "Last Updated" date at top
2. Move completed items from "Current Focus" to "Recently Completed"
3. Check off boxes as you complete tasks
4. Add new blockers/questions as they come up
5. Update stats (services deployed, etc.)
6. Add session notes each time you work on WOPR

**How to use with Claude:**
- Upload this file at start of conversation
- Or paste the relevant sections (Current Focus, Blockers, Next Steps)
- I'll know exactly where you are without re-explaining everything

---

## Summary of Changes (2025-12-18)

**ADDED:**
- WOPR-EDM edge device management service concept
- Phase 1.5 for WOPR-EDM implementation
- New technical decisions (CRD pattern, 72h cache, containerization)
- Edge device stats tracking
- Future enhancements for EDM capabilities
- New questions/decisions around EDM auth and bootstrap

**UPDATED:**
- Service count: 0/10 (was 0/9)
- Current focus includes EDM design tasks
- Timeline adjusted for EDM phase
- wopr-cam now containerized (managed by edge agent)
