import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_URL;
let baseURL = "https://jobpulse-ai-enhanced-job-tracker-production.up.railway.app/";

if (rawBaseUrl) {
  baseURL = rawBaseUrl.startsWith("http://") || rawBaseUrl.startsWith("https://")
    ? rawBaseUrl
    : `https://${rawBaseUrl}`;
}

const api = axios.create({
  baseURL: baseURL,
});

// Automatically attach the JWT token (if present) to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;