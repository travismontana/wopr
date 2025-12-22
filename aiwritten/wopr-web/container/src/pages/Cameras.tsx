/**
 * WOPR - Wargaming Oversight & Position Recognition
 * Copyright (c) 2025 Bob Bomar <bob@bomar.us>
 * SPDX-License-Identifier: MIT
 * 
 * Cameras page - manage cameras and trigger captures.
 */

import { useQuery, useMutation } from '@tanstack/react-query'
import { cameraApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Camera as CameraIcon, CheckCircle2, XCircle, Wifi, WifiOff } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

export function Cameras() {

  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraApi.list,
  })

  const captureMutation = useMutation({
    mutationFn: ({ id, subject }: { id: string; subject: string }) =>
      cameraApi.capture(id, { subject }),
    onSuccess: () => {
      alert('Capture successful!')
    },
    onError: (error: any) => {
      alert(`Capture failed: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleCapture = (cameraId: string) => {
    captureMutation.mutate({ id: cameraId, subject: 'capture' })
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cameras</h1>
          <p className="text-muted-foreground">Manage capture devices</p>
        </div>
      </div>

      {cameras && cameras.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CameraIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No cameras registered</h3>
            <p className="text-sm text-muted-foreground">
              Register cameras via the API
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cameras?.map((camera) => {
            const isOnline = camera.status === 'online'
            const lastSeen = camera.last_heartbeat
              ? formatRelativeTime(camera.last_heartbeat)
              : 'Never'

            return (
              <Card key={camera.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {camera.name}
                        {isOnline ? (
                          <Wifi className="h-4 w-4 text-green-500" />
                        ) : (
                          <WifiOff className="h-4 w-4 text-red-500" />
                        )}
                      </CardTitle>
                      <CardDescription>{camera.device_id}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Status</span>
                    <div className="flex items-center gap-1">
                      {isOnline ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="capitalize">{camera.status}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last seen</span>
                    <span>{lastSeen}</span>
                  </div>

                  <Button
                    className="w-full"
                    onClick={() => handleCapture(camera.id)}
                    disabled={!isOnline || captureMutation.isPending}
                  >
                    <CameraIcon className="mr-2 h-4 w-4" />
                    {captureMutation.isPending ? 'Capturing...' : 'Capture'}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
