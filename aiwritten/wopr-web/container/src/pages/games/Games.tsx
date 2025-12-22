/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * Games page - list and start games.
 */

import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Play } from 'lucide-react'
import type { GameInstance } from "@/lib/types"

export function Games() {
  // TODO: Fetch game instances when API is ready
  const games: GameInstance[] = []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Games</h1>
          <p className="text-muted-foreground">Manage game sessions</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Start New Game
        </Button>
      </div>

      {games.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Play className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No active games</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Start a new game to begin tracking
            </p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Start Your First Game
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {games.map((game: any) => (
            <Card key={game.id}>
              <CardHeader>
                <CardTitle>{game.display_name}</CardTitle>
                <CardDescription>
                  {game.player_count} players • Round {game.current_round}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <Link to={`/games/${game.id}`}>View Game</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
