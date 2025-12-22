# WOPR Web UI

React (Vite) SPA served via nginx, designed to run in Kubernetes behind Traefik.

Routes:
- /            Dashboard
- /games       Games & sessions
- /images      Captures browser
- /ml          ML / model learning UI
- /ml/*        Labeling, datasets, training

Backends:
- /api/*       wopr-api
- /ml/api/*    wopr-ml
