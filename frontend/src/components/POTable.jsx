import React, { useMemo } from 'react';
import { Eye, Trash2, Download, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

const POTable = ({ pos, onDelete, onView, onDownload, userEmail, feePercentage = 4 }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount || 0);
  };

  const isAuthorizedToDelete = useMemo(() => {
    const authorized = ["karishmagautam178@gmail.com", "ng965118@gmail.com"];
    if (!userEmail) return false;
    const cleanEmail = userEmail.trim().toLowerCase();
    return authorized.some(email => email.toLowerCase() === cleanEmail);
  }, [userEmail]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="flex items-center space-x-1 text-green-600 bg-green-50 px-2 py-1 rounded-full text-xs font-medium border border-green-100">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="flex items-center space-x-1 text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full text-xs font-medium border border-indigo-100">
            <Clock className="w-3 h-3 animate-pulse" />
            <span>Processing</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center space-x-1 text-red-600 bg-red-50 px-2 py-1 rounded-full text-xs font-medium border border-red-100">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="text-slate-500 text-xs font-medium">{status}</span>
        );
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse min-w-[1200px]">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50/50">
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-[320px]">Supplier & Company</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-[180px]">Order Tracking</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-[140px]">Base Amount</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-[120px]">GST (18%)</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-[120px]">{feePercentage}% Amount</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right w-[140px]">Total (Incl.)</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-[120px]">Status</th>
            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center w-[120px]">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {pos.map((po) => {
            const dynamicFee = po.base_amount * (feePercentage / 100);
            return (
            <tr key={po.id} className="hover:bg-slate-50 transition-all group">
              <td className="px-6 py-4">
                <div className="font-bold text-slate-900 line-clamp-1" title={po.vendor_name}>{po.vendor_name || 'Extracting...'}</div>
                <div className="text-xs text-slate-500 truncate" title={po.company_name}>{po.company_name || 'Pending'}</div>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-slate-900">{po.order_tracking || '---'}</div>
                <div className="text-xs text-slate-400">Net {po.credit_days || 0} days</div>
              </td>
              <td className="px-6 py-4 text-right font-medium text-slate-600">
                {formatCurrency(po.base_amount)}
              </td>
              <td className="px-6 py-4 text-right font-medium text-slate-600">
                {formatCurrency(po.gst_amount)}
              </td>
              <td className="px-6 py-4 text-right font-medium text-indigo-600 bg-indigo-50/30">
                {formatCurrency(dynamicFee)}
              </td>
              <td className="px-6 py-4 text-right">
                <div className="text-sm font-bold text-slate-900">{formatCurrency(po.total_amount)}</div>
              </td>
              <td className="px-6 py-4">
                {getStatusBadge(po.status)}
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center justify-center space-x-2">
                  <button 
                    onClick={() => onView(po)}
                    className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all" 
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => onDownload(po)}
                    className="p-2 text-slate-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all" 
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  {isAuthorizedToDelete && (
                    <button 
                      onClick={() => onDelete(po.id)} 
                      className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" 
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          )})}
        </tbody>
      </table>
    </div>
  );
};

export default POTable;
