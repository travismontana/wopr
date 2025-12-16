#!/bin/bash

REPO="travismontana/wopr"

echo "🚀 Setting up WOPR project in $REPO..."
echo ""

# ============================================================================
# CREATE LABELS
# ============================================================================
echo "📋 Creating labels..."

gh label create "backend" --color "0052CC" --description "Backend service work" --repo "$REPO" --force
gh label create "frontend" --color "5319E7" --description "Frontend/UI work" --repo "$REPO" --force
gh label create "api" --color "1D76DB" --description "API endpoints and integration" --repo "$REPO" --force
gh label create "database" --color "D93F0B" --description "Database schema and operations" --repo "$REPO" --force
gh label create "storage" --color "FBCA04" --description "Storage and file management" --repo "$REPO" --force
gh label create "operations" --color "0E8A16" --description "DevOps and operational tasks" --repo "$REPO" --force
gh label create "argocd" --color "006B75" --description "ArgoCD configuration" --repo "$REPO" --force
gh label create "security" --color "D73A4A" --description "Security-related work" --repo "$REPO" --force
gh label create "observability" --color "BFD4F2" --description "Logging, monitoring, metrics" --repo "$REPO" --force
gh label create "UI" --color "C5DEF5" --description "User interface components" --repo "$REPO" --force
gh label create "images" --color "F9D0C4" --description "Image handling and processing" --repo "$REPO" --force
gh label create "image handling" --color "FEF2C0" --description "Image capture and storage" --repo "$REPO" --force
gh label create "AI/ML" --color "7057FF" --description "AI and machine learning" --repo "$REPO" --force
gh label create "computer vision" --color "8B4789" --description "Computer vision and image recognition" --repo "$REPO" --force
gh label create "infrastructure" --color "C2E0C6" --description "Infrastructure and cluster management" --repo "$REPO" --force
gh label create "distributed systems" --color "BFD4F2" --description "Multi-node and distributed architecture" --repo "$REPO" --force
gh label create "game logic" --color "E99695" --description "Game play and logic" --repo "$REPO" --force

echo "✅ Labels created"
echo ""

# ============================================================================
# CREATE MILESTONES
# ============================================================================
echo "🎯 Creating milestones..."

gh api repos/$REPO/milestones -f title="Config Management & Image Viewing" -f description="Basic infrastructure, config management, and image viewing capabilities" -f state="open"
gh api repos/$REPO/milestones -f title="Image Recognition & Change Tracking" -f description="Computer vision integration and change detection" -f state="open"
gh api repos/$REPO/milestones -f title="Multi-Node Infrastructure & Object Storage" -f description="Distributed architecture and scalable storage" -f state="open"
gh api repos/$REPO/milestones -f title="Full Game Play Integration" -f description="Complete WOPR game integration" -f state="open"

echo "✅ Milestones created"
echo ""

# ============================================================================
# MILESTONE 1: Config Management & Image Viewing
# ============================================================================
echo "📝 Creating Milestone 1 issues..."

MILESTONE1="Config Management & Image Viewing"

gh issue create --repo "$REPO" \
  --title "Design and implement database schema for config storage" \
  --body "- Design PostgreSQL schema for storing configuration data
- Include tables for game config, camera settings, and system parameters
- Add proper indexing and constraints
- Create migration scripts
- Document schema design and relationships" \
  --label "database,backend" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Setup PostgreSQL StatefulSet in Kubernetes" \
  --body "- Create Kubernetes StatefulSet manifest for PostgreSQL
- Configure persistent volume claims for data storage
- Setup proper resource limits and requests
- Add liveness and readiness probes
- Document deployment process" \
  --label "database,operations" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Build wopr-api service with FastAPI/Flask" \
  --body "- Decide framework:  FastAPI vs Flask for wopr-api backend
- Bootstrap REST API project structure
- Implement base application wiring and config
- Setup proper error handling and logging" \
  --label "backend,api" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Implement config CRUD endpoints in wopr-api" \
  --body "- Design and add REST endpoints for CRUD operations on configuration data
- Integrate with DB schema and validation logic
- Ensure input/output is well-documented (OpenAPI)
- Add proper authentication and authorization
- Write unit tests for endpoints" \
  --label "api,backend" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Add health/readiness endpoints to wopr-api" \
  --body "- Implement /health and /readiness endpoints in API
- Add checks for DB, storage, and dependent service connectivity
- Ensure endpoints are suitable for Kubernetes liveness/readiness probes
- Document endpoint behavior and expected responses" \
  --label "api,operations" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Setup basic image storage (local PV or NFS)" \
  --body "- Provision local persistent volume or NFS for initial image storage
- Document storage path and access policies
- Integrate with wopr-api and wopr-cam for image ingest
- Plan migration path for later MinIO upgrade
- Setup proper permissions and security" \
  --label "storage,operations" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Update wopr-cam service to POST images to storage" \
  --body "- Update wopr-cam service code to support POSTing images directly to the configured storage target
- Ensure compatibility with local PV or NFS storage implementation
- Add support for configurable endpoint URL
- Add error handling and retry logic for image uploads
- Implement proper logging for upload operations" \
  --label "image handling,backend" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Build wopr-webui frontend (framework selection)" \
  --body "- Select and set up frontend framework for wopr-webui (consider React, Vue, Svelte, etc.)
- Bootstrap project repo with initial structure
- Setup build pipeline and development environment
- Integrate with API endpoints for config and image modules as they become available
- Configure routing and state management" \
  --label "frontend" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Implement config viewer in webui" \
  --body "- Build a webui component to display the current configuration in YAML or table form
- Fetch and render config from wopr-api endpoints
- Ensure responsive UI and accessible formatting
- Add loading states and error handling
- Support different config categories/sections" \
  --label "frontend,UI" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Implement config editor in webui (YAML-style)" \
  --body "- Add an editable YAML code view to the webui for configuration
- Integrate update functionality via API
- Provide validation feedback and a safe update/revert flow
- Add syntax highlighting for YAML
- Implement confirmation dialogs for critical changes" \
  --label "frontend,UI" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Implement image gallery/viewer in webui" \
  --body "- Create an image gallery page/component for browsing uploaded images
- Support grid and single-image views
- Enable filtering/sorting by metadata (timestamp, cam, etc)
- Add pagination for large image sets
- Implement image zoom and navigation controls" \
  --label "frontend,images,UI" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Create ArgoCD Applications for wopr-db, wopr-api, wopr-webui" \
  --body "- Define ArgoCD Application manifests for wopr-db, wopr-api, and wopr-webui
- Configure sync policies and health checks
- Deploy Applications to ArgoCD and verify successful deployment
- Setup proper RBAC and namespace isolation
- Document ArgoCD application structure" \
  --label "argocd,operations" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Setup secrets management for database credentials" \
  --body "- Choose secrets management solution (Sealed Secrets, External Secrets, Vault, etc.)
- Implement secret creation and rotation for database credentials
- Update services to consume secrets from the chosen solution
- Document the secrets management workflow
- Add monitoring for secret expiration" \
  --label "security,operations" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Add basic logging to all services (JSON structured logs)" \
  --body "- Implement JSON structured logging in wopr-cam, wopr-api, and wopr-webui
- Ensure consistent log format across all services
- Include relevant context (request IDs, timestamps, service names)
- Add appropriate log levels (DEBUG, INFO, WARN, ERROR)
- Document logging standards and best practices" \
  --label "observability,backend" \
  --milestone "$MILESTONE1"

gh issue create --repo "$REPO" \
  --title "Configure log shipping to Loki" \
  --body "- Deploy Loki to Kubernetes cluster (if not already present)
- Configure log collection (Promtail, Fluentd, or similar)
- Ensure all wopr services' logs are shipped to Loki
- Verify logs are queryable in Grafana
- Add retention policies and storage optimization
- Document log querying patterns" \
  --label "observability,operations" \
  --milestone "$MILESTONE1"

echo "✅ Milestone 1 issues created"
echo ""

# ============================================================================
# MILESTONE 2: Image Recognition & Change Tracking
# ============================================================================
echo "📝 Creating Milestone 2 issues..."

MILESTONE2="Image Recognition & Change Tracking"

gh issue create --repo "$REPO" \
  --title "Research and select computer vision framework (OpenCV, TensorFlow, etc. )" \
  --body "- Evaluate computer vision frameworks for image analysis needs
- Consider OpenCV, TensorFlow, PyTorch, or specialized libraries
- Assess performance, ease of integration, and licensing
- Document framework selection decision and rationale
- Create proof-of-concept with selected framework" \
  --label "AI/ML,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Build wopr-vision service for image analysis" \
  --body "- Create new microservice for computer vision processing
- Implement service skeleton with proper architecture
- Setup message queue or API integration with wopr-api
- Add health checks and monitoring endpoints
- Document service API and deployment requirements" \
  --label "backend,AI/ML,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Implement basic image diff/change detection algorithm" \
  --body "- Develop algorithm to detect changes between sequential images
- Implement pixel-based difference detection
- Add configurable sensitivity thresholds
- Optimize for performance with large images
- Create unit tests with sample images
- Document algorithm behavior and parameters" \
  --label "AI/ML,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Add OCR capability for reading game state from images" \
  --body "- Integrate OCR library (Tesseract, EasyOCR, etc.)
- Train or configure for game-specific text recognition
- Implement text extraction from game screen regions
- Add preprocessing for improved OCR accuracy
- Handle different font sizes and styles
- Test with various game states and lighting conditions" \
  --label "AI/ML,computer vision,game logic" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Extend database schema for vision results and detected changes" \
  --body "- Design tables for storing image analysis results
- Add schema for change detection metadata
- Include fields for OCR text, change regions, confidence scores
- Create indexes for efficient querying
- Write migration scripts
- Update API models to reflect new schema" \
  --label "database,backend" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Implement vision API endpoints in wopr-api" \
  --body "- Create REST endpoints for triggering image analysis
- Add endpoints for retrieving vision results
- Implement job queue for async processing
- Return analysis results with confidence scores
- Add filtering and pagination for results
- Document API with OpenAPI/Swagger" \
  --label "api,backend,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Integrate wopr-vision processing into image upload pipeline" \
  --body "- Connect image upload flow to wopr-vision service
- Trigger automatic analysis on new images
- Implement async job processing with status tracking
- Add retry logic for failed analyses
- Store results back to database
- Implement notification system for detected changes" \
  --label "backend,computer vision,image handling" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Build change history viewer in webui" \
  --body "- Create UI component to display detected changes over time
- Show timeline of changes with thumbnails
- Implement side-by-side comparison view
- Add filtering by change type and confidence
- Include visual highlighting of change regions
- Add export functionality for change reports" \
  --label "frontend,UI,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Add visualization overlays for detected changes in webui" \
  --body "- Implement overlay rendering on images to highlight changes
- Use bounding boxes or heatmaps for change regions
- Add toggle controls to show/hide overlays
- Color-code by change type or confidence level
- Support zoom and pan for detailed inspection
- Make overlays responsive and performant" \
  --label "frontend,UI,images,computer vision" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Setup Prometheus metrics for vision service performance" \
  --body "- Instrument wopr-vision with Prometheus client
- Add metrics for processing time, queue depth, success/failure rates
- Track resource usage (CPU, memory, GPU if applicable)
- Create Prometheus scrape config for wopr-vision
- Build Grafana dashboards for vision metrics
- Setup alerts for performance degradation" \
  --label "observability,operations,AI/ML" \
  --milestone "$MILESTONE2"

gh issue create --repo "$REPO" \
  --title "Add alerting for significant detected changes" \
  --body "- Define thresholds for 'significant' changes
- Implement alerting mechanism (email, Slack, webhooks, etc.)
- Add configurable alert rules and recipients
- Include change details and image links in alerts
- Implement alert throttling to prevent spam
- Add alert management UI in webui
- Document alert configuration" \
  --label "observability,operations,computer vision" \
  --milestone "$MILESTONE2"

echo "✅ Milestone 2 issues created"
echo ""

# ============================================================================
# MILESTONE 3: Multi-Node Infrastructure & Object Storage
# ============================================================================
echo "📝 Creating Milestone 3 issues..."

MILESTONE3="Multi-Node Infrastructure & Object Storage"

gh issue create --repo "$REPO" \
  --title "Deploy MinIO for distributed object storage" \
  --body "- Install MinIO in Kubernetes cluster
- Configure distributed mode for high availability
- Setup persistent volumes for MinIO storage
- Configure access credentials and policies
- Test basic object operations (put, get, delete)
- Document MinIO deployment and configuration" \
  --label "storage,infrastructure,operations" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Migrate image storage from local PV/NFS to MinIO" \
  --body "- Create migration script to move existing images to MinIO
- Update wopr-api to use MinIO S3-compatible API
- Update wopr-cam to upload directly to MinIO
- Implement fallback mechanism during migration
- Verify all images are accessible post-migration
- Decommission old storage after successful migration
- Update documentation" \
  --label "storage,backend,operations" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Implement image metadata indexing in database" \
  --body "- Design schema for image metadata (size, format, location, timestamps, etc.)
- Create indexes for efficient metadata queries
- Implement automatic metadata extraction on upload
- Add metadata update endpoints to API
- Support bulk metadata operations
- Add metadata search and filtering capabilities" \
  --label "database,backend,images" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Add support for multiple wopr-cam instances" \
  --body "- Update architecture to support multiple camera instances
- Implement unique camera identification and registration
- Add camera management endpoints to API
- Update database schema for multi-camera support
- Implement camera selection in webui
- Add camera health monitoring
- Document multi-camera deployment" \
  --label "backend,infrastructure,image handling" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Implement load balancing for wopr-api service" \
  --body "- Configure Kubernetes Service with load balancing
- Scale wopr-api to multiple replicas
- Implement proper session affinity if needed
- Add health checks for all replicas
- Test failover scenarios
- Monitor load distribution across replicas
- Document scaling procedures" \
  --label "infrastructure,operations,api" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Setup Redis for caching and session management" \
  --body "- Deploy Redis to Kubernetes cluster
- Configure Redis for high availability (Sentinel or Cluster mode)
- Implement caching layer in wopr-api for frequent queries
- Add session management using Redis
- Configure proper TTLs and eviction policies
- Monitor Redis performance and memory usage
- Document Redis usage patterns" \
  --label "infrastructure,operations,backend" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Implement distributed job queue for vision processing" \
  --body "- Choose and deploy job queue system (Celery, RabbitMQ, Redis Queue, etc.)
- Configure workers for parallel vision processing
- Implement job submission from wopr-api
- Add job status tracking and result retrieval
- Implement job retry and failure handling
- Monitor queue depth and worker health
- Document job queue architecture" \
  --label "infrastructure,backend,AI/ML,distributed systems" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Add horizontal pod autoscaling for vision workers" \
  --body "- Configure HPA for wopr-vision service
- Define CPU/memory thresholds for scaling
- Set min/max replica counts
- Test autoscaling behavior under load
- Monitor scaling events and effectiveness
- Tune autoscaling parameters
- Document autoscaling configuration" \
  --label "infrastructure,operations,AI/ML" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Implement multi-region support (if applicable)" \
  --body "- Design architecture for multi-region deployment
- Implement region-aware routing
- Setup cross-region replication for critical data
- Handle latency and consistency challenges
- Test failover between regions
- Document multi-region deployment procedures
- (Mark as optional/future if not immediately needed)" \
  --label "infrastructure,distributed systems,operations" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Setup distributed tracing with Jaeger or Zipkin" \
  --body "- Deploy distributed tracing backend (Jaeger or Zipkin)
- Instrument all services with tracing libraries
- Implement trace context propagation across services
- Add custom spans for key operations
- Integrate traces with logs (trace IDs in logs)
- Build dashboards for trace analysis
- Document tracing practices and debugging workflows" \
  --label "observability,operations,distributed systems" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Add resource quotas and limits for all services" \
  --body "- Define CPU and memory requirements for each service
- Set resource requests and limits in Kubernetes manifests
- Configure ResourceQuotas for namespaces
- Test services under resource constraints
- Monitor resource usage and adjust limits as needed
- Implement pod disruption budgets
- Document resource allocation strategy" \
  --label "infrastructure,operations" \
  --milestone "$MILESTONE3"

gh issue create --repo "$REPO" \
  --title "Implement backup and disaster recovery procedures" \
  --body "- Design backup strategy for database and object storage
- Implement automated database backups
- Configure MinIO backup/replication
- Create disaster recovery runbooks
- Test restore procedures regularly
- Setup monitoring for backup success/failure
- Document backup and recovery procedures" \
  --label "operations,security,database,storage" \
  --milestone "$MILESTONE3"

echo "✅ Milestone 3 issues created"
echo ""

# ============================================================================
# MILESTONE 4: Full Game Play Integration
# ============================================================================
echo "📝 Creating Milestone 4 issues..."

MILESTONE4="Full Game Play Integration"

gh issue create --repo "$REPO" \
  --title "Design game state machine and rule engine" \
  --body "- Model WOPR game as a state machine
- Define all possible game states and transitions
- Design rule engine for evaluating game moves
- Document game logic and win conditions
- Create test cases for all game scenarios
- Implement validation for game state transitions" \
  --label "game logic,backend" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Implement game state tracking in database" \
  --body "- Extend database schema for game state storage
- Track current game state, move history, and player info
- Implement state versioning for rollback capability
- Add indexes for efficient game queries
- Create migration scripts
- Document game state data model" \
  --label "database,backend,game logic" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Build game move detection from vision analysis" \
  --body "- Implement logic to interpret vision results as game moves
- Map detected changes to game actions
- Handle ambiguous or invalid moves
- Add confidence scoring for move detection
- Implement move validation against game rules
- Create test suite with sample game scenarios" \
  --label "AI/ML,computer vision,game logic,backend" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Implement AI opponent logic (basic strategy)" \
  --body "- Design AI opponent strategy for WOPR game
- Implement basic move selection algorithm
- Add difficulty levels (easy, medium, hard)
- Consider minimax, MCTS, or other game AI techniques
- Test AI against known game scenarios
- Tune AI performance and response time
- Document AI strategy and decision-making" \
  --label "AI/ML,game logic,backend" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Add game control endpoints to wopr-api" \
  --body "- Create API endpoints for starting/stopping games
- Add endpoints for making moves and getting game state
- Implement move validation in API layer
- Add game history and replay endpoints
- Document game API with OpenAPI/Swagger
- Implement proper authentication for game controls" \
  --label "api,backend,game logic" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Build game play interface in webui" \
  --body "- Create interactive game board UI component
- Implement move input controls
- Display current game state visually
- Show move history and analysis
- Add game controls (start, pause, reset)
- Implement real-time updates (WebSocket or polling)
- Make UI responsive and accessible" \
  --label "frontend,UI,game logic" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Implement real-time game state updates (WebSocket or SSE)" \
  --body "- Choose real-time update mechanism (WebSocket or Server-Sent Events)
- Implement server-side push for game state changes
- Update webui to consume real-time updates
- Handle connection failures and reconnection
- Optimize update frequency and payload size
- Test with multiple concurrent games
- Document real-time architecture" \
  --label "backend,frontend,infrastructure,game logic" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Add game history and replay functionality" \
  --body "- Store complete game history in database
- Implement replay API endpoints
- Build replay UI with step-through controls
- Add speed controls for replay
- Support exporting games in standard formats
- Implement game analysis and statistics
- Add sharing capabilities for interesting games" \
  --label "backend,frontend,game logic,database" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Implement game analytics and statistics tracking" \
  --body "- Design analytics schema for game metrics
- Track win/loss rates, move patterns, game duration
- Implement analytics API endpoints
- Build analytics dashboard in webui
- Add visualizations for game statistics
- Support filtering by time period, opponent, etc.
- Export analytics data for external analysis" \
  --label "backend,frontend,database,game logic,observability" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Build admin panel for game configuration and monitoring" \
  --body "- Create admin section in webui
- Add game configuration management
- Implement system health monitoring dashboard
- Add user/game management interfaces
- Include log viewer and troubleshooting tools
- Implement role-based access control for admin features
- Document admin capabilities and workflows" \
  --label "frontend,UI,operations,security" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Add comprehensive API documentation (OpenAPI/Swagger UI)" \
  --body "- Generate OpenAPI 3.0 spec for all API endpoints
- Deploy Swagger UI for interactive API docs
- Add detailed descriptions and examples for all endpoints
- Document authentication and authorization
- Include error codes and troubleshooting guide
- Add code samples for common API operations
- Keep documentation in sync with code" \
  --label "api,documentation" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Implement end-to-end integration tests" \
  --body "- Design E2E test scenarios covering full workflows
- Implement automated tests using appropriate framework
- Test complete game play scenarios
- Test multi-camera and multi-user scenarios
- Add CI/CD integration for E2E tests
- Setup test environment isolation
- Document test coverage and procedures" \
  --label "operations,backend,frontend" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Performance testing and optimization" \
  --body "- Conduct load testing on all services
- Identify performance bottlenecks
- Optimize database queries and indexes
- Tune caching strategies
- Optimize image processing pipelines
- Test system under peak load conditions
- Document performance characteristics and limits
- Create performance benchmarks" \
  --label "operations,backend,observability" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Security audit and hardening" \
  --body "- Conduct security review of all services
- Implement authentication and authorization consistently
- Add rate limiting and DDoS protection
- Review and secure all API endpoints
- Implement input validation and sanitization
- Setup security scanning in CI/CD
- Document security practices and policies
- Address any identified vulnerabilities" \
  --label "security,operations" \
  --milestone "$MILESTONE4"

gh issue create --repo "$REPO" \
  --title "Create comprehensive project documentation" \
  --body "- Write architecture overview and design docs
- Document deployment procedures
- Create user guides for webui
- Write API integration guides
- Document troubleshooting procedures
- Create contribution guidelines
- Add code of conduct
- Setup documentation site (GitHub Pages, Read the Docs, etc. )" \
  --label "documentation" \
  --milestone "$MILESTONE4"

echo "✅ Milestone 4 issues created"
echo ""

echo "🎉 All done! Your WOPR project is fully set up with:"
echo "   - 17 labels"
echo "   - 4 milestones"
echo "   - 15 issues in Milestone 1"
echo "   - 11 issues in Milestone 2"
echo "   - 12 issues in Milestone 3"
echo "   - 15 issues in Milestone 4"
echo "   Total: 53 issues"
echo ""
echo "Visit your repository at:  https://github.com/$REPO"
