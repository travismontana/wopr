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

# Issue: Python module standardization
gh issue create --repo travismontana/wopr \
  --milestone "Config Management & Image Viewing" \
  --title "Standardize Python project structure (pyproject.toml, semantic versioning)" \
  --body "**Description:**
Establish standardized Python project structure for all WOPR modules.

**Tasks:**
- Create pyproject.toml for wopr_config module
- Implement semantic versioning (0.1.0, 0.2.0, etc.)
- Add project metadata (dependencies, author, license)
- Setup proper package structure
- Document version bumping process

**Acceptance Criteria:**
- wopr_config has valid pyproject.toml
- Version number properly defined
- Can build wheel/sdist
- Module follows PEP standards"

# Issue: Git+https distribution
gh issue create --repo travismontana/wopr \
  --milestone "Config Management & Image Viewing" \
  --title "Setup wopr-config module git+https distribution with version pinning" \
  --body "**Description:**
Enable distributed services to install wopr_config module via git+https with proper version control.

**Tasks:**
- Test git+https pip install from GitHub
- Document version pinning strategies (tag, commit, branch)
- Create git tags for releases (v0.1.0, v0.2.0)
- Update service requirements.txt to use git+https
- Document update process for services

**Example Usage:**
\`\`\`bash
pip install git+https://github.com/travismontana/wopr.git@v0.1.0#subdirectory=pymod/wopr_config
\`\`\`

**Acceptance Criteria:**
- Services can pip install wopr_config from git
- Version pinning works correctly
- Update process documented"

# Issue: Database migrations
gh issue create --repo travismontana/wopr \
  --milestone "Config Management & Image Viewing" \
  --title "Implement database migration system with Alembic" \
  --body "**Description:**
Setup Alembic for database schema migrations to enable safe schema evolution.

**Tasks:**
- Install and configure Alembic
- Create initial migration from current schema
- Document migration workflow (create, upgrade, downgrade)
- Integrate migrations into deployment process
- Add migration health checks

**Acceptance Criteria:**
- Alembic configured and working
- Initial migration created
- Can upgrade/downgrade schema
- Documented process for creating new migrations
- Migrations run automatically on deployment"
