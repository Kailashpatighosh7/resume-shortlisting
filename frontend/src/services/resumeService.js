import api from './api';

export const resumeService = {
  async upload(jobId, files) {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const res = await api.post(`/resumes/upload/${jobId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async uploadZip(jobId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post(`/resumes/upload-zip/${jobId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async get(id) {
    const res = await api.get(`/resumes/${id}`);
    return res.data;
  },

  async download(id) {
    const res = await api.get(`/resumes/${id}/download`, { responseType: 'blob' });
    return res.data;
  },

  async delete(id) {
    const res = await api.delete(`/resumes/${id}`);
    return res.data;
  },
};
