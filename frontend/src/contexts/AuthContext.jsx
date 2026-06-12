import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const profile = await authService.getMe();
      setUser(profile);
    } catch {
      localStorage.removeItem('access_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email, password) => {
    const { access_token } = await authService.login(email, password);
    localStorage.setItem('access_token', access_token);
    const profile = await authService.getMe();
    setUser(profile);
    return profile;
  };

  const register = async (data) => {
    await authService.register(data);
    return login(data.email, data.password);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  const updateProfile = async (data) => {
    const profile = await authService.updateProfile(data);
    setUser(profile);
    return profile;
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
      updateProfile,
      refreshUser: loadUser,
    }),
    [user, loading, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
