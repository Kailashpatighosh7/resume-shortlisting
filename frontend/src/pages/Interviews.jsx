import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plus, Calendar } from 'lucide-react';
import { useInterviews } from '../hooks/useInterviews';
import { useJobs } from '../hooks/useJobs';
import { useCandidates } from '../hooks/useCandidates';
import { interviewService } from '../services/interviewService';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import Input from '../components/ui/Input';
import Table from '../components/ui/Table';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import { INTERVIEW_MODES, INTERVIEW_STATUSES } from '../utils/constants';
import { formatDateTime, fromDatetimeLocalValue } from '../utils/formatters';
import { getApiErrorMessage } from '../utils/validators';

export default function Interviews() {
  const [searchParams] = useSearchParams();
  const initialCandidateId = searchParams.get('candidateId') || '';
  const initialJobId = searchParams.get('jobId') || '';

  const [statusFilter, setStatusFilter] = useState('');
  const [createOpen, setCreateOpen] = useState(Boolean(initialCandidateId));
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    candidate_id: initialCandidateId,
    job_id: initialJobId,
    scheduled_at: '',
    mode: 'video',
    meeting_link: '',
    notes: '',
  });

  const { items, loading, error, refetch } = useInterviews({
    status: statusFilter || undefined,
  });
  const { items: jobs } = useJobs({ perPage: 100 });
  const { items: candidates } = useCandidates({
    jobId: form.job_id ? parseInt(form.job_id, 10) : undefined,
    perPage: 200,
  });

  const jobOptions = jobs.map((j) => ({ value: String(j.id), label: j.title }));
  const candidateOptions = candidates.map((c) => ({ value: String(c.id), label: c.name }));

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await interviewService.create({
        candidate_id: parseInt(form.candidate_id, 10),
        job_id: parseInt(form.job_id, 10),
        scheduled_at: fromDatetimeLocalValue(form.scheduled_at),
        mode: form.mode,
        meeting_link: form.meeting_link,
        notes: form.notes,
      });
      setCreateOpen(false);
      refetch();
    } catch (err) {
      alert(getApiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleStatusUpdate = async (interview, newStatus) => {
    try {
      await interviewService.update(interview.id, { status: newStatus });
      refetch();
    } catch (err) {
      alert(getApiErrorMessage(err));
    }
  };

  const columns = [
    { key: 'candidate_name', label: 'Candidate' },
    { key: 'job_title', label: 'Job' },
    { key: 'scheduled_at', label: 'Scheduled', render: (row) => formatDateTime(row.scheduled_at) },
    { key: 'mode', label: 'Mode', render: (row) => <span className="capitalize">{row.mode}</span> },
    { key: 'status', label: 'Status', render: (row) => <Badge status={row.status} /> },
    { key: 'actions', label: '', render: (row) => (
      row.status === 'scheduled' && (
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" onClick={() => handleStatusUpdate(row, 'completed')}>Complete</Button>
          <Button variant="ghost" size="sm" onClick={() => handleStatusUpdate(row, 'cancelled')}>Cancel</Button>
        </div>
      )
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Interviews</h2>
          <p className="text-slate-500">Schedule and manage candidate interviews</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}><Plus className="h-4 w-4" /> Schedule Interview</Button>
      </div>

      <Select
        options={INTERVIEW_STATUSES}
        placeholder="All statuses"
        value={statusFilter}
        onChange={(e) => setStatusFilter(e.target.value)}
        className="w-40"
      />

      {loading ? (
        <Spinner className="py-20" />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No interviews scheduled"
          description="Schedule your first interview with a shortlisted candidate."
          action={<Button onClick={() => setCreateOpen(true)}><Plus className="h-4 w-4" /> Schedule Interview</Button>}
        />
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <Table columns={columns} data={items} />
        </div>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Schedule Interview" size="lg">
        <form onSubmit={handleCreate} className="space-y-4">
          <Select
            label="Job"
            options={jobOptions}
            placeholder="Select job..."
            value={form.job_id}
            onChange={(e) => setForm((p) => ({ ...p, job_id: e.target.value, candidate_id: '' }))}
            required
          />
          <Select
            label="Candidate"
            options={candidateOptions}
            placeholder="Select candidate..."
            value={form.candidate_id}
            onChange={(e) => setForm((p) => ({ ...p, candidate_id: e.target.value }))}
            required
          />
          <Input
            label="Date & Time"
            type="datetime-local"
            value={form.scheduled_at}
            onChange={(e) => setForm((p) => ({ ...p, scheduled_at: e.target.value }))}
            required
          />
          <Select
            label="Mode"
            options={INTERVIEW_MODES}
            value={form.mode}
            onChange={(e) => setForm((p) => ({ ...p, mode: e.target.value }))}
          />
          <Input
            label="Meeting Link"
            value={form.meeting_link}
            onChange={(e) => setForm((p) => ({ ...p, meeting_link: e.target.value }))}
            placeholder="https://meet.google.com/..."
          />
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))}
              rows={3}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button type="submit" loading={saving}>Schedule</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
