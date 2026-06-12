import { useAnalytics } from '../hooks/useAnalytics';
import StatCard from '../components/charts/StatCard';
import BarChartCard from '../components/charts/BarChartCard';
import PieChartCard from '../components/charts/PieChartCard';
import LineChartCard from '../components/charts/LineChartCard';
import Card, { CardHeader } from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';
import ErrorState from '../components/ui/ErrorState';
import { Briefcase, Users, Calendar, Mail, TrendingUp, UserCheck } from 'lucide-react';
import { formatPercent } from '../utils/formatters';

export default function Analytics() {
  const { data, loading, error, refetch } = useAnalytics();

  if (loading) return <Spinner className="py-20" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { stats, top_skills, monthly_activity, score_distribution, status_distribution } = data;

  const activityData = monthly_activity?.map((m) => ({
    month: m.month,
    jobs: m.jobs_created,
    candidates: m.candidates_added,
    interviews: m.interviews_scheduled,
  })) || [];

  const skillsData = top_skills?.map((s) => ({ skill: s.skill, count: s.count })) || [];

  const scoreData = score_distribution?.map((s) => ({
    range: s.range || s.label || s.name,
    count: s.count || s.value,
  })) || [];

  const statusData = status_distribution?.map((s) => ({
    name: s.status || s.name,
    value: s.count || s.value,
  })) || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Analytics</h2>
        <p className="text-slate-500">Hiring pipeline insights and trends</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard title="Total Jobs" value={stats.total_jobs} icon={Briefcase} />
        <StatCard title="Total Candidates" value={stats.total_candidates} icon={Users} />
        <StatCard title="Interviews" value={stats.total_interviews} icon={Calendar} />
        <StatCard title="Emails Sent" value={stats.emails_sent} icon={Mail} />
        <StatCard title="Avg Match Score" value={formatPercent(stats.average_match_score)} icon={TrendingUp} />
        <StatCard
          title="Interview Conversion"
          value={formatPercent(stats.interview_conversion_rate)}
          subtitle={`${stats.shortlisted_candidates} shortlisted`}
          icon={UserCheck}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <LineChartCard
          title="Monthly Activity"
          data={activityData}
          lines={[
            { key: 'jobs', color: '#6366f1', name: 'Jobs Created' },
            { key: 'candidates', color: '#10b981', name: 'Candidates Added' },
            { key: 'interviews', color: '#f59e0b', name: 'Interviews' },
          ]}
        />
        <BarChartCard title="Top Skills" data={skillsData.slice(0, 10)} nameKey="skill" dataKey="count" color="#10b981" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {scoreData.length > 0 && (
          <BarChartCard title="Score Distribution" data={scoreData} nameKey="range" dataKey="count" color="#8b5cf6" />
        )}
        {statusData.length > 0 && (
          <PieChartCard title="Candidate Status" data={statusData} />
        )}
      </div>
    </div>
  );
}
