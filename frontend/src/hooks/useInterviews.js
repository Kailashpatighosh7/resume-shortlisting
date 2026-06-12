import { useCallback, useEffect, useState } from 'react';
import { interviewService } from '../services/interviewService';
import { getApiErrorMessage } from '../utils/validators';

export function useInterviews(params = {}) {
  const [data, setData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInterviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await interviewService.list(params);
      setData(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [params.status]);

  useEffect(() => {
    fetchInterviews();
  }, [fetchInterviews]);

  return { ...data, loading, error, refetch: fetchInterviews };
}
