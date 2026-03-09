import api from "./authApi";

export const analyzeLand = (polygon) => api.post("/land/analyze", { polygon });
export const createProject = (data) => api.post("/projects", data);
export const getMyProjects = () => api.get("/projects/my");
export const getProjectDetails = (id) => api.get(`/projects/${id}`);
