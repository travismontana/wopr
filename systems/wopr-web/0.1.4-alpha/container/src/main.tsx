import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./app";

// Route imports
import Dashboard from "./routes/home/dashboard";
import Play from "./routes/play/index";
import NewGame from "./routes/play/new-game";
import Settings from "./routes/settings/index";
import MLOverview from "./routes/settings/ml/index";
import Capture from "./routes/settings/ml/capture";
import SysStatus from "./routes/settings/status/index";
import SysConfig from "./routes/settings/config/index";

// Theme
import "./themes/modern.css";
import WorkInProgress from "./routes/wip";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <WorkInProgress /> },
      {
        path: "play",
        element: <WorkInProgress />,
        children: [
          { path: "new", element: <WorkInProgress /> },
        ],
      },
      {
        path: "settings",
        element: <Settings />,
        children: [
          {
            path: "ml",
            element: <WorkInProgress />,
            children: [
              { path: "capture", element: <WorkInProgress /> },
            ],
          },
          {
            path: "status",
            element: <StatusPage />,
            children: [],
          },
          {
            path: "config",
            element: <WorkInProgress />,
            children: [],
          }
        ],
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);