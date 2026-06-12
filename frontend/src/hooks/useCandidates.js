import { useCallback, useEffect, useState } from 'react';
import { candidateService } from '../services/candidateService';
import { getApiErrorMessage } from '../utils/validators';

export function useCandidates(params = {}) {
  const [data, setData] = useState({ items: [], total: 0, page: 1, per_page: 50 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCandidates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await candidateService.list(params);
      setData(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [params.jobId, params.page, params.perPage, params.status, params.search]);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  return { ...data, loading, error, refetch: fetchCandidates };
}

export function useCandidate(id) {
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCandidate = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const result = await candidateService.get(id);
      setCandidate(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCandidate();
  }, [fetchCandidate]);

  return { candidate, loading, error, refetch: fetchCandidate };
}
