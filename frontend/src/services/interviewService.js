import api from './api';

export const interviewService = {
  async list({ status } = {}) {
    const res = await api.get('/interviews', { params: { status } });
    return res.data;
  },

  async create(data) {
    const res = await api.post('/interviews', data);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/interviews/${id}`, data);
    return res.data;
  },

  async delete(id) {
    const res = await api.delete(`/interviews/${id}`);
    return res.data;
  },
};
