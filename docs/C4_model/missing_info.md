# WOPR Architecture - Missing Information and Assumptions

## Executive Summary

This document catalogs all assumptions made during the C4 architecture analysis, identifies missing information, and lists open questions that require clarification from the development team or system administrators.

## Critical Missing Information

### 1. Authentication & Authorization
**Status**: Not visible in codebase

**Missing Details**:
- User authentication mechanism (OAuth, JWT, session-based?)
- Authorization model (RBAC, ABAC, attribute-based?)
- API key management for service-to-service communication
- User roles and permissions structure
- Session management strategy

**Impact**: High - Security and access control are critical

**Recommended Actions**:
- Review authentication implementation (likely in Directus or API middleware)
- Document user flows and permission matrices
- Verify security audit compliance

### 2. Database Schema Details
**Status**: Partially inferred from code

**Missing Details**:
- Complete table definitions with all columns
- Foreign key relationships and constraints
- Indexes on frequently queried columns
- Database migration history and versioning
- Partitioning strategy for large tables (playtracker)
- Archival/purging policies for old data

**Impact**: Medium - Affects performance and data integrity

**Recommended Actions**:
- Export schema from PostgreSQL
- Document all tables, relationships, and indexes
- Review query performance and optimization

### 3. Infrastructure Specifications
**Status**: Largely unknown

**Missing Details**:
- Kubernetes cluster provider (k3s, k8s, managed service)
- Node specifications (CPU, RAM, disk)
- Cluster networking plugin (Calico, Cilium, Flannel)
- Ingress controller implementation
- Certificate management (cert-manager configuration)
- Load balancer setup (MetalLB, cloud LB)
- NFS server specifications and performance characteristics

**Impact**: High - Affects capacity planning and reliability

**Recommended Actions**:
- Document infrastructure as code (Terraform, Helm charts)
- Capture node specifications and resource allocations
- Review scaling and capacity plans

### 4. CI/CD Pipeline
**Status**: Minimal evidence in code

**Missing Details**:
- Complete GitHub Actions workflows
- Build and test processes
- Deployment automation (GitOps tools like ArgoCD/Flux?)
- Container registry location and access
- Image scanning and vulnerability management
- Rollback procedures
- Blue-green or canary deployment strategies

**Impact**: Medium - Affects release velocity and reliability

**Recommended Actions**:
- Document complete CI/CD pipeline
- Review deployment procedures and approvals
- Test rollback scenarios

### 5. Observability Configuration
**Status**: Components identified, configuration unknown

**Missing Details**:
- Prometheus configuration and scrape targets
- Alert rules and thresholds
- Grafana dashboard definitions
- Log retention policies in Loki
- Trace sampling rates in Tempo
- On-call rotation and incident response procedures

**Impact**: Medium - Affects operational visibility

**Recommended Actions**:
- Export and version control dashboards
- Document alerting thresholds and escalation
- Review SLOs and SLIs

### 6. Backup and Disaster Recovery
**Status**: Partially configured (CloudNativePG backups mentioned)

**Missing Details**:
- PostgreSQL backup schedule and retention
- NFS backup strategy
- Recovery time objective (RTO) and recovery point objective (RPO)
- Disaster recovery testing schedule
- Backup restoration procedures
- Off-site backup storage

**Impact**: Critical - Data loss prevention

**Recommended Actions**:
- Document complete backup procedures
- Test restoration process
- Implement automated backup verification

### 7. Security Policies
**Status**: Minimal evidence

**Missing Details**:
- Kubernetes network policies (partial example provided)
- Pod security policies or standards
- RBAC configuration for Kubernetes
- Secrets management strategy (external vault?)
- Container image signing and verification
- Vulnerability scanning results
- Penetration testing reports

**Impact**: High - Security posture

**Recommended Actions**:
- Security audit of entire stack
- Implement least privilege access
- Regular vulnerability assessments

### 8. Camera Hardware Integration
**Status**: Physical hardware mentioned, integration unclear

**Missing Details**:
- Camera connection method (USB, network, direct)
- Camera configuration and calibration
- Hardware failover or redundancy
- Image quality settings (resolution, format, compression)
- Physical mounting specifications
- Camera replacement procedures

**Impact**: Medium - Core functionality dependency

**Recommended Actions**:
- Document hardware setup procedures
- Create camera troubleshooting guide
- Establish hardware replacement process

### 9. ML Model Management
**Status**: Service exists, model lifecycle unclear

**Missing Details**:
- Model training pipeline
- Model versioning strategy
- A/B testing or gradual rollout of new models
- Model performance monitoring
- Retraining triggers and schedules
- Model artifact storage and retrieval

**Impact**: Medium - Affects system accuracy

**Recommended Actions**:
- Document ML model lifecycle
- Implement model performance tracking
- Establish model governance policies

### 10. NFS Storage Structure and Policies
**Status**: Directory structure inferred

**Missing Details**:
- Complete directory tree and file organization
- File naming conventions (partially documented)
- Storage quota and limits
- File retention and archival policies
- Access permissions and security
- Performance characteristics (IOPS, throughput)
- Backup and replication strategy

**Impact**: Medium - Data management and performance

**Recommended Actions**:
- Document complete file organization
- Review and enforce retention policies
- Monitor storage performance

## Architecture Assumptions

### System Context Assumptions

1. **External Systems Availability**: All external systems (Directus, Loki, OpenTelemetry, Label Studio) are highly available
2. **Network Reliability**: Stable network connectivity between all components
3. **Tailscale VPN**: Provides secure access layer for all administrative tasks
4. **Domain Ownership**: `tailandtraillabs.org` is controlled by the organization
5. **User Base**: Small to medium user base (not internet-scale traffic)

### Container Architecture Assumptions

1. **Horizontal Scaling**: API and Worker services can scale horizontally without state issues
2. **Stateless Services**: Most services are stateless except databases and file storage
3. **Shared Storage**: All pods requiring file access have NFS mounted at same path
4. **Camera Singleton**: Only one camera service instance runs at a time
5. **Database Pooling**: Connection pooling handled by application or external pooler
6. **Task Idempotency**: Celery tasks can be safely retried without side effects

### Component Architecture Assumptions

1. **Directus Migration**: System migrated from Directus CMS to direct PostgreSQL access
2. **CRUD Pattern**: Standard CRUD operations sufficient for most resources
3. **Best-Effort Processing**: Background tasks continue on individual failures
4. **File Immutability**: Captured images never modified after creation
5. **Session Locking**: No concurrent modifications to same session (enforced by UI)

### Code-Level Assumptions

1. **Python Version**: Python 3.11-3.13 across all services
2. **Async Support**: Database queries can use async patterns (asyncpg available)
3. **Type Hints**: Code uses type hints for better IDE support
4. **Pydantic Validation**: All API payloads validated by Pydantic models
5. **OpenTelemetry**: Auto-instrumentation handles most tracing needs
6. **Error Handling**: Exceptions caught and logged with trace context

### Deployment Assumptions

1. **Kubernetes 1.27+**: Recent Kubernetes version with modern features
2. **Container Runtime**: containerd as runtime
3. **Rolling Updates**: Zero-downtime deployments via rolling updates
4. **Resource Limits**: All pods have requests and limits defined
5. **Health Checks**: Liveness and readiness probes on all services
6. **Cert Manager**: Automated TLS certificate management
7. **Private Network**: Cluster not directly exposed to internet

### Data Assumptions

1. **PostgreSQL Features**: UUID generation, CHECK constraints, JSONB support
2. **Database Schema**: Managed by migrations (tool unknown)
3. **Referential Integrity**: Foreign key constraints enforced
4. **Image File Sizes**: 1-5MB per image (4K camera)
5. **Session Sizes**: 50-500 images per typical session
6. **Data Retention**: No automatic purging of old data

## Open Questions

### Functional Questions

1. **Multi-Player Support**: How are multi-player games handled? Turn order? Simultaneous play?
2. **Game Rules Validation**: Does system validate moves against game rules?
3. **Computer Vision**: Is ML-based piece detection implemented? Accuracy?
4. **Replay Functionality**: Can players replay games from captured images?
5. **Statistics and Analytics**: What game statistics are tracked and displayed?

### Technical Questions

1. **Concurrent Sessions**: Maximum supported concurrent game sessions?
2. **Image Processing**: Are images processed in real-time or batch?
3. **Caching Strategy**: What caching is implemented beyond Redis?
4. **Rate Limiting**: API rate limits and throttling mechanisms?
5. **Feature Flags**: Feature flag system for gradual rollouts?

### Operational Questions

1. **SLAs**: What are the service level agreements?
2. **Uptime Requirements**: Target availability percentage?
3. **Maintenance Windows**: Scheduled maintenance procedures?
4. **Incident Response**: On-call rotation and escalation procedures?
5. **Capacity Planning**: Current usage vs. capacity metrics?

### Security Questions

1. **Data Encryption**: Encryption at rest and in transit?
2. **Audit Logging**: User action audit trail?
3. **Compliance**: Any regulatory compliance requirements (GDPR, etc.)?
4. **Penetration Testing**: Regular security assessments?
5. **Secret Rotation**: Automated secret rotation policies?

### Business Questions

1. **User Tiers**: Free vs. paid tiers with different limits?
2. **Multi-Tenancy**: Single-tenant or multi-tenant architecture?
3. **White-Label**: Support for white-label deployments?
4. **API Access**: Public API for third-party integrations?
5. **Data Ownership**: Who owns game data? Privacy policy?

## Architectural Decisions (Inferred)

### Technology Choices

1. **Python Ecosystem**: Standardized on Python for all backend services
   - **Rationale**: Developer familiarity, rich library ecosystem
   - **Tradeoffs**: Performance vs. productivity

2. **FastAPI Framework**: Modern async Python web framework
   - **Rationale**: Performance, automatic API docs, type safety
   - **Tradeoffs**: Less mature than Flask/Django

3. **Streamlit for Web UI**: Python-based web framework
   - **Rationale**: Rapid development, Python-native
   - **Tradeoffs**: Less flexible than React/Vue, limited customization

4. **PostgreSQL Database**: Relational database
   - **Rationale**: ACID compliance, mature ecosystem, JSON support
   - **Tradeoffs**: Vertical scaling limits vs. NoSQL

5. **Celery + Redis**: Distributed task queue
   - **Rationale**: Mature, Python-native, Redis multi-purpose
   - **Tradeoffs**: Complexity vs. simpler alternatives

6. **NFS for Storage**: Shared filesystem
   - **Rationale**: Simple, well-understood, ReadWriteMany support
   - **Tradeoffs**: Performance vs. object storage (S3)

7. **Kubernetes Deployment**: Container orchestration
   - **Rationale**: Industry standard, declarative config, scaling
   - **Tradeoffs**: Complexity vs. simpler deployment options

8. **Observability Stack** (Grafana, Loki, Tempo, OpenTelemetry):
   - **Rationale**: Open source, vendor-neutral, integrated
   - **Tradeoffs**: Self-hosted complexity vs. SaaS options

### Design Patterns

1. **Microservices Architecture**: Separate services for different concerns
   - **Rationale**: Independent scaling, technology flexibility
   - **Impact**: Increased operational complexity

2. **Generic CRUD Router**: Code reuse via Python generics
   - **Rationale**: Reduce boilerplate, consistency
   - **Impact**: Less flexibility for custom endpoints

3. **Best-Effort Background Tasks**: Continue processing on partial failures
   - **Rationale**: Reliability, eventual consistency
   - **Impact**: Need for error monitoring and reconciliation

4. **Direct Database Access**: Bypassing Directus for performance
   - **Rationale**: Reduce latency, simplify architecture
   - **Impact**: Lose Directus features (admin UI, versioning)

5. **Shared File Storage**: NFS mounted across pods
   - **Rationale**: Simple file sharing, atomic operations
   - **Impact**: NFS becomes single point of failure

## Recommendations for Documentation

### High Priority

1. **Security Documentation**: Complete security audit and documentation
2. **Runbooks**: Operational procedures for common scenarios
3. **Disaster Recovery Plan**: Complete DR documentation with testing schedule
4. **API Documentation**: Public API docs (OpenAPI/Swagger)
5. **Database Schema**: Complete ERD and table documentation

### Medium Priority

1. **Architecture Decision Records (ADRs)**: Document key architectural decisions
2. **Development Setup Guide**: Local development environment setup
3. **Deployment Guide**: Step-by-step deployment procedures
4. **Monitoring and Alerting**: Complete observability documentation
5. **Troubleshooting Guide**: Common issues and resolutions

### Lower Priority

1. **Performance Benchmarks**: Load testing results and capacity planning
2. **Cost Analysis**: Infrastructure cost breakdown and optimization
3. **User Guides**: End-user documentation and tutorials
4. **ML Model Documentation**: Model training and evaluation procedures
5. **Third-Party Integration Guide**: How to integrate with WOPR APIs

## Conclusion

This analysis has revealed a well-structured microservices architecture with modern observability practices. However, several critical areas lack documentation, particularly around security, disaster recovery, and operational procedures.

**Immediate Actions Recommended**:
1. Security audit and penetration testing
2. Document complete backup and disaster recovery procedures
3. Create operational runbooks for common scenarios
4. Export and version control Kubernetes manifests
5. Document database schema and relationships

**Long-term Improvements**:
1. Implement comprehensive monitoring and alerting
2. Establish SLOs and track SLI metrics
3. Create Architecture Decision Records for key choices
4. Develop comprehensive API documentation
5. Implement automated compliance and security scanning

This documentation should be treated as a living document and updated as the system evolves and additional information becomes available.