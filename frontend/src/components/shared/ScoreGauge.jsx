export default function ScoreGauge({ score, size = 'md' }) {
  const value = Math.min(100, Math.max(0, score ?? 0));
  const color = value >= 75 ? '#10b981' : value >= 50 ? '#f59e0b' : '#ef4444';
  const sizes = { sm: 48, md: 72, lg: 96 };
  const dim = sizes[size];
  const stroke = size === 'sm' ? 4 : 6;
  const radius = (dim - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: dim, height: dim }}>
      <svg width={dim} height={dim} className="-rotate-90">
        <circle cx={dim / 2} cy={dim / 2} r={radius} fill="none" stroke="#e2e8f0" strokeWidth={stroke} />
        <circle
          cx={dim / 2}
          cy={dim / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className={`absolute font-bold text-slate-900 ${size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-xl' : 'text-sm'}`}>
        {Math.round(value)}%
      </span>
    </div>
  );
}
