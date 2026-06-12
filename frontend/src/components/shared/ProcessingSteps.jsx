import { useEffect, useState } from 'react';
import { CheckCircle, Loader2, Circle } from 'lucide-react';
export default function ProcessingSteps({ steps, active, title = 'Processing...' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  useEffect(() => {
    if (!active) {
      setCurrentIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 1800);
    return () => clearInterval(interval);
  }, [active, steps.length]);
  
if (!active) return null;
return (
  <div className="rounded-xl border border-brand-200 bg-brand-50/50 p-6">
    <p className="mb-4 text-sm font-semibold text-brand-800">{title}</p>
    <ul className="space-y-3">
      {steps.map((step, index) => {
        const done = index < currentIndex;
        const current = index === currentIndex;
        return (
          <li key={step} className="flex items-center gap-3 text-sm">
            {done ? (
              <CheckCircle className="h-5 w-5 shrink-0 text-emerald-500" />
            ) : current ? (
              <Loader2 className="h-5 w-5 shrink-0 animate-spin text-brand-600" />
            ) : (
              <Circle className="h-5 w-5 shrink-0 text-slate-300" />
            )}
            <span
              className={
                done
                  ? 'text-emerald-700'
                  : current
                    ? 'font-medium text-brand-800'
                    : 'text-slate-400'
              }
            >
              {step}
            </span>
          </li>
        );
      })}
    </ul>
  </div>
);
}