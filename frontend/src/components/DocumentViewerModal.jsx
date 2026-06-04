import React from 'react';
import { X, ExternalLink, Download, FileText, ImageIcon } from 'lucide-react';

const DocumentViewerModal = ({ po, onClose }) => {
  if (!po) return null;

  const isImage = po.file_type?.match(/png|jpg|jpeg/i);
  const isPdf = po.file_type?.match(/pdf/i);
  
  // We need to serve the file from the backend. 
  // For now we'll assume an endpoint /api/po/file/{id} or direct path
  const fileUrl = `/api/po/file/${po.id}`;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-6 animate-fade-in">
      <div className="bg-white w-full max-w-5xl h-[90vh] rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col border border-white/20">
        
        {/* Header */}
        <div className="px-10 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white rounded-2xl shadow-sm border border-slate-100">
              {isImage ? <ImageIcon className="w-6 h-6 text-indigo-500" /> : <FileText className="w-6 h-6 text-indigo-500" />}
            </div>
            <div>
              <h3 className="text-xl font-black text-slate-900">{po.order_tracking || 'Document Preview'}</h3>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">{po.vendor_name}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <a 
              href={fileUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-5 py-2.5 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all shadow-sm"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open Original</span>
            </a>
            <button 
              onClick={onClose}
              className="p-3 bg-slate-900 text-white rounded-2xl hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/10 active:scale-90"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 bg-slate-100 p-8 overflow-auto flex items-center justify-center min-h-0">
          {isPdf ? (
            <iframe 
              src={`${fileUrl}#toolbar=0`} 
              className="w-full h-full rounded-2xl border border-slate-200 shadow-inner bg-white"
              title="PDF Viewer"
            />
          ) : isImage ? (
            <div className="relative group max-w-full">
                <img 
                src={fileUrl} 
                alt="Invoice" 
                className="max-w-full max-h-full rounded-2xl shadow-2xl border-4 border-white object-contain"
                />
            </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-[2rem] shadow-sm border border-slate-200 px-10">
              <FileText className="w-16 h-16 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-900 font-bold text-lg">Preview Not Available</p>
              <p className="text-slate-400 text-sm mt-2 font-medium">This file type ({po.file_type}) cannot be previewed directly. <br/>Please download it to view the content.</p>
              <a 
                href={fileUrl} 
                download 
                className="mt-8 inline-flex items-center space-x-2 px-8 py-3 bg-indigo-50 text-indigo-600 font-black rounded-2xl hover:bg-indigo-100 transition-all uppercase tracking-widest text-xs"
              >
                <Download className="w-4 h-4" />
                <span>Download File</span>
              </a>
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="px-10 py-4 bg-white border-t border-slate-100 flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-widest">
            <div className="flex items-center space-x-6">
                <span>Total: ₹{Number(po.total_amount).toLocaleString('en-IN')}</span>
                <span className="w-1 h-1 bg-slate-200 rounded-full"></span>
                <span>GST: ₹{Number(po.gst_amount).toLocaleString('en-IN')}</span>
            </div>
            <span>ID: {po.id}</span>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewerModal;
