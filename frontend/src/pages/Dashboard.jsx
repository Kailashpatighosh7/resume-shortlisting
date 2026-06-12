import { Link } from 'react-router-dom';
import { Briefcase, Users, Calendar, TrendingUp, Plus, Upload } from 'lucide-react';
import { useAnalytics } from '../hooks/useAnalytics';
import StatCard from '../components/charts/StatCard';
import LineChartCard from '../components/charts/LineChartCard';
import BarChartCard from '../components/charts/BarChartCard';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import Button from '../components/ui/Button';
import Card, { CardHeader } from '../components/ui/Card';
import { formatPercent } from '../utils/formatters';

export default function Dashboard() {
  const { data, loading, error, refetch } = useAnalytics();

  if (loading) return <Spinner className="py-20" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { stats, monthly_activity, top_skills, status_distribution } = data;

  const activityData = monthly_activity?.map((m) => ({
    month: m.month,
    jobs: m.jobs_created,
    candidates: m.candidates_added,
    interviews: m.interviews_scheduled,
  })) || [];

  const skillsData = top_skills?.slice(0, 8).map((s) => ({
    skill: s.skill,
    count: s.count,
  })) || [];

  const statusData = status_distribution?.map((s) => ({
    name: s.status || s.name,
    value: s.count || s.value,
  })) || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Dashboard</h2>
          <p className="text-slate-500">Overview of your hiring pipeline</p>
        </div>
        <div className="flex gap-3">
          <Link to="/jobs/new">
            <Button><Plus className="h-4 w-4" /> New Job</Button>
          </Link>
          <Link to="/upload">
            <Button variant="secondary"><Upload className="h-4 w-4" /> Upload</Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Jobs" value={stats.total_jobs} icon={Briefcase} />
        <StatCard title="Total Candidates" value={stats.total_candidates} icon={Users} />
        <StatCard title="Interviews" value={stats.total_interviews} icon={Calendar} />
        <StatCard
          title="Avg Match Score"
          value={formatPercent(stats.average_match_score)}
          subtitle={`${stats.shortlisted_candidates} shortlisted`}
          icon={TrendingUp}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <LineChartCard
          title="Monthly Activity"
          subtitle="Jobs, candidates, and interviews over time"
          data={activityData}
          lines={[
            { key: 'jobs', color: '#6366f1', name: 'Jobs' },
            { key: 'candidates', color: '#10b981', name: 'Candidates' },
            { key: 'interviews', color: '#f59e0b', name: 'Interviews' },
          ]}
        />
        <BarChartCard
          title="Top Skills"
          subtitle="Most common skills across candidates"
          data={skillsData}
          nameKey="skill"
          dataKey="count"
        />
      </div>

      {statusData.length > 0 && (
        <Card>
          <CardHeader title="Candidate Status Breakdown" subtitle="Distribution by pipeline stage" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {statusData.map((s) => (
              <div key={s.name} className="rounded-lg bg-slate-50 p-4 text-center">
                <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                <p className="mt-1 text-sm capitalize text-slate-500">{s.name}</p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
