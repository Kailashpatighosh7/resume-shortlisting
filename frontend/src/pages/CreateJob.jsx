import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { jobService } from '../services/jobService';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import Card from '../components/ui/Card';
import Spinner from '../components/ui/Spinner';
import { JOB_STATUSES } from '../utils/constants';
import { getApiErrorMessage } from '../utils/validators';

const emptyForm = {
  title: '',
  department: '',
  required_skills: '',
  preferred_skills: '',
  min_experience: 0,
  education: '',
  location: '',
  description: '',
  shortlist_quota: 5,
  status: 'open',
};

export default function CreateJob() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    jobService.get(id).then((job) => {
      setForm({
        title: job.title,
        department: job.department,
        required_skills: job.required_skills,
        preferred_skills: job.preferred_skills,
        min_experience: job.min_experience,
        education: job.education,
        location: job.location,
        description: job.description,
        shortlist_quota: job.shortlist_quota ?? 5,
        status: job.status,
      });
    }).catch((err) => setError(getApiErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: ['min_experience', 'shortlist_quota'].includes(name)
        ? parseInt(value, 10) || 0
        : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = { ...form };
      if (!isEdit) delete payload.status;
      const job = isEdit
        ? await jobService.update(id, payload)
        : await jobService.create(payload);
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner className="py-20" />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">{isEdit ? 'Edit Job' : 'Create Job'}</h2>
        <p className="text-slate-500">Define the role requirements for AI-powered matching</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          <Input label="Job Title" name="title" value={form.title} onChange={handleChange} required />
          <div className="grid gap-5 sm:grid-cols-2">
            <Input label="Department" name="department" value={form.department} onChange={handleChange} />
            <Input label="Location" name="location" value={form.location} onChange={handleChange} />
          </div>
          <Input
            label="Required Skills"
            name="required_skills"
            value={form.required_skills}
            onChange={handleChange}
            placeholder="Python, React, SQL (comma-separated)"
            required
          />
          <Input
            label="Preferred Skills"
            name="preferred_skills"
            value={form.preferred_skills}
            onChange={handleChange}
            placeholder="Docker, AWS (comma-separated)"
          />
          <div className="grid gap-5 sm:grid-cols-2">
            <Input label="Min Experience (years)" name="min_experience" type="number" min="0" value={form.min_experience} onChange={handleChange} />
            <Input
              label="Shortlist Quota"
              name="shortlist_quota"
              type="number"
              min="1"
              max="100"
              value={form.shortlist_quota}
              onChange={handleChange}
              required
            />
          </div>
          <Input label="Education" name="education" value={form.education} onChange={handleChange} placeholder="Bachelor's in CS" />
          <p className="-mt-3 text-xs text-slate-500">
            After ranking, the top {form.shortlist_quota} candidate(s) will be auto-shortlisted; remaining candidates will be rejected.
          </p>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Job Description</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={6}
              required
              minLength={10}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
              placeholder="Describe the role, responsibilities, and requirements..."
            />
          </div>
          {isEdit && (
            <Select label="Status" name="status" options={JOB_STATUSES} value={form.status} onChange={handleChange} />
          )}
          <div className="flex gap-3 pt-2">
            <Button type="submit" loading={saving}>{isEdit ? 'Save Changes' : 'Create Job'}</Button>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
