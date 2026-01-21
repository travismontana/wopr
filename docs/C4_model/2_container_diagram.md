
```markdown name=02-container-diagram.md
# WOPR Container Diagram

This diagram breaks down the WOPR system into its main containers (applications, services, databases).

```mermaid
C4Container
    title Container Diagram - WOPR System

    Person(user, "User", "Tabletop gamer or admin")
    
    System_Boundary(wopr, "WOPR System") {
        Container(web, "wopr-web", "Streamlit/Python", "Web UI for game management and ML image capture")
        Container(api, "wopr-api", "FastAPI/Python", "REST API orchestrating all services")
        Container(cam, "wopr-cam", "FastAPI/Python", "Camera control service (Raspberry Pi)")
        Container(model, "wopr-model", "FastAPI/Python", "ML model management service")
        Container(directus, "wopr-directus", "Directus CMS", "Headless CMS for data management")
        Container(db, "PostgreSQL", "CNPG Cluster", "Game data, ML metadata, pieces")
        Container(configdb, "Config PostgreSQL", "PostgreSQL", "Configuration key-value store")
        Container(thumbor, "wopr-thumbor", "Thumbor/Python", "Image processing and resizing")
        Container(imgproxy, "wopr-imgproxy", "imgproxy/Go", "Alternative image proxy")
        Container(filebrowser, "wopr-filebrowser", "File Browser", "Web-based file management UI")
        Container(heimdall, "wopr-heimdall", "Heimdall", "Application dashboard")
        Container(labelstudio, "wopr-labelstudio", "Label Studio", "ML data annotation platform")
    }
    
    System_Ext(camera_hw, "Camera Hardware", "Physical camera")
    System_Ext(nfs, "NFS Storage", "Image and model storage")
    System_Ext(ollama_ext, "Ollama", "Vision AI")
    System_Ext(monitoring, "Monitoring", "Observability stack")
    
    Rel(user, web, "Uses", "HTTPS/8501")
    Rel(user, heimdall, "Accesses dashboard", "HTTPS")
    Rel(web, api, "Makes API calls", "HTTPS/JSON")
    Rel(api, cam, "Triggers capture", "HTTP/5000")
    Rel(api, model, "Manages models", "HTTP/8000")
    Rel(api, db, "Reads/writes data", "PostgreSQL/5432")
    Rel(api, configdb, "Fetches config", "PostgreSQL/5432")
    Rel(api, directus, "CRUD operations", "HTTP/8055")
    Rel(cam, camera_hw, "Captures images", "picamera2/v4l2")
    Rel(api, ollama_ext, "Sends for inference", "HTTP/11434")
    Rel(web, thumbor, "Requests thumbnails", "HTTP/8888")
    Rel(web, imgproxy, "Requests resized images", "HTTP")
    Rel(filebrowser, nfs, "Browses files", "NFS")
    Rel(labelstudio, nfs, "Accesses training data", "NFS")
    Rel(api, nfs, "Stores images", "NFS v3")
    Rel(cam, nfs, "Saves captures", "NFS v3")
    Rel(api, monitoring, "Sends telemetry", "OTLP")
    Rel(cam, monitoring, "Sends telemetry", "OTLP")
    
    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")