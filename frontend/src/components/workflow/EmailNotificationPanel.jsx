import { useState } from 'react';
import { Mail, Pencil, Send, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';
import Card, { CardHeader } from '../ui/Card';
import Modal from '../ui/Modal';
import ConfirmModal from '../shared/ConfirmModal';
import { personalizeTemplate } from '../../utils/emailTemplates';

function CandidateEmailList({ candidates, type, template, onEditTemplate, onRequestSend, sendingId }) {
  const isShortlisted = type === 'shortlisted';
  const borderColor = isShortlisted ? 'border-emerald-200' : 'border-orange-200';
  const headerBg = isShortlisted ? 'bg-emerald-50' : 'bg-orange-50';
  const headerText = isShortlisted ? 'text-emerald-800' : 'text-orange-800';
  const editVariant = isShortlisted ? 'success' : 'warning';

  if (!candidates.length) {
    return (
      <Card className={`${borderColor}`}>
        <div className={`rounded-t-xl ${headerBg} px-6 py-4`}>
          <h3 className={`font-semibold ${headerText}`}>
            {isShortlisted ? 'Shortlisted Candidates' : 'Rejected Candidates'}
          </h3>
        </div>
        <p className="p-6 text-sm text-slate-500">No candidates in this group.</p>
      </Card>
    );
  }

  return (
    <Card className={`overflow-hidden ${borderColor}`} padding={false}>
      <div className={`flex items-center justify-between ${headerBg} px-6 py-4`}>
        <div>
          <h3 className={`font-semibold ${headerText}`}>
            {isShortlisted ? 'Shortlisted Candidates' : 'Rejected Candidates'}
          </h3>
          <p className="text-sm text-slate-600">{candidates.length} candidate(s)</p>
        </div>
        <Button
          size="sm"
          variant={editVariant}
          onClick={() => onEditTemplate(type)}
        >
          <Pencil className="h-4 w-4" />
          Edit Email
        </Button>
      </div>

      <ul className="divide-y divide-slate-100">
        {candidates.map((c) => {
          const subject = personalizeTemplate(template.subject, c.candidate_name);
          const sent = c.emailSent;
          return (
            <li key={c.candidate_id} className="flex flex-wrap items-center justify-between gap-3 px-6 py-4">
              <div>
                <p className="font-medium text-slate-900">{c.candidate_name}</p>
                <p className="text-sm text-slate-500">{c.candidate_email || 'No email on file'}</p>
                <p className="mt-1 text-xs text-slate-400 truncate max-w-md">Subject: {subject}</p>
              </div>
              <div className="flex items-center gap-2">
                {sent ? (
                  <span className="flex items-center gap-1 text-sm text-emerald-600">
                    <CheckCircle className="h-4 w-4" /> Sent
                  </span>
                ) : (
                  <Button
                    size="sm"
                    loading={sendingId === c.candidate_id}
                    disabled={!c.candidate_email}
                    onClick={() => onRequestSend(c, type)}
                  >
                    <Send className="h-4 w-4" />
                    Send
                  </Button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

export default function EmailNotificationPanel({
  shortlistedCandidates,
  rejectedCandidates,
  emailTemplates,
  onUpdateTemplate,
  onSendOne,
  onSendAll,
  sendingId,
  sendingAll,
  onFinish,
}) {
  const [editType, setEditType] = useState(null);
  const [draft, setDraft] = useState({ subject: '', body: '' });
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAllOpen, setConfirmAllOpen] = useState(false);
  const [pendingSend, setPendingSend] = useState(null);

  const openEdit = (type) => {
    setEditType(type);
    setDraft({ ...emailTemplates[type] });
  };

  const saveTemplate = () => {
    onUpdateTemplate(editType, draft);
    setEditType(null);
  };

  const totalToSend =
    shortlistedCandidates.filter((c) => !c.emailSent && c.candidate_email).length +
    rejectedCandidates.filter((c) => !c.emailSent && c.candidate_email).length;

  const allSent =
    [...shortlistedCandidates, ...rejectedCandidates].every(
      (c) => c.emailSent || !c.candidate_email
    ) &&
    (shortlistedCandidates.length > 0 || rejectedCandidates.length > 0);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title="Send Notifications"
          subtitle="Review and customize emails before sending to candidates"
        />
        <p className="text-sm text-slate-500">
          Use <strong>Edit Email</strong> to customize the message template. Placeholders like the candidate name are applied automatically when sending.
        </p>
      </Card>

      <CandidateEmailList
        type="shortlisted"
        candidates={shortlistedCandidates}
        template={emailTemplates.shortlisted}
        onEditTemplate={openEdit}
        onRequestSend={(c, type) => { setPendingSend({ candidate: c, type }); setConfirmOpen(true); }}
        sendingId={sendingId}
      />

      <CandidateEmailList
        type="rejected"
        candidates={rejectedCandidates}
        template={emailTemplates.rejected}
        onEditTemplate={openEdit}
        onRequestSend={(c, type) => { setPendingSend({ candidate: c, type }); setConfirmOpen(true); }}
        sendingId={sendingId}
      />

      <div className="flex flex-wrap justify-between gap-3">
        <Button variant="secondary" onClick={onFinish}>
          Start New Workflow
        </Button>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            loading={sendingAll}
            disabled={totalToSend === 0}
            onClick={() => setConfirmAllOpen(true)}
          >
            <Mail className="h-4 w-4" />
            Send All ({totalToSend})
          </Button>
          {allSent && (
            <Button onClick={onFinish}>
              <CheckCircle className="h-4 w-4" />
              Done
            </Button>
          )}
        </div>
      </div>

      <ConfirmModal
        open={confirmOpen}
        onClose={() => { setConfirmOpen(false); setPendingSend(null); }}
        title="Send Email?"
        message={
          pendingSend
            ? `Do you want to send a ${pendingSend.type} email to ${pendingSend.candidate.candidate_name}?`
            : ''
        }
        confirmLabel="Yes, Send Email"
        loading={!!sendingId}
        onConfirm={async () => {
          if (pendingSend) {
            await onSendOne(pendingSend.candidate, pendingSend.type);
            setConfirmOpen(false);
            setPendingSend(null);
          }
        }}
      />
      <ConfirmModal
        open={confirmAllOpen}
        onClose={() => setConfirmAllOpen(false)}
        title="Send All Emails?"
        message={`Do you want to send emails to ${totalToSend} candidate(s)? This action cannot be undone.`}
        confirmLabel={`Send All (${totalToSend})`}
        loading={sendingAll}
        onConfirm={async () => {
          await onSendAll();
          setConfirmAllOpen(false);
        }}
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
              The greeting will use each candidate&apos;s name when the email is sent.
            </p>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setEditType(null)}>Cancel</Button>
            <Button onClick={saveTemplate}>Save Template</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
