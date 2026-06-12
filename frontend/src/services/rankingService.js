import api from './api';

export const rankingService = {
  async rank(jobId) {
    const res = await api.post(`/jobs/${jobId}/rank`);
    return res.data;
  },

  async getRankings(jobId) {
    const res = await api.get(`/jobs/${jobId}/rankings`);
    return res.data;
  },

  async getExplanation(scoreId) {
    const res = await api.get(`/rankings/${scoreId}/explain`);
    return res.data;
  },

  async exportCsv(jobId) {
    const res = await api.get(`/jobs/${jobId}/rankings/export`, {
      responseType: 'blob',
    });
    return res.data;
  },
};
