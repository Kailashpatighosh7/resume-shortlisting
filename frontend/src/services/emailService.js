import api from './api';

export const emailService = {
  async getStats() {
    const res = await api.get('/emails/stats');
    return res.data;
  },

  async list({ emailType, jobId, limit = 100 } = {}) {
    const res = await api.get('/emails', {
      params: { email_type: emailType, job_id: jobId, limit },
    });
    return res.data;
  },

  async send(data) {
    const res = await api.post('/emails/send', data);
    return res.data;
  },
};
