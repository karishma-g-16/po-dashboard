import React, { useState } from 'react';
import { AlertTriangle, Trash2 } from 'lucide-react';
import { authApi } from '../api';

const SettingsView = ({ user, onLogout }) => {
  const [email, setEmail] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    if (confirmation !== 'delete my account') {
      setError("Please type 'delete my account' exactly to confirm.");
      return;
    }
    if (email.toLowerCase() !== user?.email.toLowerCase()) {
      setError("Email does not match your account.");
      return;
    }

    if (window.confirm("Are you absolutely sure? This action CANNOT be undone.")) {
      setLoading(true);
      setError('');
      try {
        await authApi.deleteAccount(email, confirmation);
        alert("Your account and all associated data have been deleted.");
        onLogout();
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to delete account");
        setLoading(false);
      }
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 mt-4">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Settings</h2>
        <p className="text-slate-500 text-sm">Manage your account preferences and settings.</p>
      </div>

      {/* Danger Zone */}
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-center space-x-3 text-red-600 mb-4">
          <AlertTriangle className="w-6 h-6" />
          <h3 className="text-lg font-bold">Danger Zone</h3>
        </div>
        <p className="text-red-700 text-sm mb-6">
          Permanently delete your account and all associated purchase orders. 
          This action is not reversible. You will lose access to all your uploaded files and data.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 text-sm font-medium rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleDeleteAccount} className="space-y-4 max-w-md">
          <div>
            <label className="block text-xs font-bold text-red-700 uppercase tracking-wider mb-2">Confirm Email</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={user?.email || "your-email@example.com"}
              className="w-full px-4 py-2 bg-white border border-red-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-red-700 uppercase tracking-wider mb-2">Type "delete my account"</label>
            <input 
              type="text" 
              required
              value={confirmation}
              onChange={(e) => setConfirmation(e.target.value)}
              placeholder="delete my account"
              className="w-full px-4 py-2 bg-white border border-red-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading || confirmation !== 'delete my account' || email.toLowerCase() !== user?.email?.toLowerCase()}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg shadow-sm transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Trash2 className="w-4 h-4" />
            <span>{loading ? 'Deleting...' : 'Delete Account'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default SettingsView;