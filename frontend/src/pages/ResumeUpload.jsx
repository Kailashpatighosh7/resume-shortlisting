import { useState, useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CheckCircle, Trophy, ArrowRight } from 'lucide-react';
import { useJobs } from '../hooks/useJobs';
import { useAuth } from '../contexts/AuthContext';
import { resumeService } from '../services/resumeService';
import { rankingService } from '../services/rankingService';
import { emailService } from '../services/emailService';
import Button from '../components/ui/Button';
import Select from '../components/ui/Select';
import Card from '../components/ui/Card';
import FileUploader from '../components/shared/FileUploader';
import ProcessingSteps from '../components/shared/ProcessingSteps';
import Spinner from '../components/ui/Spinner';
import { UPLOAD_PROCESSING_STEPS } from '../utils/processingSteps';
import WorkflowStepper from '../components/workflow/WorkflowStepper';
import RankingLeaderboard from '../components/workflow/RankingLeaderboard';
import EmailNotificationPanel from '../components/workflow/EmailNotificationPanel';
import { ACCEPTED_RESUME_TYPES, ACCEPTED_ZIP_TYPE } from '../utils/constants';
import { shortlistedEmailTemplate, rejectedEmailTemplate, personalizeTemplate } from '../utils/emailTemplates';
import { getApiErrorMessage } from '../utils/validators';

const STEP = {
  UPLOAD: 1,
  SUCCESS: 2,
  RANKING: 3,
  EMAILS: 4,
};

export default function ResumeUpload() {
  const [searchParams] = useSearchParams();
  const initialJobId = searchParams.get('jobId') || '';
  const { user } = useAuth();

  const { items: jobs, loading: jobsLoading } = useJobs({ perPage: 100, status: 'open' });

  const [currentStep, setCurrentStep] = useState(STEP.UPLOAD);
  const [jobId, setJobId] = useState(initialJobId);
  const [files, setFiles] = useState([]);
  const [zipFile, setZipFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('files');

  const [rankings, setRankings] = useState(null);
  const [rankingLoading, setRankingLoading] = useState(false);
  const [emailSentMap, setEmailSentMap] = useState({});
  const [emailTemplates, setEmailTemplates] = useState({ shortlisted: { subject: '', body: '' }, rejected: { subject: '', body: '' } });
  const [sendingId, setSendingId] = useState(null);
  const [sendingAll, setSendingAll] = useState(false);

  const jobOptions = jobs.map((j) => ({ value: String(j.id), label: j.title }));
  const selectedJob = jobs.find((j) => String(j.id) === jobId);
  const jobTitle = rankings?.job_title || selectedJob?.title || 'the position';
  const company = user?.company || '';

  const resetWorkflow = () => {
    setCurrentStep(STEP.UPLOAD);
    setUploadResult(null);
    setRankings(null);
    setEmailSentMap({});
    setFiles([]);
    setZipFile(null);
    setError('');
  };

  const initEmailTemplates = useCallback((title) => {
    setEmailTemplates({
      shortlisted: shortlistedEmailTemplate(title, company),
      rejected: rejectedEmailTemplate(title, company),
    });
  }, [company]);

  const handleUpload = async () => {
    if (!jobId) {
      setError('Please select a job');
      return;
    }
    setUploading(true);
    setError('');
    setUploadResult(null);
    try {
      const res = mode === 'files'
        ? await resumeService.upload(parseInt(jobId, 10), files)
        : await resumeService.uploadZip(parseInt(jobId, 10), zipFile);
      setUploadResult(res);
      setFiles([]);
      setZipFile(null);
      setCurrentStep(STEP.SUCCESS);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setUploading(false);
    }
  };

  const handleRankCandidates = async () => {
    setRankingLoading(true);
    setCurrentStep(STEP.RANKING);
    setError('');
    try {
      const result = await rankingService.rank(parseInt(jobId, 10));
      setRankings(result);
      initEmailTemplates(result.job_title);
    } catch (err) {
      setError(getApiErrorMessage(err));
      setCurrentStep(STEP.SUCCESS);
    } finally {
      setRankingLoading(false);
    }
  };

  const shortlistedList = useMemo(() => {
    if (!rankings?.rankings) return [];
    return rankings.rankings
      .filter((r) => r.status === 'shortlisted')
      .map((r) => ({ ...r, emailSent: emailSentMap[r.candidate_id] }));
  }, [rankings, emailSentMap]);

  const rejectedList = useMemo(() => {
    if (!rankings?.rankings) return [];
    return rankings.rankings
      .filter((r) => r.status === 'rejected')
      .map((r) => ({ ...r, emailSent: emailSentMap[r.candidate_id] }));
  }, [rankings, emailSentMap]);

  const buildEmailContent = (candidateName, type) => {
    const template = emailTemplates[type];
    return {
      subject: personalizeTemplate(template.subject, candidateName),
      body: personalizeTemplate(template.body, candidateName),
    };
  };

  const sendCandidateEmail = async (candidate, type) => {
    const { subject, body } = buildEmailContent(candidate.candidate_name, type);
    await emailService.send({
      candidate_id: candidate.candidate_id,
      job_id: parseInt(jobId, 10),
      email_type: type,
      subject,
      body,
    });
    setEmailSentMap((prev) => ({ ...prev, [candidate.candidate_id]: true }));
  };

  const handleSendEmail = async (candidate, type) => {
    if (!candidate.candidate_email) return;
    setSendingId(candidate.candidate_id);
    setError('');
    try {
      await sendCandidateEmail(candidate, type);
    } catch (err) {
      setError(getApiErrorMessage(err));
      throw err;
    } finally {
      setSendingId(null);
    }
  };

  const handleSendAll = async () => {
    setSendingAll(true);
    setError('');
    const toSend = [
      ...shortlistedList.filter((c) => !c.emailSent && c.candidate_email).map((c) => ({ ...c, type: 'shortlisted' })),
      ...rejectedList.filter((c) => !c.emailSent && c.candidate_email).map((c) => ({ ...c, type: 'rejected' })),
    ];
    try {
      for (const candidate of toSend) {
        await sendCandidateEmail(candidate, candidate.type);
      }
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setSendingAll(false);
    }
  };

  const handleContinueToEmails = () => {
    if (!emailTemplates.shortlisted.subject) {
      initEmailTemplates(jobTitle);
    }
    setCurrentStep(STEP.EMAILS);
  };

  if (jobsLoading) return <Spinner className="py-20" />;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Recruitment Workflow</h2>
        <p className="text-slate-500">Upload resumes, rank candidates, and send notifications</p>
      </div>

      <WorkflowStepper currentStep={currentStep} />

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      {/* Step 1: Upload Resume */}
      {currentStep === STEP.UPLOAD && (
        <Card>
          <Select
            label="Select Job"
            options={jobOptions}
            placeholder="Choose a job posting..."
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
          />

          <div className="mt-6 flex gap-2 border-b border-slate-200">
            {['files', 'zip'].map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => { setMode(m); setError(''); }}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  mode === m ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                {m === 'files' ? 'Individual Files' : 'ZIP Archive'}
              </button>
            ))}
          </div>

          <div className="mt-6">
            {mode === 'files' ? (
              <FileUploader
                accept={ACCEPTED_RESUME_TYPES}
                multiple
                onFilesSelected={setFiles}
                hint="PDF and DOCX files supported (max 10MB each)"
              />
            ) : (
              <FileUploader
                accept={ACCEPTED_ZIP_TYPE}
                multiple={false}
                onFilesSelected={(f) => setZipFile(f[0] || null)}
                label="Drag & drop a ZIP file here"
                hint="ZIP may contain PDF and DOCX files in any folder structure"
              />
            )}
          </div>

          {uploading && (
            <div className="mt-6">
              <ProcessingSteps
                active={uploading}
                steps={UPLOAD_PROCESSING_STEPS}
                title="Uploading resumes..."
              />
            </div>
          )}

          <div className="mt-6">
            <Button
              loading={uploading}
              disabled={mode === 'files' ? files.length === 0 : !zipFile}
              onClick={handleUpload}
            >
              Upload {mode === 'files' ? `${files.length} File(s)` : 'ZIP Archive'}
            </Button>
          </div>
        </Card>
      )}

      {/* Step 2: Upload Successful */}
      {currentStep === STEP.SUCCESS && uploadResult && (
        <Card>
          <div className="flex flex-col items-center py-8 text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
              <CheckCircle className="h-8 w-8 text-emerald-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Upload Successful</h3>
            <p className="mt-2 max-w-md text-sm text-slate-600">{uploadResult.message}</p>
            {uploadResult.candidates_created != null && (
              <p className="mt-1 text-sm text-emerald-700">
                {uploadResult.candidates_created} candidate(s) created
              </p>
            )}
            {uploadResult.processed != null && (
              <p className="mt-1 text-sm text-slate-500">
                {uploadResult.processed} processed, {uploadResult.failed} failed out of {uploadResult.total_files}
              </p>
            )}
            <p className="mt-4 text-sm text-slate-500">
              Resumes are ready. Proceed to rank candidates against the job requirements.
            </p>
            <Button
              className="mt-6"
              variant="success"
              loading={rankingLoading}
              onClick={handleRankCandidates}
            >
              <Trophy className="h-4 w-4" />
              Rank Candidates
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      )}

      {/* Step 3: Show Ranking */}
      {currentStep === STEP.RANKING && (
        <RankingLeaderboard
          rankings={rankings}
          loading={rankingLoading}
          onContinue={handleContinueToEmails}
        />
      )}

      {/* Step 4: Send Email */}
      {currentStep === STEP.EMAILS && (
        <EmailNotificationPanel
          shortlistedCandidates={shortlistedList}
          rejectedCandidates={rejectedList}
          emailTemplates={emailTemplates}
          onUpdateTemplate={(type, draft) =>
            setEmailTemplates((prev) => ({ ...prev, [type]: draft }))
          }
          onSendOne={handleSendEmail}
          onSendAll={handleSendAll}
          sendingId={sendingId}
          sendingAll={sendingAll}
          onFinish={resetWorkflow}
        />
      )}
    </div>
  );
}
