# C4 Model: System Context Diagram

## WOPR - Wargaming Oversight & Position Recognition

```mermaid
C4Context
    title System Context Diagram for WOPR

    Person(player, "Game Player", "Tabletop wargame player who wants to track game state")
    Person(admin, "System Administrator", "Manages WOPR infrastructure and configurations")
    
    System(wopr, "WOPR System", "Tracks tabletop game state through computer vision, analyzes images, detects game pieces, and validates moves")
    
    System_Ext(directus, "Directus CMS", "Content management system for configuration and data storage")
    System_Ext(postgres, "PostgreSQL Database", "Stores game data, sessions, plays, and configuration")
    System_Ext(nfs, "NFS Storage", "Network file storage for captured images")
    System_Ext(loki, "Loki", "Log aggregation system for observability")
    System_Ext(otel, "OpenTelemetry Collector", "Collects traces and metrics for monitoring")
    System_Ext(redis, "Redis", "Task queue backend for Celery")
    System_Ext(labelstudio, "Label Studio", "Image annotation and ML training platform")
    
    Rel(player, wopr, "Captures game images, views game state", "HTTPS")
    Rel(admin, wopr, "Configures system, monitors health", "HTTPS")
    
    Rel(wopr, directus, "Reads configuration, manages content", "HTTPS/API")
    Rel(wopr, postgres, "Stores and retrieves game data", "PostgreSQL Protocol")
    Rel(wopr, nfs, "Stores captured images", "NFS Protocol")
    Rel(wopr, loki, "Sends logs", "HTTP")
    Rel(wopr, otel, "Sends traces and metrics", "OTLP")
    Rel(wopr, redis, "Enqueues background tasks", "Redis Protocol")
    Rel(wopr, labelstudio, "Exports images for annotation", "API")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

## Description

The WOPR (Wargaming Oversight & Position Recognition) system is a computer vision-based application that tracks the state of tabletop wargames. The system context shows:

### Actors
- **Game Players**: Primary users who capture overhead images of their game boards through a web interface
- **System Administrators**: Manage the WOPR infrastructure, configurations, and monitoring

### WOPR System
The core system that provides:
- Image capture from overhead cameras
- Computer vision analysis of game pieces
- Game state tracking and validation
- Session and play management
- Web-based user interface

### External Systems

**Data Storage & Management:**
- **Directus CMS**: Provides content management and API for configuration data
- **PostgreSQL Database**: Primary data store for games, sessions, plays, players, and system configuration
- **NFS Storage**: Centralized file storage for captured game board images

**Observability & Monitoring:**
- **Loki**: Log aggregation for centralized logging across all services
- **OpenTelemetry Collector**: Collects distributed traces and metrics for system observability

**Task Processing:**
- **Redis**: Message broker backend for Celery task queue, handles asynchronous jobs like image archiving

**Machine Learning:**
- **Label Studio**: External platform for image annotation and training ML models for game piece detection

## Assumptions

1. **Network connectivity**: All external systems are accessible via network (local or cloud)
2. **Authentication**: Directus handles user authentication (implementation details not visible in code)
3. **Camera hardware**: Physical camera devices (EMEET SmartCam C960 4K mentioned) connected to system
4. **Deployment environment**: System appears designed for Kubernetes deployment based on references to k8s probes
5. **Domain**: System accessible via `tailandtraillabs.org` domain

## Key Interfaces

- **HTTPS/Web**: User-facing interfaces for game interaction
- **PostgreSQL Protocol**: Database connections for data persistence
- **NFS Protocol**: File system access for image storage
- **HTTP/OTLP**: Observability data transmission
- **Redis Protocol**: Task queue communication

## External Dependencies

The system has significant external dependencies on:
- Database availability (PostgreSQL)
- File storage (NFS)
- Observability infrastructure (Loki, OpenTelemetry)
- Task queue (Redis)
- Content management (Directus)