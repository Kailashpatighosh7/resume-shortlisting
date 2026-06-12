import api from './api';

export const analyticsService = {
  async getDashboard() {
    const res = await api.get('/analytics/dashboard');
    return res.data;
  },
};
