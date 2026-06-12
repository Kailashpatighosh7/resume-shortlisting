import api from './api';

export const candidateService = {
  async list({ jobId, page = 1, perPage = 50, status, search } = {}) {
    const res = await api.get('/candidates', {
      params: {
        job_id: jobId,
        page,
        per_page: perPage,
        status,
        search,
      },
    });
    return res.data;
  },

  async get(id) {
    const res = await api.get(`/candidates/${id}`);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/candidates/${id}`, data);
    return res.data;
  },

  async delete(id) {
    const res = await api.delete(`/candidates/${id}`);
    return res.data;
  },
};
