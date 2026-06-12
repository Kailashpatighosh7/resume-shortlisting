import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../ui/Button';

export default function Navbar({ title, subtitle }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-8 py-4">
      <div>
        {title && <h1 className="text-xl font-semibold text-slate-900">{title}</h1>}
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100">
            <User className="h-4 w-4 text-brand-600" />
          </div>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
            <p className="text-xs text-slate-500">{user?.company || user?.email}</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={logout} title="Logout">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
