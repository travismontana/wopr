/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * TypeScript type definitions.
 */

export interface User {
  id: string
  username: string
  email: string
  role: string
  created_at: string
  last_login: string | null
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface Camera {
  id: string
  name: string
  device_id: string
  service_url: string
  status: string
  capabilities: Record<string, any> | null
  metadata: Record<string, any> | null
  created_at: string
  updated_at: string
  last_heartbeat: string | null
}

export interface Game {
  id: string
  game_type: string
  display_name: string
  description: string | null
  ruleset_version: string | null
  piece_definitions: Record<string, any> | null
  metadata: Record<string, any> | null
  created_at: string
  updated_at: string
}

export interface GameInstance {
  id: string
  game_id: string
  created_by: string | null
  status: string
  player_count: number | null
  player_names: string[] | null
  started_at: string | null
  completed_at: string | null
  metadata: Record<string, any> | null
  created_at: string
  updated_at: string
}

export interface GameState {
  id: string
  game_instance_id: string
  image_id: string | null
  round_number: number
  state_snapshot: Record<string, any> | null
  ai_detected_state: Record<string, any> | null
  user_confirmed_state: Record<string, any> | null
  confirmation_status: string
  confirmed_by: string | null
  confirmed_at: string | null
  changes_from_previous: Record<string, any> | null
  rule_violations: Record<string, any> | null
  metadata: Record<string, any> | null
  created_at: string
}

export interface Image {
  id: string
  filename: string
  file_path: string
  thumbnail_path: string | null
  game_instance_id: string | null
  camera_id: string | null
  camera_session_id: string | null
  captured_by: string | null
  subject: string | null
  width: number | null
  height: number | null
  format: string | null
  size_bytes: number | null
  analysis_status: string
  analysis_started_at: string | null
  analysis_completed_at: string | null
  analysis_result: Record<string, any> | null
  is_training_data: boolean
  training_labels: Record<string, any> | null
  augmented_from: string | null
  metadata: Record<string, any> | null
  created_at: string
  updated_at: string
}

export interface HealthResponse {
  status: string
  timestamp: string
  version: string
}

export interface ReadyResponse {
  ready: boolean
  database: string
  config_service: string
  redis: string
  timestamp: string
}

export interface ApiError {
  error: string
  detail?: string
  timestamp: string
}
