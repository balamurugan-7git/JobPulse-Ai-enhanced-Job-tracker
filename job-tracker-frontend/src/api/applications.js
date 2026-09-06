import api from "./axios";

export const getApplications = () => api.get("/applications");
export const createApplication = (data) => api.post("/applications", data);
export const updateApplication = (id, data) => api.put(`/applications/${id}`, data);
export const deleteApplication = (id) => api.delete(`/applications/${id}`);

export const computeMatchScore = (id) => api.post(`/applications/${id}/match-score`);
export const classifyRole = (id) => api.post(`/applications/${id}/classify-role`);
export const getSkillGap = (id) => api.get(`/applications/${id}/skill-gap`);

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/me/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const updateExperience = (years) =>
  api.put("/me/experience", { years_of_experience: years });

export const getAnalytics = () => api.get("/analytics");