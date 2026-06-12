import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Send, CheckCircle, XCircle, Pencil } from 'lucide-react';
import { useEmailStats, useEmailLogs } from '../hooks/useEmails';
import { useJobs } from '../hooks/useJobs';
import { useCandidates } from '../hooks/useCandidates';
import { useAuth } from '../contexts/AuthContext';
import { emailService } from '../services/emailService';
import StatCard from '../components/charts/StatCard';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import Card, { CardHeader } from '../components/ui/Card';
import Table from '../components/ui/Table';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import ConfirmModal from '../components/shared/ConfirmModal';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import { formatDateTime, capitalize } from '../utils/formatters';
import { shortlistedEmailTemplate, rejectedEmailTemplate, personalizeTemplate } from '../utils/emailTemplates';
import { getApiErrorMessage } from '../utils/validators';

function CandidateSection({
  title,
  titleClass,
  borderClass,
  headerBg,
  candidates,
  type,
  template,
  onEdit,
  onRequestSend,
  sendingId,
}) {
  const editVariant = type === 'shortlisted' ? 'success' : 'warning';
  return (
    <div className={`rounded-xl border ${borderClass} overflow-hidden`}>
      <div className={`flex items-center justify-between ${headerBg} px-4 py-3`}>
        <h4 className={`text-sm font-semibold ${titleClass}`}>{title} ({candidates.length})</h4>
        <Button size="sm" variant={editVariant} onClick={() => onEdit(type)}>
          <Pencil className="h-3 w-3" /> Edit Email
        </Button>
      </div>
      {candidates.length === 0 ? (
        <p className="p-4 text-sm text-slate-500">No candidates in this group.</p>
) : (
        <ul className="divide-y divide-slate-100 bg-white">
          {candidates.map((c) => (
            <li key={c.id} className="flex items-center justify-between gap-3 px-4 py-3">
              <div className="min-w-0">
                <Link to={`/candidates/${c.id}`} className="text-sm font-medium text-brand-600 hover:underline">
                  {c.name}
                </Link>
                <p className="text-xs text-slate-500">{c.email || 'No email'}</p>
                <p className="mt-0.5 truncate text-xs text-slate-400">
                  Subject: {personalizeTemplate(template.subject, c.name)}
                </p>
              </div>
              <Button
                size="sm"
                variant={editVariant}
                disabled={!c.email}
                loading={sendingId === c.id}
                onClick={() => onRequestSend(c, type)}
              >
                <Send className="h-3 w-3" /> Send
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Emails() {
  const { user } = useAuth();
  const { stats, loading: statsLoading, error: statsError, refetch: refetchStats } = useEmailStats();
  const { items: logs, loading: logsLoading, refetch: refetchLogs } = useEmailLogs({ limit: 50 });
  const { items: jobs } = useJobs({ perPage: 100 });

  const [selectedJobId, setSelectedJobId] = useState('');
  const [emailTemplates, setEmailTemplates] = useState({
    shortlisted: { subject: '', body: '' },
    rejected: { subject: '', body: '' },
  });
  const [editType, setEditType] = useState(null);
  const [draft, setDraft] = useState({ subject: '', body: '' });
  const [sendingId, setSendingId] = useState(null);
  const [sendingAll, setSendingAll] = useState(false);
  const [sendError, setSendError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAllOpen, setConfirmAllOpen] = useState(false);
  const [pendingSend, setPendingSend] = useState(null);
  const selectedJob = jobs.find((j) => String(j.id) === selectedJobId);
  useEffect(() => {
    if (!selectedJob) return;
    setEmailTemplates({
      shortlisted: shortlistedEmailTemplate(selectedJob.title, user?.company || ''),
      rejected: rejectedEmailTemplate(selectedJob.title, user?.company || ''),
    });
  }, [selectedJob, user?.company]);

  const { items: shortlisted } = useCandidates({
    jobId: selectedJobId ? parseInt(selectedJobId, 10) : undefined,
    status: 'shortlisted',
    perPage: 200,
  });
  const { items: rejected } = useCandidates({
    jobId: selectedJobId ? parseInt(selectedJobId, 10) : undefined,
    status: 'rejected',
    perPage: 200,
  });

  const jobOptions = jobs.map((j) => ({ value: String(j.id), label: j.title }));

  const sendable = useMemo(
    () => [...shortlisted, ...rejected].filter((c) => c.email),
    [shortlisted, rejected]
  );
  const buildEmailContent = (candidateName, type) => {
    const template = emailTemplates[type];
    return {
      subject: personalizeTemplate(template.subject, candidateName),
      body: personalizeTemplate(template.body, candidateName),
    };
  };
  const sendToCandidate = async (candidate, type) => {
    const { subject, body } = buildEmailContent(candidate.name, type);
    await emailService.send({
      candidate_id: candidate.id,
      job_id: parseInt(selectedJobId, 10),
      email_type: type,
      subject,
      body,
    });
  };
  const handleConfirmSend = async () => {
    if (!pendingSend) return;
    setSendingId(pendingSend.candidate.id);
    setSendError('');
    try {
      await sendToCandidate(pendingSend.candidate, pendingSend.type);
      setConfirmOpen(false);
      setPendingSend(null);
      refetchStats();
      refetchLogs();
    } catch (err) {
      setSendError(getApiErrorMessage(err));
    } finally {
      setSendingId(null);
    }
  };

  const handleSendAll = async () => {
    setSendingAll(true);
    setSendError('');
    try {
      for (const c of shortlisted.filter((x) => x.email)) {
        await sendToCandidate(c, 'shortlisted');
      }
      for (const c of rejected.filter((x) => x.email)) {
        await sendToCandidate(c, 'rejected');
      }
      setConfirmAllOpen(false);
      refetchStats();
      refetchLogs();
    } catch (err) {
      setSendError(getApiErrorMessage(err));
    } finally {
      setSendingAll(false);
    }
  };

  const openEdit = (type) => {
    setEditType(type);
    setDraft({ ...emailTemplates[type] });
  };

  const logColumns = [
    { key: 'recipient_email', label: 'Recipient' },
    { key: 'email_type', label: 'Type', render: (row) => <Badge status={row.email_type} /> },
    { key: 'subject', label: 'Subject', render: (row) => (
      <span className="max-w-xs truncate block">{row.subject}</span>
    )},
    { key: 'status', label: 'Status', render: (row) => (
      <span className={row.status === 'sent' ? 'text-emerald-600' : 'text-red-600'}>
        {capitalize(row.status)}
      </span>
    )},
    { key: 'sent_at', label: 'Sent', render: (row) => formatDateTime(row.sent_at) },
  ];

  if (statsLoading) return <Spinner className="py-20" />;
  if (statsError) return <ErrorState message={statsError} onRetry={refetchStats} />;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Emails</h2>
        <p className="text-slate-500">Email sending stats and notifications by job</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Emails" value={stats.total} icon={Mail} />
        <StatCard title="Successfully Sent" value={stats.sent} icon={CheckCircle} />
        <StatCard title="Failed" value={stats.failed} icon={XCircle} />
        <StatCard
          title="Shortlist / Reject"
          value={`${stats.shortlisted} / ${stats.rejected}`}
          subtitle={`${stats.interview_scheduled} interview emails`}
        />
      </div>

      <Card>
      <CardHeader title="Send Emails by Job" subtitle="Select a job, edit templates, and notify candidates" />
        <Select
          label="Select Job"
          options={jobOptions}
          placeholder="Choose a job..."
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
          className="max-w-md"
        />

        {sendError && (
          <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{sendError}</div>
        )}

        {selectedJobId && (
        <>
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <CandidateSection
            title="Shortlisted"
            titleClass="text-emerald-700"
            borderClass="border-emerald-200"
            headerBg="bg-emerald-50"
            candidates={shortlisted}
            type="shortlisted"
            template={emailTemplates.shortlisted}
            onEdit={openEdit}
            onRequestSend={(c, type) => { setPendingSend({ candidate: c, type }); setConfirmOpen(true); }}
            sendingId={sendingId}
          />
          <CandidateSection
            title="Rejected"
            titleClass="text-orange-700"
            borderClass="border-orange-200"
            headerBg="bg-orange-50"
            candidates={rejected}
            type="rejected"
            template={emailTemplates.rejected}
            onEdit={openEdit}
            onRequestSend={(c, type) => { setPendingSend({ candidate: c, type }); setConfirmOpen(true); }}
            sendingId={sendingId}
          />
          </div>

            {sendable.length > 0 && (
              <div className="mt-6 flex justify-end">
                <Button onClick={() => setConfirmAllOpen(true)} loading={sendingAll}>
                  <Mail className="h-4 w-4" />
                  Send All ({sendable.length})
                </Button>
              </div>
            )}
        </>
        )}
      </Card>

      <Card padding={false}>
        <div className="border-b border-slate-200 px-6 py-4">
          <CardHeader title="Recent Email Log" subtitle={`${logs.length} recent entries`} />
        </div>
        {logsLoading ? (
          <Spinner className="py-12" />
        ) : (
          <Table columns={logColumns} data={logs} emptyMessage="No emails sent yet" />
        )}
      </Card>

      <ConfirmModal
        open={confirmOpen}
        onClose={() => { setConfirmOpen(false); setPendingSend(null); setSendError(''); }}
        title="Send Email?"
        message={
          pendingSend
            ? `Do you want to send a ${pendingSend.type} email to ${pendingSend.candidate.name}?`
            : ''
        }
        confirmLabel="Yes, Send Email"
        loading={!!sendingId}
        onConfirm={handleConfirmSend}
      />

      <ConfirmModal
        open={confirmAllOpen}
        onClose={() => setConfirmAllOpen(false)}
        title="Send All Emails?"
        message={`Do you want to send emails to ${sendable.length} candidate(s)? This will notify all shortlisted and rejected candidates for this job.`}
        confirmLabel={`Send All (${sendable.length})`}
        loading={sendingAll}
        onConfirm={handleSendAll}
      />

      <Modal
        open={!!editType}
        onClose={() => setEditType(null)}
        title={editType === 'shortlisted' ? 'Edit Shortlist Email' : 'Edit Rejection Email'}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Subject</label>
            <input
              value={draft.subject}
              onChange={(e) => setDraft((d) => ({ ...d, subject: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />          
          </div>
          
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Body</label>
            <textarea
              value={draft.body}
              onChange={(e) => setDraft((d) => ({ ...d, body: e.target.value }))}
              rows={12}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
            <p className="mt-1 text-xs text-slate-500">
              Use {'{candidate_name}'} as a placeholder for the candidate&apos;s name.
            </p>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setEditType(null)}>Cancel</Button>
            <Button onClick={() => { setEmailTemplates((p) => ({ ...p, [editType]: draft })); setEditType(null); }}>
              Save Template
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
