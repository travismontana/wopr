# WOPR System Context Diagram

This diagram shows the WOPR system in its environment, including external users and systems.

```mermaid
C4Context
    title System Context Diagram - WOPR System

    Person(player, "Tabletop Gamer", "Uses WOPR to track game state")
    Person(admin, "System Administrator", "Manages WOPR infrastructure")
    
    System(wopr, "WOPR System", "Tracks tabletop game state through computer vision, validates moves, maintains game history")
    
    System_Ext(camera, "Physical Camera", "EMEET SmartCam C960 4K / IMX477 Camera Module")
    System_Ext(nas, "NFS Storage", "Synology NAS (danas.hangar.bpfx.org)")
    System_Ext(ollama, "Ollama AI Service", "Vision LLM (Qwen2-VL) at groth.abode")
    System_Ext(homeassistant, "Home Assistant", "Controls lighting conditions")
    System_Ext(otel, "OpenTelemetry Collector", "Tempo/Loki/Grafana monitoring stack")
    
    Rel(player, wopr, "Captures game images, views analysis", "HTTPS")
    Rel(admin, wopr, "Manages configuration, models, system", "HTTPS")
    Rel(wopr, camera, "Triggers captures", "HTTP/5000")
    Rel(wopr, nas, "Stores/retrieves images", "NFS v3")
    Rel(wopr, ollama, "Sends images for AI analysis", "HTTP/11434")
    Rel(wopr, homeassistant, "Controls lighting", "HTTP/8123")
    Rel(wopr, otel, "Sends traces and logs", "OTLP/HTTP")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")