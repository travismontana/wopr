# WOPR Web

Copyright (c) 2025 Bob Bomar <bob@bomar.us>  
Licensed under the MIT License

---

## Overview

React 18 + TypeScript frontend for WOPR (Wargaming Oversight & Position Recognition).

**Tech Stack:**
- **Vite** - Build tool
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Routing
- **React Hook Form** - Form handling
- **Axios** - HTTP client

---

## Features

- ✅ JWT authentication with auto-redirect
- ✅ Dark/Light mode toggle
- ✅ Responsive layout (mobile + desktop)
- ✅ Protected routes
- ✅ API error handling
- ✅ Real-time polling (cameras, health)
- ✅ Type-safe API client
- ✅ Production-ready Docker build

---

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start dev server
npm run dev
```

**Access:** http://localhost:3000

**Default credentials:** `admin / admin123`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build image
docker build -t wopr-web:0.1.0 .

# Run container
docker run -p 80:80 wopr-web:0.1.0
```

**Access:** http://localhost

---

## Project Structure

```
wopr-web/
├── src/
│   ├── components/
│   │   ├── ui/              # Shadcn components (Button, Card, Input, etc.)
│   │   └── layout/          # Layout components (Layout, ProtectedRoute)
│   ├── pages/
│   │   ├── Login.tsx        # Login page
│   │   ├── Dashboard.tsx    # Dashboard
│   │   ├── Cameras.tsx      # Camera management
│   │   ├── games/           # Games pages
│   │   ├── ml/              # ML training pages
│   │   └── admin/           # Admin pages
│   ├── lib/
│   │   ├── api.ts           # API client with axios
│   │   ├── types.ts         # TypeScript types
│   │   └── utils.ts         # Utility functions
│   ├── store/
│   │   ├── authStore.ts     # Auth state (Zustand)
│   │   └── themeStore.ts    # Theme state (Zustand)
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entrypoint
│   └── index.css            # Global styles + Tailwind
├── public/                  # Static assets
├── Dockerfile               # Production build
├── nginx.conf               # Nginx config for SPA
└── package.json
```

---

## Routes

| Path | Component | Auth Required |
|------|-----------|---------------|
| `/login` | Login | No |
| `/dashboard` | Dashboard | Yes |
| `/games` | Games | Yes |
| `/cameras` | Cameras | Yes |
| `/ml` | ML Training | Yes |
| `/admin` | Admin | Yes (admin role) |

---

## Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

**In production (K8s):**
- API proxy configured in nginx.conf
- Requests to `/api/*` → `wopr-api.svc:8000`

---

## API Integration

### Authentication

```typescript
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

// Login
const response = await authApi.login({ username, password })
useAuthStore.getState().login(response)

// Logout
useAuthStore.getState().logout()

// Get current user
const user = await authApi.me()
```

### Cameras

```typescript
import { cameraApi } from '@/lib/api'

// List cameras
const cameras = await cameraApi.list()

// Trigger capture
const result = await cameraApi.capture(cameraId, { subject: 'capture' })
```

### React Query Usage

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'

// Fetch data
const { data, isLoading } = useQuery({
  queryKey: ['cameras'],
  queryFn: cameraApi.list,
})

// Mutate data
const mutation = useMutation({
  mutationFn: cameraApi.capture,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['cameras'] })
  },
})
```

---

## Styling

### Tailwind + Shadcn/ui

Components use Tailwind utility classes:

```tsx
<Button className="w-full">
  Click me
</Button>

<Card className="p-4">
  <CardTitle>Title</CardTitle>
  <CardContent>Content</CardContent>
</Card>
```

### Dark Mode

Controlled by `useThemeStore`:

```typescript
import { useThemeStore } from '@/store/themeStore'

const { theme, toggleTheme } = useThemeStore()
```

CSS variables defined in `index.css`, automatically switch on theme change.

---

## Development

### Type Checking

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

### Building

```bash
npm run build
```

Output: `dist/` directory

---

## Deployment

### Kubernetes

**Prerequisites:**
- wopr-api service running
- Ingress controller

**Steps:**

1. Build image:
```bash
docker build -t your-registry/wopr-web:0.1.0 .
docker push your-registry/wopr-web:0.1.0
```

2. Create k8s manifests (example):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wopr-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wopr-web
  template:
    metadata:
      labels:
        app: wopr-web
    spec:
      containers:
      - name: wopr-web
        image: your-registry/wopr-web:0.1.0
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: wopr-web
spec:
  selector:
    app: wopr-web
  ports:
  - port: 80
    targetPort: 80
```

3. Create ingress:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wopr
spec:
  rules:
  - host: wopr.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wopr-web
            port:
              number: 80
```

---

## Next Steps

### Immediate
- [x] Basic layout and navigation
- [x] Authentication flow
- [x] Dashboard with status cards
- [x] Camera listing and capture
- [ ] Game instance management
- [ ] ML training workflows

### Phase 2
- [ ] WebSocket support for real-time updates
- [ ] Image gallery and viewer
- [ ] Game replay viewer
- [ ] Training progress visualization
- [ ] Advanced admin features

### Phase 3
- [ ] Image annotation tools
- [ ] Batch operations
- [ ] Export/import functionality
- [ ] User preferences
- [ ] Advanced filtering/search

---

## Troubleshooting

### CORS Errors

Ensure wopr-api has CORS configured:
```python
# In wopr-api/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Failed

Check:
1. wopr-api is running on port 8000
2. `VITE_API_URL` in .env is correct
3. Network connectivity

### Authentication Loop

Clear browser storage:
```javascript
localStorage.clear()
```

---

## License

MIT License - see LICENSE file

---

**SYSTEMS STATUS: OPERATIONAL**

Ready for deployment.
