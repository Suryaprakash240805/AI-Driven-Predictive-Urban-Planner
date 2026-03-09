import api from "./authApi";

export const getPendingProjects = () => api.get("/validator/pending");
export const approveProject = (id, data) => api.post(`/validator/approve/${id}`, data);
export const rejectProject = (id, data) => api.post(`/validator/reject/${id}`, data);
export const getValidatorStats = () => api.get("/validator/stats");
