import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Search, Briefcase } from 'lucide-react';
import { useJobs } from '../hooks/useJobs';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Table from '../components/ui/Table';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import { JOB_STATUSES } from '../utils/constants';
import { formatDate } from '../utils/formatters';

export default function Jobs() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);

  const { items, total, per_page, loading, error, refetch } = useJobs({
    page,
    perPage: 20,
    status: status || undefined,
    search: search || undefined,
  });

  const columns = [
    { key: 'title', label: 'Title', render: (row) => (
      <div>
        <p className="font-medium text-slate-900">{row.title}</p>
        <p className="text-xs text-slate-500">{row.department || '—'}</p>
      </div>
    )},
    { key: 'location', label: 'Location' },
    { key: 'candidate_count', label: 'Candidates' },
    { key: 'status', label: 'Status', render: (row) => <Badge status={row.status} /> },
    { key: 'created_at', label: 'Created', render: (row) => formatDate(row.created_at) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Jobs</h2>
          <p className="text-slate-500">{total} job postings</p>
        </div>
        <Link to="/jobs/new">
          <Button><Plus className="h-4 w-4" /> Create Job</Button>
        </Link>
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search jobs..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9"
          />
        </div>
        <Select
          options={JOB_STATUSES}
          placeholder="All statuses"
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="w-40"
        />
      </div>

      {loading ? (
        <Spinner className="py-20" />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No jobs yet"
          description="Create your first job posting to start screening candidates."
          action={<Link to="/jobs/new"><Button>Create Job</Button></Link>}
        />
      ) : (
        <>
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <Table columns={columns} data={items} onRowClick={(row) => navigate(`/jobs/${row.id}`)} />
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
