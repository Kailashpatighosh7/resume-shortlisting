export default function SkillBadge({ skill, variant = 'default' }) {
  const variants = {
    default: 'bg-slate-100 text-slate-700',
    matched: 'bg-emerald-100 text-emerald-700',
    missing: 'bg-red-100 text-red-700',
    semantic: 'bg-blue-100 text-blue-700',
  };

  return (
    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${variants[variant]}`}>
      {skill}
    </span>
  );
}
