/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * Theme state management.
 */

import { create } from 'zustand'

type Theme = 'light' | 'dark'

interface ThemeState {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

export const useThemeStore = create<ThemeState>((set) => {
  // Initialize from localStorage or system preference
  const storedTheme = localStorage.getItem('wopr_theme') as Theme
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  const initialTheme = storedTheme || systemTheme

  // Apply theme to document
  if (initialTheme === 'dark') {
    document.documentElement.classList.add('dark')
  }

  return {
    theme: initialTheme,

    toggleTheme: () =>
      set((state) => {
        const newTheme = state.theme === 'light' ? 'dark' : 'light'
        localStorage.setItem('wopr_theme', newTheme)
        if (newTheme === 'dark') {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
        return { theme: newTheme }
      }),

    setTheme: (theme: Theme) => {
      localStorage.setItem('wopr_theme', theme)
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      set({ theme })
    },
  }
})
