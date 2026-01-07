/**
 * Copyright 2026 Bob Bomar
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// src/components/wip.tsx

export default function WorkInProgress() {
  return (
    <article className="page wip-page">
      <div className="wip-content">
        <img 
          src="/assets/construction.gif" 
          alt="Under construction"
          className="wip-gif"
        />
        <h1>Work in Progress</h1>
        <p className="wip-message">
          This feature is currently under construction.
          <br />
          Check back soon!
        </p>
      </div>
    </article>
  );
}
