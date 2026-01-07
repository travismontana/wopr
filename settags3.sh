# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
