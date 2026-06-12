import { useCallback, useEffect, useState } from 'react';
import { jobService } from '../services/jobService';
import { getApiErrorMessage } from '../utils/validators';

export function useJobs(params = {}) {
  const [data, setData] = useState({ items: [], total: 0, page: 1, per_page: 20 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await jobService.list(params);
      setData(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [params.page, params.perPage, params.status, params.search]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return { ...data, loading, error, refetch: fetchJobs };
}

export function useJob(id) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJob = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const result = await jobService.get(id);
      setJob(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchJob();
  }, [fetchJob]);

  return { job, loading, error, refetch: fetchJob };
}
