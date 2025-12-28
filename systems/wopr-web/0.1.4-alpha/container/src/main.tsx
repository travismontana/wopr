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

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      {
        path: "play",
        element: <Play />,
        children: [
          { path: "new", element: <NewGame /> },
        ],
      },
      {
        path: "settings",
        element: <Settings />,
        children: [
          {
            path: "ml",
            element: <MLOverview />,
            children: [
              { path: "capture", element: <Capture /> },
            ],
          },
          {
            path: "status",
            element: <SysStatus />,
            children: [],
          },
          {
            path: "config",
            element: <SysConfig />,
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