/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * API client with authentication.
 */

/// <reference types="vite/client" />    <-- ADD THIS LINE

import axios, { type AxiosError } from 'axios'
/// <reference types="vite/client" />
import type {
  User,
  LoginRequest,
  TokenResponse,
  Camera,
  Game,
  GameInstance,
  GameState,
  Image,
  HealthResponse,
  ReadyResponse,
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('wopr_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('wopr_token')
      localStorage.removeItem('wopr_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ===== AUTH =====
export const authApi = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>('/api/v1/auth/login', credentials)
    return data
  },

  register: async (credentials: LoginRequest & { email: string }): Promise<User> => {
    const { data } = await api.post<User>('/api/v1/auth/register', credentials)
    return data
  },

  me: async (): Promise<User> => {
    const { data } = await api.get<User>('/api/v1/auth/me')
    return data
  },
}

// ===== HEALTH =====
export const healthApi = {
  health: async (): Promise<HealthResponse> => {
    const { data } = await api.get<HealthResponse>('/health')
    return data
  },

  ready: async (): Promise<ReadyResponse> => {
    const { data } = await api.get<ReadyResponse>('/ready')
    return data
  },
}

// ===== CAMERAS =====
export const cameraApi = {
  list: async (): Promise<Camera[]> => {
    const { data } = await api.get<Camera[]>('/api/v1/cameras')
    return data
  },

  get: async (id: string): Promise<Camera> => {
    const { data } = await api.get<Camera>(`/api/v1/cameras/${id}`)
    return data
  },

  create: async (camera: Partial<Camera>): Promise<Camera> => {
    const { data } = await api.post<Camera>('/api/v1/cameras', camera)
    return data
  },

  capture: async (
    id: string,
    request: { game_instance_id?: string; subject?: string }
  ): Promise<{ image_id: string; filename: string; file_path: string; captured_at: string }> => {
    const { data } = await api.post(`/api/v1/cameras/${id}/capture`, request)
    return data
  },
}

// ===== GAMES (PLACEHOLDER - API endpoints not implemented yet) =====
export const gameApi = {
  list: async (): Promise<Game[]> => {
    const { data } = await api.get<Game[]>('/api/v1/games')
    return data
  },

  get: async (id: string): Promise<Game> => {
    const { data } = await api.get<Game>(`/api/v1/games/${id}`)
    return data
  },

  create: async (game: Partial<Game>): Promise<Game> => {
    const { data } = await api.post<Game>('/api/v1/games', game)
    return data
  },

  listInstances: async (gameId: string): Promise<GameInstance[]> => {
    const { data } = await api.get<GameInstance[]>(`/api/v1/games/${gameId}/instances`)
    return data
  },

  createInstance: async (gameId: string, instance: Partial<GameInstance>): Promise<GameInstance> => {
    const { data } = await api.post<GameInstance>(`/api/v1/games/${gameId}/instances`, instance)
    return data
  },

  getInstance: async (id: string): Promise<GameInstance> => {
    const { data } = await api.get<GameInstance>(`/api/v1/instances/${id}`)
    return data
  },

  getInstanceState: async (id: string): Promise<GameState[]> => {
    const { data } = await api.get<GameState[]>(`/api/v1/instances/${id}/history`)
    return data
  },
}

// ===== IMAGES (PLACEHOLDER - API endpoints not implemented yet) =====
export const imageApi = {
  list: async (params?: Record<string, any>): Promise<Image[]> => {
    const { data } = await api.get<Image[]>('/api/v1/images', { params })
    return data
  },

  get: async (id: string): Promise<Image> => {
    const { data } = await api.get<Image>(`/api/v1/images/${id}`)
    return data
  },

  upload: async (file: File, metadata: Record<string, any>): Promise<Image> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))
    const { data } = await api.post<Image>('/api/v1/images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
