import { useCallback, useEffect, useState } from 'react';
import { emailService } from '../services/emailService';
import { getApiErrorMessage } from '../utils/validators';

export function useEmailStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await emailService.getStats();
      setStats(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}

export function useEmailLogs(params = {}) {
  const [data, setData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await emailService.list(params);
      setData(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [params.emailType, params.jobId, params.limit]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  return { ...data, loading, error, refetch: fetchLogs };
}
