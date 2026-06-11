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
          <span className="inline-flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-md text-[11px] font-semibold border border-emerald-200/60 shadow-sm">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center space-x-1.5 bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md text-[11px] font-semibold border border-indigo-200/60 shadow-sm">
            <Clock className="w-3 h-3 animate-pulse" />
            <span>Processing</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center space-x-1.5 bg-red-50 text-red-700 px-2.5 py-1 rounded-md text-[11px] font-semibold border border-red-200/60 shadow-sm">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md text-[11px] font-semibold border border-slate-200/60 shadow-sm">{status}</span>
        );
    }
  };

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full text-left border-collapse min-w-[1200px]">
        <thead>
          <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 text-[12px] font-semibold tracking-wide">
            <th className="px-6 py-3.5 whitespace-nowrap">Supplier & Company</th>
            <th className="px-6 py-3.5 whitespace-nowrap">Order Tracking</th>
            <th className="px-6 py-3.5 text-right whitespace-nowrap">Base Amount</th>
            <th className="px-6 py-3.5 text-right whitespace-nowrap">GST (18%)</th>
            <th className="px-6 py-3.5 text-right whitespace-nowrap">{feePercentage}% Fee</th>
            <th className="px-6 py-3.5 text-right whitespace-nowrap">Total (Incl.)</th>
            <th className="px-6 py-3.5 whitespace-nowrap">Status</th>
            <th className="px-6 py-3.5 text-center whitespace-nowrap">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {pos.map((po) => {
            const dynamicFee = po.base_amount * (feePercentage / 100);
            return (
            <tr key={po.id} className="hover:bg-slate-50/60 transition-colors group">
              <td className="px-6 py-4 align-middle">
                <div className="font-semibold text-slate-900 text-[14px] line-clamp-1" title={po.vendor_name}>{po.vendor_name || 'Extracting...'}</div>
                <div className="text-[13px] text-slate-500 mt-0.5 truncate" title={po.company_name}>{po.company_name || 'Pending'}</div>
              </td>
              <td className="px-6 py-4 align-middle">
                <div className="font-medium text-slate-900 text-[13px]">{po.order_tracking || '---'}</div>
                <div className="text-[12px] text-slate-400 mt-0.5">Net {po.credit_days || 0} days</div>
              </td>
              <td className="px-6 py-4 text-right align-middle">
                <span className="font-medium text-slate-600 text-[13px]">{formatCurrency(po.base_amount)}</span>
              </td>
              <td className="px-6 py-4 text-right align-middle">
                <span className="font-medium text-slate-600 text-[13px]">{formatCurrency(po.gst_amount)}</span>
              </td>
              <td className="px-6 py-4 text-right align-middle">
                <span className="inline-flex font-semibold text-indigo-700 bg-indigo-50/50 px-2 py-0.5 rounded text-[13px]">
                  {formatCurrency(dynamicFee)}
                </span>
              </td>
              <td className="px-6 py-4 text-right align-middle">
                <span className="font-bold text-slate-900 text-[14px]">{formatCurrency(po.total_amount)}</span>
              </td>
              <td className="px-6 py-4 align-middle">
                {getStatusBadge(po.status)}
              </td>
              <td className="px-6 py-4 align-middle">
                <div className="flex items-center justify-center space-x-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => onView(po)}
                    className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors" 
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => onDownload(po)}
                    className="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors" 
                    title="Download PDF"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  {isAuthorizedToDelete && (
                    <button 
                      onClick={() => onDelete(po.id)} 
                      className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors" 
                      title="Delete Record"
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
