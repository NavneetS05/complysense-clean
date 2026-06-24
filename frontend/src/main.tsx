// Use: React app entry point. Renders the application with router and global providers.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

// Apply persisted dark mode class before first render to prevent flash
try {
  const dark = localStorage.getItem("cs_dark");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (dark === "true" || (dark === null && prefersDark)) {
    document.documentElement.classList.add("dark");
  }
} catch { /* */ }

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
