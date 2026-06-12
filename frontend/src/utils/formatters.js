export function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatScore(score) {
  if (score == null) return '—';
  return `${Math.round(score)}%`;
}

export function formatPercent(value) {
  if (value == null) return '0%';
  return `${Math.round(value)}%`;
}

export function parseSkills(skillsStr) {
  if (!skillsStr) return [];
  return skillsStr.split(',').map((s) => s.trim()).filter(Boolean);
}

export function skillsToString(skills) {
  if (Array.isArray(skills)) return skills.join(', ');
  return skills || '';
}

export function toDatetimeLocalValue(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function fromDatetimeLocalValue(value) {
  if (!value) return null;
  return new Date(value).toISOString();
}

export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}
