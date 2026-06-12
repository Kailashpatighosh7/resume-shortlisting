import api from './api';

export const jobService = {
  async list({ page = 1, perPage = 20, status, search } = {}) {
    const res = await api.get('/jobs', {
      params: { page, per_page: perPage, status, search },
    });
    return res.data;
  },

  async get(id) {
    const res = await api.get(`/jobs/${id}`);
    return res.data;
  },

  async create(data) {
    const res = await api.post('/jobs', data);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/jobs/${id}`, data);
    return res.data;
  },

  async delete(id) {
    const res = await api.delete(`/jobs/${id}`);
    return res.data;
  },
};
