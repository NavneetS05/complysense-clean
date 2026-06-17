// Use: Axios API client instance configured for the AI microservice.

import axios from "axios";

export const aiApi = axios.create({
  baseURL: import.meta.env.VITE_AI_URL ?? "http://localhost:8001"
});
