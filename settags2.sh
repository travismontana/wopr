#!/usr/bin/env bash
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

# scripts/apply-version-patches.sh

set -euo pipefail

# Create temp patch file
PATCH_FILE=$(mktemp)

cat > "$PATCH_FILE" << 'ENDPATCH'
--- a/wopr-cam/app.py
+++ b/wopr-cam/app.py
@@ -6,6 +6,7 @@
 from flask import Flask, jsonify, request
 from wopr.config import init_config, get_str, get_int
 from wopr.storage import imagefilename
+from wopr.version import __version__, version_info
 import cv2
 
 app = Flask(__name__)
@@ -13,6 +14,18 @@ init_config()
 
 @app.route('/health', methods=['GET'])
 def health():
-    return jsonify({'status': 'healthy'})
+    """Health check endpoint with version info."""
+    return jsonify({
+        'status': 'healthy',
+        'service': 'wopr-cam',
+        'version': version_info()
+    })
+
+@app.route('/version', methods=['GET'])
+def version():
+    """Version endpoint."""
+    return jsonify(version_info())
 
 @app.route('/capture', methods=['POST'])
 def capture():
@@ -40,5 +53,6 @@ def capture():
         return jsonify({'status': 'error'}), 500
 
 if __name__ == '__main__':
+    print(f"Starting WOPR Camera Service v{__version__}")
     app.run(host='0.0.0.0', port=5000)
--- a/wopr-api/app.py
+++ b/wopr-api/app.py
@@ -6,11 +6,14 @@
 from fastapi import FastAPI
 from wopr.config import init_config
+from wopr.version import __version__, version_info
 
 init_config()
 
 app = FastAPI(
     title="WOPR API",
+    version=__version__,
     description="Wargaming Oversight & Position Recognition Backend API"
 )
 
@@ -18,7 +21,17 @@ app = FastAPI(
 async def health():
     """Health check endpoint."""
-    return {"status": "healthy"}
+    return {
+        "status": "healthy",
+        "service": "wopr-api",
+        "version": version_info()
+    }
+
+@app.get("/version")
+async def version():
+    """Detailed version information."""
+    return version_info()
 
 @app.post("/games")
 async def create_game():
ENDPATCH

echo "Applying version patches..."
patch -p1 < "$PATCH_FILE"

rm "$PATCH_FILE"

echo "Done. Review with: git diff"
