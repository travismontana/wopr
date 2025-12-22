/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * ML Training page - capture training data and manage training jobs.
 */

import { Card, CardContent } from '@/components/ui/card'
import { Brain } from 'lucide-react'

export function MLTraining() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ML Training</h1>
        <p className="text-muted-foreground">
          Capture training data and manage model training
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Brain className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">ML Training</h3>
          <p className="text-sm text-muted-foreground text-center max-w-md">
            Training workflows and dataset management coming soon.
            This will include image capture, labeling, and training job management.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
