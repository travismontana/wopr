/                          → Dashboard
/play                      → Game list/management
/play/new                  → New game wizard
/play/:gameId/edit         → Edit specific game
/play/:gameId/status       → Show status, follow along
/settings                  → Settings landing (or redirect to /settings/ml)
/settings/ml               → ML overview
/settings/ml/capture       → Capture interface
/settings/ml/images        → Image gallery
/settings/ml/images/:id    → Edit specific image
/settings/ml/training      → Training pipeline
/settings/cameras          → Camera list
/settings/cameras/:id      → Camera control/edit
/settings/config           → Config management


<Main>                              (app.tsx - layout wrapper)
  <Header />
  <Nav />
  <main>
    <Outlet />                      (routes render here)
      ├─ <Dashboard />              (/)
      ├─ <Play />                   (/play)
      │   └─ <Outlet />             (nested routes)
      │       ├─ <NewGame />        (/play/new)
      │       └─ <EditGame />       (/play/:gameId/edit)
      └─ <Settings />               (/settings)
          └─ <Outlet />             (nested routes)
              ├─ <ML />             (/settings/ml)
              │   └─ <Outlet />
              │       ├─ <Capture />
              │       ├─ <Images />
              │       └─ <Training />
              ├─ <Cameras />        (/settings/cameras)
              └─ <Config />         (/settings/config)