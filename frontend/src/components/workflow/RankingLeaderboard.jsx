import { useNavigate } from 'react-router-dom';
import { Trophy } from 'lucide-react';
import Button from '../ui/Button';
import Card, { CardHeader } from '../ui/Card';
import Badge from '../ui/Badge';
import ScoreGauge from '../shared/ScoreGauge';
import SkillBadge from '../shared/SkillBadge';
import ProcessingSteps from '../shared/ProcessingSteps';
import { RANKING_PROCESSING_STEPS } from '../../utils/processingSteps';

export default function RankingLeaderboard({
  rankings,
  loading,
  onContinue,
}) {
  const navigate = useNavigate();

  if (loading) {
    return (
      <Card>
        <div className="py-8">
          <ProcessingSteps
            active={loading}
            steps={RANKING_PROCESSING_STEPS}
            title="Calculating rankings..."
          />
        </div>
      </Card>
    );
  }

  if (!rankings?.rankings?.length) {
    return (
      <Card>
        <div className="py-12 text-center">
          <Trophy className="mx-auto h-12 w-12 text-slate-300" />
          <p className="mt-4 text-slate-600">No candidates to rank yet.</p>
        </div>
      </Card>
    );
  }

  const shortlistedCount = rankings.rankings.filter((r) => r.status === 'shortlisted').length;
  const rejectedCount = rankings.rankings.filter((r) => r.status === 'rejected').length;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title="Leaderboard"
          subtitle={`${rankings.job_title} — ${rankings.total_candidates} candidates ranked`}
        />
        <p className="mb-4 text-sm text-slate-500">
          Top <strong>{rankings.shortlist_quota}</strong> candidates were automatically shortlisted;
          the rest were rejected. Click a name to review or change status on their profile.
        </p>

        <div className="mb-4 flex gap-4 text-sm">
          <span className="rounded-full bg-emerald-100 px-3 py-1 font-medium text-emerald-700">
            {shortlistedCount} shortlisted
          </span>
          <span className="rounded-full bg-orange-100 px-3 py-1 font-medium text-orange-700">
            {rejectedCount} rejected
          </span>
        </div>

        <div className="space-y-3">
          {rankings.rankings.map((entry) => (
            <div
              key={entry.candidate_id}
              className={`rounded-xl border p-4 transition-colors ${
                entry.status === 'shortlisted'
                  ? 'border-emerald-200 bg-emerald-50/50'
                  : entry.status === 'rejected'
                    ? 'border-orange-200 bg-orange-50/50'
                    : 'border-slate-200 bg-white'
              }`}
            >
              <div className="flex flex-wrap items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
                  #{entry.rank}
                </div>
                <ScoreGauge score={entry.overall_score} size="sm" />
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => navigate(`/candidates/${entry.candidate_id}`)}
                      className="font-semibold text-brand-600 hover:text-brand-800 hover:underline"
                    >
                      {entry.candidate_name}
                    </button>
                    {entry.status && entry.status !== 'new' && <Badge status={entry.status} />}
                  </div>
                  <p className="text-sm text-slate-500">{entry.candidate_email || 'No email'}</p>
                  <p className="mt-1 text-xs text-slate-400">{entry.resume_filename}</p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {(entry.matched_skills || []).slice(0, 5).map((s) => (
                      <SkillBadge
                        key={s}
                        skill={typeof s === 'string' ? s : s.skill}
                        variant="matched"
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={onContinue}>
          Continue to Send Emails
        </Button>
      </div>
    </div>
  );
}
