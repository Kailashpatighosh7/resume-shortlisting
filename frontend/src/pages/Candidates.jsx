import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, Users } from 'lucide-react';
import { useCandidates } from '../hooks/useCandidates';
import { useJobs } from '../hooks/useJobs';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Table from '../components/ui/Table';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import Button from '../components/ui/Button';
import { CANDIDATE_STATUSES } from '../utils/constants';
import { formatDate } from '../utils/formatters';

export default function Candidates() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialJobId = searchParams.get('jobId') || '';

  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [jobId, setJobId] = useState(initialJobId);
  const [page, setPage] = useState(1);

  const { items: jobs } = useJobs({ perPage: 100 });
  const { items, total, per_page, loading, error, refetch } = useCandidates({
    jobId: jobId ? parseInt(jobId, 10) : undefined,
    page,
    perPage: 50,
    status: status || undefined,
    search: search || undefined,
  });

  const jobOptions = jobs.map((j) => ({ value: String(j.id), label: j.title }));

  const columns = [
    { key: 'name', label: 'Name', render: (row) => (
      <div>
        <p className="font-medium text-slate-900">{row.name}</p>
        <p className="text-xs text-slate-500">{row.email || '—'}</p>
      </div>
    )},
    { key: 'phone', label: 'Phone' },
    { key: 'status', label: 'Status', render: (row) => <Badge status={row.status} /> },
    { key: 'created_at', label: 'Added', render: (row) => formatDate(row.created_at) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Candidates</h2>
        <p className="text-slate-500">{total} candidates</p>
      </div>

      <div className="space-y-4">
        <div className="relative">      
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9"
          />
        </div>
        <div className="flex gap-4">
          <div className="w-[80%]">
            <Select
              options={jobOptions}
              placeholder="All jobs"
              value={jobId}
              onChange={(e) => { setJobId(e.target.value); setPage(1); }}
            />
          </div>
          <div className="w-[20%] min-w-[140px]">
            <Select
              options={CANDIDATE_STATUSES}
              placeholder="All statuses"
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            />
          </div>
        </div>
      </div>

      {loading ? (
        <Spinner className="py-20" />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No candidates found"
          description="Upload resumes for a job to see candidates here."
        />
      ) : (
        <>
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <Table columns={columns} data={items} onRowClick={(row) => navigate(`/candidates/${row.id}`)} />
          </div>
          {total > per_page && (
            <div className="flex justify-center gap-2">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
              <span className="flex items-center px-4 text-sm text-slate-500">Page {page} of {Math.ceil(total / per_page)}</span>
              <Button variant="secondary" size="sm" disabled={page >= Math.ceil(total / per_page)} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
