/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * Admin page - user management, config, system monitoring.
 */

import { Card, CardContent } from '@/components/ui/card'
import { Settings } from 'lucide-react'

export function Admin() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin</h1>
        <p className="text-muted-foreground">
          System administration and configuration
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Settings className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Admin Panel</h3>
          <p className="text-sm text-muted-foreground text-center max-w-md">
            User management, configuration editing, and system monitoring coming soon.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
