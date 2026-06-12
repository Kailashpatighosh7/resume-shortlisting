import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Edit, Trash2, Upload, Trophy, Users } from 'lucide-react';
import { useJob } from '../hooks/useJobs';
import { useCandidates } from '../hooks/useCandidates';
import { jobService } from '../services/jobService';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Card, { CardHeader } from '../components/ui/Card';
import Table from '../components/ui/Table';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import Modal from '../components/ui/Modal';
import SkillBadge from '../components/shared/SkillBadge';
import { parseSkills, formatDate } from '../utils/formatters';
import { getApiErrorMessage } from '../utils/validators';

export default function JobDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { job, loading, error, refetch } = useJob(id);
  const { items: candidates } = useCandidates({ jobId: parseInt(id, 10), perPage: 10 });
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await jobService.delete(id);
      navigate('/jobs');
    } catch (err) {
      alert(getApiErrorMessage(err));
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <Spinner className="py-20" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!job) return null;

  const candidateColumns = [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'status', label: 'Status', render: (row) => <Badge status={row.status} /> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-slate-900">{job.title}</h2>
            <Badge status={job.status} />
          </div>
          <p className="mt-1 text-slate-500">
            {job.department && `${job.department} · `}
            {job.location || 'No location'} · Created {formatDate(job.created_at)}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/upload?jobId=${id}`}>
            <Button variant="secondary"><Upload className="h-4 w-4" /> Upload Resumes</Button>
          </Link>
          <Link to={`/rankings/${id}`}>
            <Button variant="secondary"><Trophy className="h-4 w-4" /> Rankings</Button>
          </Link>
          <Link to={`/jobs/${id}/edit`}>
            <Button variant="secondary"><Edit className="h-4 w-4" /> Edit</Button>
          </Link>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="h-4 w-4" /> Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Description" />
          <p className="whitespace-pre-wrap text-sm text-slate-700">{job.description}</p>
        </Card>
        <Card>
          <CardHeader title="Requirements" />
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="font-medium text-slate-500">Shortlist Quota</dt>
              <dd className="text-slate-900">{job.shortlist_quota ?? 5} candidates</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-500">Min Experience</dt>
              <dd className="text-slate-900">{job.min_experience} years</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-500">Education</dt>
              <dd className="text-slate-900">{job.education || '—'}</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-500">Required Skills</dt>
              <dd className="mt-1 flex flex-wrap gap-1">
                {parseSkills(job.required_skills).map((s) => <SkillBadge key={s} skill={s} />)}
              </dd>
            </div>
            {job.preferred_skills && (
              <div>
                <dt className="font-medium text-slate-500">Preferred Skills</dt>
                <dd className="mt-1 flex flex-wrap gap-1">
                  {parseSkills(job.preferred_skills).map((s) => <SkillBadge key={s} skill={s} variant="semantic" />)}
                </dd>
              </div>
            )}
          </dl>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Candidates"
          subtitle={`${job.candidate_count} total`}
          action={
            <Link to={`/candidates?jobId=${id}`}>
              <Button variant="ghost" size="sm"><Users className="h-4 w-4" /> View All</Button>
            </Link>
          }
        />
        <Table
          columns={candidateColumns}
          data={candidates}
          onRowClick={(row) => navigate(`/candidates/${row.id}`)}
          emptyMessage="No candidates yet. Upload resumes to get started."
        />
      </Card>

      <Modal open={deleteOpen} onClose={() => setDeleteOpen(false)} title="Delete Job">
        <p className="text-sm text-slate-600">
          This will permanently delete the job and all associated candidates, resumes, and rankings.
        </p>
        <div className="mt-4 flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button variant="danger" loading={deleting} onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}
