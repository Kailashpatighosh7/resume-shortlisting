import { Check } from 'lucide-react';

const STEPS = [
  { id: 1, label: 'Upload Resume' },
  { id: 2, label: 'Upload Successful' },
  { id: 3, label: 'Show Ranking' },
  { id: 4, label: 'Send Email' },
];

export default function WorkflowStepper({ currentStep }) {
  return (
    <nav aria-label="Recruitment workflow progress" className="mb-8">
      <ol className="flex items-center justify-between gap-2">
        {STEPS.map((step, index) => {
          const done = currentStep > step.id;
          const active = currentStep === step.id;

          return (
            <li key={step.id} className="flex flex-1 items-center">
              <div className="flex flex-col items-center gap-2 text-center w-full">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition-colors ${
                    done
                      ? 'bg-emerald-500 text-white'
                      : active
                        ? 'bg-brand-600 text-white ring-4 ring-brand-100'
                        : 'bg-slate-200 text-slate-500'
                  }`}
                >
                  {done ? <Check className="h-4 w-4" /> : step.id}
                </div>
                <span
                  className={`hidden text-xs font-medium sm:block ${
                    active ? 'text-brand-700' : done ? 'text-emerald-700' : 'text-slate-500'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={`mx-1 h-0.5 flex-1 min-w-[12px] ${
                    currentStep > step.id ? 'bg-emerald-400' : 'bg-slate-200'
                  }`}
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
