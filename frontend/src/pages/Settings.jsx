import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card, { CardHeader } from '../components/ui/Card';
import { getApiErrorMessage, validatePassword } from '../utils/validators';

export default function Settings() {
  const { user, updateProfile } = useAuth();

  const [profile, setProfile] = useState({
    full_name: user?.full_name || '',
    company: user?.company || '',
  });
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [profileSaving, setProfileSaving] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');
  const [profileError, setProfileError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setProfileSaving(true);
    setProfileError('');
    setProfileMsg('');
    try {
      await updateProfile(profile);
      setProfileMsg('Profile updated successfully');
    } catch (err) {
      setProfileError(getApiErrorMessage(err));
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordMsg('');

    if (!validatePassword(passwords.new_password)) {
      setPasswordError('New password must be at least 8 characters');
      return;
    }
    if (passwords.new_password !== passwords.confirm_password) {
      setPasswordError('Passwords do not match');
      return;
    }

    setPasswordSaving(true);
    try {
      await authService.changePassword(passwords.current_password, passwords.new_password);
      setPasswordMsg('Password changed successfully');
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setPasswordError(getApiErrorMessage(err));
    } finally {
      setPasswordSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Settings</h2>
        <p className="text-slate-500">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader title="Profile" subtitle={user?.email} />
        {profileMsg && <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{profileMsg}</div>}
        {profileError && <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{profileError}</div>}
        <form onSubmit={handleProfileSave} className="space-y-4">
          <Input
            label="Full Name"
            value={profile.full_name}
            onChange={(e) => setProfile((p) => ({ ...p, full_name: e.target.value }))}
            required
          />
          <Input
            label="Company"
            value={profile.company}
            onChange={(e) => setProfile((p) => ({ ...p, company: e.target.value }))}
          />
          <Button type="submit" loading={profileSaving}>Save Profile</Button>
        </form>
      </Card>

      <Card>
        <CardHeader title="Change Password" />
        {passwordMsg && <div className="mb-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{passwordMsg}</div>}
        {passwordError && <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{passwordError}</div>}
        <form onSubmit={handlePasswordChange} className="space-y-4">
          <Input
            label="Current Password"
            type="password"
            value={passwords.current_password}
            onChange={(e) => setPasswords((p) => ({ ...p, current_password: e.target.value }))}
            required
          />
          <Input
            label="New Password"
            type="password"
            value={passwords.new_password}
            onChange={(e) => setPasswords((p) => ({ ...p, new_password: e.target.value }))}
            required
          />
          <Input
            label="Confirm New Password"
            type="password"
            value={passwords.confirm_password}
            onChange={(e) => setPasswords((p) => ({ ...p, confirm_password: e.target.value }))}
            required
          />
          <Button type="submit" loading={passwordSaving}>Change Password</Button>
        </form>
      </Card>
    </div>
  );
}
