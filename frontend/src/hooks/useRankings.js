import { useCallback, useState } from 'react';
import { rankingService } from '../services/rankingService';
import { getApiErrorMessage } from '../utils/validators';

export function useRankings(jobId) {
  const [rankings, setRankings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRankings = useCallback(async () => {
    if (!jobId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await rankingService.getRankings(jobId);
      setRankings(result);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  const runRanking = useCallback(async () => {
    if (!jobId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await rankingService.rank(jobId);
      setRankings(result);
      return result;
    } catch (err) {
      setError(getApiErrorMessage(err));
      throw err;
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  return { rankings, loading, error, fetchRankings, runRanking };
}
