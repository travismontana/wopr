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

/*
 * Core config file
 * OS Env variables needed:
 * WOPR_ENVIRONMENT
 * WOPR_API_URL
 * 
 * 1. Get the environment variable
 * 2. use those to grab the main config
 *   ${WOPR_API_URL}/api/v2/config/all
 *   That retuns a json
 * 3. exports woprconfig 
 */

export interface WoprConfig {}