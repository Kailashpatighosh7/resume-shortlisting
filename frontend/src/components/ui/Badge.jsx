import { STATUS_COLORS } from '../../utils/constants';
import { capitalize } from '../../utils/formatters';

export default function Badge({ status, children, className = '' }) {
  const colorClass = STATUS_COLORS[status] || 'bg-slate-100 text-slate-700';
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass} ${className}`}>
      {children || capitalize(status)}
    </span>
  );
}
