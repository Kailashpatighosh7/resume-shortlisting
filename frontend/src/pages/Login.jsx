import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import toast from 'react-hot-toast'
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineUser, HiOutlineOfficeBuilding, HiOutlineArrowLeft, HiOutlineShieldCheck, HiOutlineKey } from 'react-icons/hi'
import loginBg from '../assets/login-bg.png'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', full_name: '', company: '' })
  const { login, register, loginDemo } = useAuth()
  const navigate = useNavigate()

  // Forgot Password State
  const [showForgot, setShowForgot] = useState(false)
  const [forgotStep, setForgotStep] = useState(1) // 1: email, 2: new password, 3: success
  const [forgotEmail, setForgotEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [forgotLoading, setForgotLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      if (isRegister) {
        await register(form)
        toast.success('Account created! Please login.')
        setIsRegister(false)
      } else {
        await login(form.email, form.password)
        toast.success('Welcome back!')
        navigate('/dashboard')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  async function handleDemoLogin() {
    setLoading(true)
    try {
      await loginDemo()
      toast.success('Welcome to Demo Mode!')
      navigate('/dashboard')
    } catch (err) {
      toast.error('Failed to enter demo mode')
    } finally {
      setLoading(false)
    }
  }

  // Forgot Password Handlers
  function openForgotPassword() {
    setShowForgot(true)
    setForgotStep(1)
    setForgotEmail('')
    setNewPassword('')
    setConfirmPassword('')
  }

  function closeForgotPassword() {
    setShowForgot(false)
    setForgotStep(1)
    setForgotEmail('')
    setNewPassword('')
    setConfirmPassword('')
  }

  async function handleVerifyEmail(e) {
    e.preventDefault()
    setForgotLoading(true)
    try {
      await api.post('/auth/forgot-password/verify', { email: forgotEmail })
      toast.success('Email verified! Set your new password.')
      setForgotStep(2)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'No account found with this email')
    } finally {
      setForgotLoading(false)
    }
  }

  async function handleResetPassword(e) {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setForgotLoading(true)
    try {
      await api.post('/auth/forgot-password/reset', {
        email: forgotEmail,
        new_password: newPassword,
      })
      toast.success('Password reset successfully!')
      setForgotStep(3)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to reset password')
    } finally {
      setForgotLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <>
  <div
    className="auth-left-panel"
    style={{
      backgroundImage: `url(${loginBg})`
    }}
  >
    <div className="hero-overlay" />

    <div className="hero-content">
      <div className="hero-badge">
        AI RECRUITMENT PLATFORM
      </div>

      <h1>
        Hire Smarter With
        <br />
        AI-Powered Candidate Screening
      </h1>

      <p>
        Automatically analyze resumes, rank candidates,
        identify skill gaps, and streamline recruitment workflows.
      </p>

      
    </div>
  </div>

  <div className="auth-right-panel">
    <div className="login-glass-card">

      <h2>
        {isRegister ? 'Create Account' : 'Welcome Back'}
      </h2>

      <p className="subtitle">
        {isRegister
          ? 'Start your AI-powered recruiting journey'
          : 'Sign in to your recruiter dashboard'}
      </p>

      <div className="auth-tabs">
        <button
          type="button"
          className={!isRegister ? 'active' : ''}
          onClick={() => setIsRegister(false)}
        >
          Login
        </button>

        <button
          type="button"
          className={isRegister ? 'active' : ''}
          onClick={() => setIsRegister(true)}
        >
          Sign Up
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">

        {isRegister && (
          <>
            <div className="relative">
              <HiOutlineUser className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Full Name"
                required
                value={form.full_name}
                onChange={(e) =>
                  setForm({
                    ...form,
                    full_name: e.target.value
                  })
                }
                className="input-field pl-10"
              />
            </div>

            <div className="relative">
              <HiOutlineOfficeBuilding className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Company (optional)"
                value={form.company}
                onChange={(e) =>
                  setForm({
                    ...form,
                    company: e.target.value
                  })
                }
                className="input-field pl-10"
              />
            </div>
          </>
        )}

        <div className="relative">
          <HiOutlineMail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="email"
            placeholder="Email Address"
            required
            value={form.email}
            onChange={(e) =>
              setForm({
                ...form,
                email: e.target.value
              })
            }
            className="input-field pl-10"
          />
        </div>

        <div className="relative">
          <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="password"
            placeholder="Password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value
              })
            }
            className="input-field pl-10"
          />
        </div>

        {!isRegister && (
          <div className="forgot-password-link-container">
            <button
              type="button"
              className="forgot-password-link"
              onClick={openForgotPassword}
            >
              Forgot Password?
            </button>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="login-btn-modern"
        >
          {loading
            ? (isRegister ? 'Creating...' : 'Signing In...')
            : (isRegister ? 'Create Account' : 'Enter Dashboard')}
        </button>
      </form>

      <div className="signup-text-modern">
        Recruit smarter with AI-powered candidate screening.
      </div>
    </div>
  </div>

</>

      {/* ── Forgot Password Modal ──────────────────────── */}
      {showForgot && (
        <div className="forgot-modal-overlay" onClick={closeForgotPassword}>
          <div className="forgot-modal animate-scale-in" onClick={(e) => e.stopPropagation()}>
            
            {/* Step Indicators */}
            <div className="forgot-steps">
              <div className={`forgot-step-dot ${forgotStep >= 1 ? 'active' : ''}`}>1</div>
              <div className={`forgot-step-line ${forgotStep >= 2 ? 'active' : ''}`} />
              <div className={`forgot-step-dot ${forgotStep >= 2 ? 'active' : ''}`}>2</div>
              <div className={`forgot-step-line ${forgotStep >= 3 ? 'active' : ''}`} />
              <div className={`forgot-step-dot ${forgotStep >= 3 ? 'active' : ''}`}>3</div>
            </div>

            {/* Step 1: Verify Email */}
            {forgotStep === 1 && (
              <div className="forgot-step-content animate-fade-in">
                <div className="forgot-icon-wrapper">
                  <HiOutlineMail className="forgot-icon" />
                </div>
                <h3>Forgot Password?</h3>
                <p className="forgot-desc">
                  Enter your registered email address and we'll verify your account.
                </p>
                <form onSubmit={handleVerifyEmail}>
                  <div className="relative" style={{ marginBottom: '16px' }}>
                    <HiOutlineMail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="email"
                      placeholder="Enter your email"
                      required
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="input-field pl-10"
                      autoFocus
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={forgotLoading}
                    className="login-btn-modern"
                  >
                    {forgotLoading ? 'Verifying...' : 'Verify Email'}
                  </button>
                </form>
                <button className="forgot-back-btn" onClick={closeForgotPassword}>
                  <HiOutlineArrowLeft /> Back to Login
                </button>
              </div>
            )}

            {/* Step 2: Set New Password */}
            {forgotStep === 2 && (
              <div className="forgot-step-content animate-fade-in">
                <div className="forgot-icon-wrapper forgot-icon-key">
                  <HiOutlineKey className="forgot-icon" />
                </div>
                <h3>Set New Password</h3>
                <p className="forgot-desc">
                  Create a strong password for <strong>{forgotEmail}</strong>
                </p>
                <form onSubmit={handleResetPassword}>
                  <div className="relative" style={{ marginBottom: '12px' }}>
                    <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="password"
                      placeholder="New Password (min 8 chars)"
                      required
                      minLength={8}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="input-field pl-10"
                      autoFocus
                    />
                  </div>
                  <div className="relative" style={{ marginBottom: '16px' }}>
                    <HiOutlineLockClosed className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="password"
                      placeholder="Confirm New Password"
                      required
                      minLength={8}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className={`input-field pl-10 ${confirmPassword && newPassword !== confirmPassword ? 'input-field-error' : ''}`}
                    />
                  </div>
                  {confirmPassword && newPassword !== confirmPassword && (
                    <p className="forgot-error-text">Passwords do not match</p>
                  )}
                  <button
                    type="submit"
                    disabled={forgotLoading || (confirmPassword && newPassword !== confirmPassword)}
                    className="login-btn-modern"
                  >
                    {forgotLoading ? 'Resetting...' : 'Reset Password'}
                  </button>
                </form>
                <button className="forgot-back-btn" onClick={() => setForgotStep(1)}>
                  <HiOutlineArrowLeft /> Change Email
                </button>
              </div>
            )}

            {/* Step 3: Success */}
            {forgotStep === 3 && (
              <div className="forgot-step-content animate-fade-in">
                <div className="forgot-icon-wrapper forgot-icon-success">
                  <HiOutlineShieldCheck className="forgot-icon" />
                </div>
                <h3>Password Updated!</h3>
                <p className="forgot-desc">
                  Your password has been reset successfully. You can now log in with your new password.
                </p>
                <button
                  className="login-btn-modern"
                  onClick={closeForgotPassword}
                >
                  Back to Login
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
