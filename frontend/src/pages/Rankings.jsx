import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Trophy, Play, Download, Eye } from 'lucide-react';
import { useJobs } from '../hooks/useJobs';
import { useRankings } from '../hooks/useRankings';
import { rankingService } from '../services/rankingService';
import { candidateService } from '../services/candidateService';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import Table from '../components/ui/Table';
import Card, { CardHeader } from '../components/ui/Card';
import Modal from '../components/ui/Modal';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import Badge from '../components/ui/Badge';
import ProcessingSteps from '../components/shared/ProcessingSteps';
import ScoreGauge from '../components/shared/ScoreGauge';
import { RANKING_PROCESSING_STEPS } from '../utils/processingSteps';
import SkillBadge from '../components/shared/SkillBadge';
import { getApiErrorMessage } from '../utils/validators';

export default function Rankings() {
  const { jobId: paramJobId } = useParams();
  const navigate = useNavigate();
  const [selectedJobId, setSelectedJobId] = useState(paramJobId || '');
  const [explainData, setExplainData] = useState(null);
  const [explainLoading, setExplainLoading] = useState(false);

  const { items: jobs } = useJobs({ perPage: 100 });
  const { rankings, loading, error, fetchRankings, runRanking } = useRankings(
    selectedJobId ? parseInt(selectedJobId, 10) : null
  );

  useEffect(() => {
    if (paramJobId) setSelectedJobId(paramJobId);
  }, [paramJobId]);

  useEffect(() => {
    if (selectedJobId) fetchRankings();
  }, [selectedJobId, fetchRankings]);

  const jobOptions = jobs.map((j) => ({ value: String(j.id), label: j.title }));

  const handleRank = async () => {
    try {
      await runRanking();
    } catch {
      // error handled in hook
    }
  };

  const handleExport = async () => {
    try {
      const blob = await rankingService.exportCsv(parseInt(selectedJobId, 10));
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rankings_job_${selectedJobId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(getApiErrorMessage(err));
    }
  };

  const handleExplain = async (candidateId) => {
    setExplainLoading(true);
    setExplainData(null);
    try {
      const detail = await candidateService.get(candidateId);
      if (detail.score?.id) {
        const report = await rankingService.getExplanation(detail.score.id);
        setExplainData(report);
      } else {
        alert('No score available for this candidate. Run ranking first.');
      }
    } catch (err) {
      alert(getApiErrorMessage(err));
    } finally {
      setExplainLoading(false);
    }
  };

  const columns = [
    { key: 'rank', label: '#', className: 'w-12' },
    { key: 'candidate_name', label: 'Candidate', render: (row) => (
      <div>
        <p className="font-medium text-brand-600">{row.candidate_name}</p>
        <p className="text-xs text-slate-500">{row.candidate_email}</p>
      </div>
    )},
    { key: 'status', label: 'Status', render: (row) => (
      row.status && row.status !== 'new' ? <Badge status={row.status} /> : <span className="text-slate-400">—</span>
    )},
    { key: 'overall_score', label: 'Score', render: (row) => (
      <div className="flex items-center gap-2">
        <ScoreGauge score={row.overall_score} size="sm" />
      </div>
    )},
    { key: 'matched_skills', label: 'Matched', render: (row) => (
      <div className="flex flex-wrap gap-1 max-w-xs">
        {(row.matched_skills || []).slice(0, 3).map((s) => (
          <SkillBadge key={s} skill={typeof s === 'string' ? s : s.skill} variant="matched" />
        ))}
        {(row.matched_skills || []).length > 3 && (
          <span className="text-xs text-slate-400">+{row.matched_skills.length - 3}</span>
        )}
      </div>
    )},
    { key: 'actions', label: '', render: (row) => (
      <div className="flex gap-1">
        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleExplain(row.candidate_id); }}>
          <Eye className="h-4 w-4" />
        </Button>
      </div>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Rankings</h2>
          <p className="text-slate-500">AI-powered semantic candidate ranking</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRank} loading={loading} disabled={!selectedJobId}>
            <Play className="h-4 w-4" /> Run Ranking
          </Button>
          {rankings?.rankings?.length > 0 && (
            <Button variant="secondary" onClick={handleExport}>
              <Download className="h-4 w-4" /> Export CSV
            </Button>
          )}
        </div>
      </div>

      <Select
        label="Select Job"
        options={jobOptions}
        placeholder="Choose a job to view rankings..."
        value={selectedJobId}
        onChange={(e) => setSelectedJobId(e.target.value)}
        className="max-w-md"
      />

      {!selectedJobId ? (
        <EmptyState icon={Trophy} title="Select a job" description="Choose a job posting to view or generate rankings." />
      ) : loading && !rankings ? (
        <Card>
          <div className="py-8">
            <ProcessingSteps
              active={loading}
              steps={RANKING_PROCESSING_STEPS}
              title="Calculating rankings..."
            />
          </div>
        </Card>
      ) : error ? (
        <ErrorState message={error} onRetry={fetchRankings} />
      ) : !rankings?.rankings?.length ? (
        <EmptyState
          icon={Trophy}
          title="No rankings yet"
          description="Upload resumes and run ranking to see AI-scored candidates."
          action={<Button onClick={handleRank} loading={loading}><Play className="h-4 w-4" /> Run Ranking</Button>}
        />
      ) : (
        <Card padding={false}>
          <div className="border-b border-slate-200 px-6 py-4">
            <CardHeader
              title={rankings.job_title}
              subtitle={`${rankings.total_candidates} candidates ranked · top ${rankings.shortlist_quota} auto-shortlisted`}
            />
          </div>
          <Table
            columns={columns}
            data={rankings.rankings}
            onRowClick={(row) => navigate(`/candidates/${row.candidate_id}`)}
          />
        </Card>
      )}

      <Modal open={!!explainData} onClose={() => setExplainData(null)} title="Explainability Report" size="lg">
        {explainLoading ? (
          <Spinner />
        ) : explainData && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <ScoreGauge score={explainData.overall_score} size="md" />
              <div>
                <p className="font-medium text-slate-900">{explainData.candidate_name}</p>
                <p className="text-sm text-slate-500">{explainData.job_title}</p>
              </div>
            </div>
            {explainData.explanation_text && (
              <p className="rounded-lg bg-slate-50 p-4 text-sm text-slate-700">{explainData.explanation_text}</p>
            )}
            <div>
              <p className="mb-2 text-sm font-medium text-slate-500">Matched Skills</p>
              <div className="flex flex-wrap gap-1">
                {(explainData.matched_skills || []).map((s) => (
                  <SkillBadge key={s} skill={typeof s === 'string' ? s : s.skill} variant="matched" />
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-slate-500">Missing Skills</p>
              <div className="flex flex-wrap gap-1">
                {(explainData.missing_skills || []).map((s) => (
                  <SkillBadge key={s} skill={typeof s === 'string' ? s : s.skill} variant="missing" />
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
