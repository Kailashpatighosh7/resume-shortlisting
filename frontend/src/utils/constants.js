export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const JOB_STATUSES = [
  { value: 'open', label: 'Open' },
  { value: 'closed', label: 'Closed' },
  { value: 'draft', label: 'Draft' },
];

export const CANDIDATE_STATUSES = [
  { value: 'new', label: 'New' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'interview', label: 'Interview' },
  { value: 'hired', label: 'Hired' },
];

export const INTERVIEW_MODES = [
  { value: 'video', label: 'Video' },
  { value: 'in-person', label: 'In Person' },
  { value: 'phone', label: 'Phone' },
];

export const INTERVIEW_STATUSES = [
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

export const EMAIL_TYPES = [
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'interview_scheduled', label: 'Interview Scheduled' },
  { value: 'custom', label: 'Custom' },
];

export const STATUS_COLORS = {
  new: 'bg-slate-100 text-slate-700',
  shortlisted: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-700',
  interview: 'bg-blue-100 text-blue-700',
  hired: 'bg-purple-100 text-purple-700',
  open: 'bg-emerald-100 text-emerald-700',
  closed: 'bg-slate-100 text-slate-600',
  draft: 'bg-amber-100 text-amber-700',
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-emerald-100 text-emerald-700',
  cancelled: 'bg-red-100 text-red-700',
  shortlisted_email: 'bg-emerald-100 text-emerald-700',
  interview_scheduled: 'bg-blue-100 text-blue-700',
  custom: 'bg-purple-100 text-purple-700',
};

export const ACCEPTED_RESUME_TYPES = '.pdf,.docx,.doc';
export const ACCEPTED_ZIP_TYPE = '.zip';
