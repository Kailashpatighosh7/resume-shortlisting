import api from './api';

export const authService = {
  async register(data) {
    const res = await api.post('/auth/register', data);
    return res.data;
  },

  async login(email, password) {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const res = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },

  async getMe() {
    const res = await api.get('/auth/me');
    return res.data;
  },

  async updateProfile(data) {
    const res = await api.put('/auth/me', data);
    return res.data;
  },

  async changePassword(currentPassword, newPassword) {
    const res = await api.post('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return res.data;
  },

  async verifyForgotPassword(email) {
    const res = await api.post('/auth/forgot-password/verify', { email });
    return res.data;
  },

  async resetPassword(email, newPassword) {
    const res = await api.post('/auth/forgot-password/reset', {
      email,
      new_password: newPassword,
    });
    return res.data;
  },
};
