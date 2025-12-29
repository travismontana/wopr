import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./app";

// Route imports
import Dashboard from "./routes/home/dashboard";
import Play from "./routes/play/index";
import NewGame from "./routes/play/new-game";
import BackOfHouse from "./routes/boh/index";
import StatusPage from "./routes/boh/status/index";
import CameraPage from "./routes/boh/cameras/index";
import CapturePage from "./routes/boh/cameras/capture";
import MLOverview from "./routes/boh/ml/index";
import ImageGallery from "./routes/boh/images/view";
import ImagesPage from "./routes/boh/images/index";
import ConfigPage from "./routes/boh/config/index";
import ConfigEditPage from "./routes/boh/config/control";

// Theme
import "./themes/modern.css";
import WorkInProgress from "./routes/wip";
import GamesManager from "./pages/GamesManager";
import MLImagesManager from "./pages/MLImagesManager";
import PiecesManager from "./pages/PiecesManager";


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
        path: "boh",
        element: <BackOfHouse />,
        children: [
          {
            path: "games",
            element: <GamesManager />,
            children: [],
          },
          {
            path: "pieces",
            element: <PiecesManager />,
            children: [],
          },
          {
            path: "ml",
            element: <WorkInProgress />,
            children: [
              { path: "images", element: <MLImagesManager /> },
            ],
          },
          {
            path: "cameras",
            element: <CameraPage />,
            children: [
              { path: "capture", element: <CapturePage /> },
              { path: "config", element: <WorkInProgress /> },
              { path: "status", element: <WorkInProgress /> },
            ],
          },
          {
            path: "images",
            element: <ImagesPage />,
            children: [
              { path: "view", element: <ImageGallery gameId="dune_imperium" /> },
              { path: "edit", element: <WorkInProgress /> },
              { path: "other", element: <WorkInProgress /> },
            ],
          },
          {
            path: "status",
            element: <StatusPage />,
            children: [],
          },
          {
            path: "config",
            element: <ConfigPage />,
            children: [
              { path: "control", element: <ConfigEditPage /> },
            ],
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