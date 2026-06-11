import React, { useState } from 'react';
import { X, Mail, ShieldCheck, Lock, ArrowRight } from 'lucide-react';
import { authApi } from '../api';

const ForgotPasswordModal = ({ onClose }) => {
  const [step, setStep] = useState(1); // 1: Email, 2: Code, 3: New Password
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const handleSendCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await authApi.forgotPassword(email);
      setMessage(response.message);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await authApi.verifyCode(email, code);
      setMessage('');
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await authApi.resetPassword(email, code, newPassword);
      setMessage('Password reset successfully! You can now login.');
      setTimeout(() => onClose(), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden relative animate-in fade-in zoom-in duration-200">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-8">
          <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-6">
            {step === 1 && <Mail className="w-6 h-6 text-indigo-600" />}
            {step === 2 && <ShieldCheck className="w-6 h-6 text-indigo-600" />}
            {step === 3 && <Lock className="w-6 h-6 text-indigo-600" />}
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            {step === 1 && 'Forgot Password?'}
            {step === 2 && 'Verify Code'}
            {step === 3 && 'New Password'}
          </h2>
          <p className="text-slate-500 text-sm mb-8">
            {step === 1 && "Enter your email address and we'll send you a 6-digit verification code."}
            {step === 2 && `We've sent a verification code to ${email}. Please enter it below.`}
            {step === 3 && 'Create a new secure password for your account.'}
          </p>

          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-sm font-medium">
              {error}
            </div>
          )}

          {message && step !== 3 && (
            <div className="mb-6 p-3 bg-green-50 border border-green-100 rounded-lg text-green-600 text-sm font-medium">
              {message}
            </div>
          )}

          {step === 1 && (
            <form onSubmit={handleSendCode} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Email Address</label>
                <input 
                  type="email" 
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                <span>{loading ? 'Sending...' : 'Send Reset Code'}</span>
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={handleVerifyCode} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Verification Code</label>
                <input 
                  type="text" 
                  required
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="123456"
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-center text-2xl font-bold tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                />
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                <span>{loading ? 'Verifying...' : 'Verify Code'}</span>
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
              <button 
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-slate-500 text-xs font-bold hover:text-indigo-600 transition-all"
              >
                Back to Email
              </button>
            </form>
          )}

          {step === 3 && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              {message ? (
                <div className="p-4 bg-green-50 border border-green-100 rounded-xl text-green-600 text-center">
                    <p className="font-bold mb-1">Success!</p>
                    <p className="text-sm">{message}</p>
                </div>
              ) : (
                <>
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">New Password</label>
                        <input 
                        type="password" 
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Confirm New Password</label>
                        <input 
                        type="password" 
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                    >
                        <span>{loading ? 'Resetting...' : 'Reset Password'}</span>
                        {!loading && <ArrowRight className="w-4 h-4" />}
                    </button>
                </>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordModal;
