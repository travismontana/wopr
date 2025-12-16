cd ~/local/wopr

# For config-service
cat > /tmp/config-service-version.patch << 'EOF'
--- a/systems/wopr-config-system/config-service/app.py
+++ b/systems/wopr-config-system/config-service/app.py
@@ -8,6 +8,7 @@
 from typing import Optional, Any, Dict, List
 from contextlib import asynccontextmanager
 import yaml
+from wopr.version import __version__, version_info
 
 # Database configuration
 DB_CONFIG = {
@@ -46,7 +47,8 @@ async def lifespan(app: FastAPI):
 
 app = FastAPI(
     title="WOPR Configuration Service",
-    description="Centralized configuration management for WOPR services",
+    version=__version__,
+    description="Centralized configuration management for WOPR services",
     lifespan=lifespan
 )
 
@@ -54,7 +56,12 @@ app = FastAPI(
 @app.get("/health")
 async def health():
     """Health check endpoint"""
-    return {"status": "healthy", "service": "config-service"}
+    return {
+        "status": "healthy",
+        "service": "wopr-config_service",
+        "version": version_info()
+    }
+
 
 class ConfigUpdate(BaseModel):
     """Model for configuration updates"""
EOF

patch -p1 < /tmp/config-service-version.patch
