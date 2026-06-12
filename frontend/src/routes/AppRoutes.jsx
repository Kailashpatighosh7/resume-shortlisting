import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import AppLayout from '../components/layout/AppLayout';

import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Jobs from '../pages/Jobs';
import CreateJob from '../pages/CreateJob';
import JobDetails from '../pages/JobDetails';
import Candidates from '../pages/Candidates';
import CandidateDetails from '../pages/CandidateDetails';
import ResumeUpload from '../pages/ResumeUpload';
import Rankings from '../pages/Rankings';
import Emails from '../pages/Emails';
import Interviews from '../pages/Interviews';
import Analytics from '../pages/Analytics';
import Settings from '../pages/Settings';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="jobs/new" element={<CreateJob />} />
        <Route path="jobs/:id" element={<JobDetails />} />
        <Route path="jobs/:id/edit" element={<CreateJob />} />
        <Route path="candidates" element={<Candidates />} />
        <Route path="candidates/:id" element={<CandidateDetails />} />
        <Route path="upload" element={<ResumeUpload />} />
        <Route path="rankings" element={<Rankings />} />
        <Route path="rankings/:jobId" element={<Rankings />} />
        <Route path="emails" element={<Emails />} />
        <Route path="interviews" element={<Interviews />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
