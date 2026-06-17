// Use: Axios API client instance configured with interceptors for the main backend service.

import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000"
});
