import axios from "axios";

const api = axios.create({
  baseURL: "https://jobpulse-ai-enhanced-job-tracker-production.up.railway.app/",
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