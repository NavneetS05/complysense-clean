// Use: Root component of the React application. Renders the application router with Toast context.

import { AppRouter } from "./routes/AppRouter";
import { ToastProvider } from "./components/shared/Toast";

export function App() {
  return (
    <ToastProvider>
      <AppRouter />
    </ToastProvider>
  );
}
