/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * Authentication state management with Zustand.
 */

import { create } from 'zustand'
import type { User, TokenResponse } from '@/lib/types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (tokenResponse: TokenResponse) => void
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => {
  // Initialize from localStorage
  const storedToken = localStorage.getItem('wopr_token')
  const storedUser = localStorage.getItem('wopr_user')
  
  return {
    user: storedUser ? JSON.parse(storedUser) : null,
    token: storedToken,
    isAuthenticated: !!storedToken,

    login: (tokenResponse: TokenResponse) => {
      localStorage.setItem('wopr_token', tokenResponse.access_token)
      localStorage.setItem('wopr_user', JSON.stringify(tokenResponse.user))
      set({
        user: tokenResponse.user,
        token: tokenResponse.access_token,
        isAuthenticated: true,
      })
    },

    logout: () => {
      localStorage.removeItem('wopr_token')
      localStorage.removeItem('wopr_user')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      })
    },

    setUser: (user: User) => {
      localStorage.setItem('wopr_user', JSON.stringify(user))
      set({ user })
    },
  }
})
