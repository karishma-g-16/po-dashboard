import React, { useState } from 'react';
import { AlertTriangle, Trash2 } from 'lucide-react';
import { authApi } from '../api';

const SettingsView = ({ user, onLogout }) => {
  const [email, setEmail] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Robust validation constants
  const isConfirmationValid = confirmation.trim().toLowerCase() === 'delete my account';
  const isEmailValid = email.trim().toLowerCase() === (user?.email || '').trim().toLowerCase();

  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    console.log("Delete account clicked");

    if (!isConfirmationValid) {
      console.log("Validation failed: Incorrect confirmation text");
      setError("Please type 'delete my account' exactly to confirm.");
      return;
    }
    if (!isEmailValid) {
      console.log("Validation failed: Email mismatch");
      setError("Email does not match your account.");
      return;
    }

    console.log("Validation passed");

    if (window.confirm("Are you absolutely sure? This action CANNOT be undone.")) {
      setLoading(true);
      setError('');
      console.log("Sending delete request");
      
      try {
        const response = await authApi.deleteAccount(email.trim(), confirmation.trim());
        console.log("Delete response:", response);
        alert("Your account and all associated data have been successfully deleted.");
        onLogout(); // Clears session and redirects to login
      } catch (err) {
        console.error("Delete account error:", err);
        setError(err.response?.data?.detail || "Failed to delete account. Please try again.");
        setLoading(false);
      }
    }
  };

  return (
    <div className="w-full max-w-[1000px] px-4 py-8 sm:px-6 md:px-8">
      {/* Page Header */}
      <div className="mb-10 border-b border-slate-200 pb-6">
        <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Settings</h2>
        <p className="text-slate-500 mt-2 text-sm">Manage your account preferences and security settings.</p>
      </div>

      {/* Danger Zone Section */}
      <div className="bg-white border border-red-200 rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="flex items-start mb-6">
          <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center shrink-0 mr-4 border border-red-100">
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900">Danger Zone</h3>
            <p className="text-slate-500 mt-1 text-sm leading-relaxed">
              Permanently delete your account and all associated purchase orders. 
              This action is not reversible. You will lose access to all your uploaded files and data.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-700 text-sm font-medium rounded-xl flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleDeleteAccount} className="space-y-6 max-w-xl">
          <div className="space-y-1.5">
            <label className="block text-sm font-semibold text-slate-700">
              Confirm Email
            </label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={user?.email || "your-email@example.com"}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all shadow-sm placeholder-slate-400"
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="block text-sm font-semibold text-slate-700">
              To verify, type <span className="text-slate-900 font-bold px-1.5 py-0.5 bg-slate-100 rounded">delete my account</span> below
            </label>
            <input 
              type="text" 
              required
              value={confirmation}
              onChange={(e) => setConfirmation(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all shadow-sm"
            />
          </div>
          
          <div className="pt-2">
            <button 
              type="submit" 
              disabled={loading || !isConfirmationValid || !isEmailValid}
              className="w-full sm:w-auto bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold py-3 px-8 rounded-xl shadow-sm transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-4 h-4" />
              <span>{loading ? 'Deleting Account...' : 'Delete Account'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SettingsView;