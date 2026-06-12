import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Download, Trash2, Mail, Calendar, UserCheck, UserX } from 'lucide-react';
import { useCandidate } from '../hooks/useCandidates';
import { candidateService } from '../services/candidateService';
import { resumeService } from '../services/resumeService';
import { emailService } from '../services/emailService';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Card, { CardHeader } from '../components/ui/Card';
import Select from '../components/ui/Select';
import Modal from '../components/ui/Modal';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import ScoreGauge from '../components/shared/ScoreGauge';
import SkillBadge from '../components/shared/SkillBadge';
import { CANDIDATE_STATUSES, EMAIL_TYPES } from '../utils/constants';
import { formatDate, formatDateTime } from '../utils/formatters';
import { getApiErrorMessage } from '../utils/validators';

export default function CandidateDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { candidate, loading, error, refetch } = useCandidate(id);

  const [statusUpdating, setStatusUpdating] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [emailOpen, setEmailOpen] = useState(false);
  const [emailType, setEmailType] = useState('shortlisted');
  const [sending, setSending] = useState(false);

  const updateStatus = async (status) => {
    setStatusUpdating(true);
    try {
      await candidateService.update(id, { status });
      refetch();
    } catch (err) {
      alert(getApiErrorMessage(err));
    } finally {
      setStatusUpdating(false);
    }
  };

  const handleStatusChange = async (e) => {
    await updateStatus(e.target.value);
  };

  const handleDownload = async () => {
    if (!candidate?.resume) return;
    try {
      const blob = await resumeService.download(candidate.resume.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = candidate.resume.original_filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(getApiErrorMessage(err));
    }
  };

  const handleDelete = async () => {
    try {
      await candidateService.delete(id);
      navigate('/candidates');
    } catch (err) {
      alert(getApiErrorMessage(err));
    }
  };

  const handleSendEmail = async () => {
    setSending(true);
    try {
      await emailService.send({
        candidate_id: parseInt(id, 10),
        job_id: candidate.job_id,
        email_type: emailType,
      });
      setEmailOpen(false);
      alert('Email sent successfully');
    } catch (err) {
      alert(getApiErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  if (loading) return <Spinner className="py-20" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!candidate) return null;

  const score = candidate.score;
  const parsed = candidate.resume?.parsed_data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-slate-900">{candidate.name}</h2>
            <Badge status={candidate.status} />
          </div>
          <p className="mt-1 text-slate-500">
            {candidate.email || 'No email'} · {candidate.phone || 'No phone'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/interviews?candidateId=${id}&jobId=${candidate.job_id}`}>
            <Button variant="secondary"><Calendar className="h-4 w-4" /> Schedule Interview</Button>
          </Link>
          <Button variant="secondary" onClick={() => setEmailOpen(true)}>
            <Mail className="h-4 w-4" /> Send Email
          </Button>
          {candidate.resume && (
            <Button variant="secondary" onClick={handleDownload}>
              <Download className="h-4 w-4" /> Download Resume
            </Button>
          )}
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="h-4 w-4" /> Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Shortlisting Decision" subtitle="Override auto-shortlist or reject manually" />
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant={candidate.status === 'shortlisted' ? 'success' : 'secondary'}
              loading={statusUpdating}
              onClick={() => updateStatus('shortlisted')}
            >
              <UserCheck className="h-4 w-4" /> Shortlist
            </Button>
            <Button
              size="sm"
              variant={candidate.status === 'rejected' ? 'danger' : 'secondary'}
              loading={statusUpdating}
              onClick={() => updateStatus('rejected')}
            >
              <UserX className="h-4 w-4" /> Reject
            </Button>
          </div>
          <div className="mt-4">
            <Select
              label="Status"
              options={CANDIDATE_STATUSES}
              value={candidate.status}
              onChange={handleStatusChange}
              disabled={statusUpdating}
            />
          </div>
          <p className="mt-3 text-xs text-slate-500">Added {formatDate(candidate.created_at)}</p>
        </Card>

        {score && (
          <Card className="lg:col-span-2">
            <CardHeader title="AI Match Score" subtitle={`Scored ${formatDateTime(score.scored_at)}`} />
            <div className="flex flex-wrap items-start gap-8">
              <ScoreGauge score={score.overall_score} size="lg" />
              <div className="flex-1 space-y-4">
                <div>
                  <p className="mb-2 text-sm font-medium text-slate-500">Matched Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {(score.matched_skills || []).map((s) => (
                      <SkillBadge key={s} skill={typeof s === 'string' ? s : s.skill || s.name} variant="matched" />
                    ))}
                  </div>
                </div>
                <div>
                  <p className="mb-2 text-sm font-medium text-slate-500">Missing Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {(score.missing_skills || []).map((s) => (
                      <SkillBadge key={s} skill={typeof s === 'string' ? s : s.skill || s.name} variant="missing" />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>

      {parsed && (
        <div className="grid gap-6 lg:grid-cols-2">
          {parsed.skills?.length > 0 && (
            <Card>
              <CardHeader title="Extracted Skills" />
              <div className="flex flex-wrap gap-1">
                {parsed.skills.map((s) => <SkillBadge key={s} skill={s} />)}
              </div>
            </Card>
          )}
          {parsed.education?.length > 0 && (
            <Card>
              <CardHeader title="Education" />
              <ul className="space-y-2 text-sm text-slate-700">
                {parsed.education.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </Card>
          )}
          {parsed.experience?.length > 0 && (
            <Card className="lg:col-span-2">
              <CardHeader title="Experience" />
              <ul className="space-y-2 text-sm text-slate-700">
                {parsed.experience.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </Card>
          )}
        </div>
      )}

      {candidate.resume?.parsed_text && (
        <Card>
          <CardHeader title="Resume Text" subtitle={candidate.resume.original_filename} />
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-xs text-slate-700">
            {candidate.resume.parsed_text}
          </pre>
        </Card>
      )}

      <Modal open={deleteOpen} onClose={() => setDeleteOpen(false)} title="Delete Candidate">
        <p className="text-sm text-slate-600">This will permanently delete the candidate and their resume.</p>
        <div className="mt-4 flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>

      <Modal open={emailOpen} onClose={() => setEmailOpen(false)} title="Send Email">
        <Select label="Email Type" options={EMAIL_TYPES} value={emailType} onChange={(e) => setEmailType(e.target.value)} />
        <div className="mt-4 flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setEmailOpen(false)}>Cancel</Button>
          <Button loading={sending} onClick={handleSendEmail}>Send</Button>
        </div>
      </Modal>
    </div>
  );
}
