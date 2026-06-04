import React, { useState } from 'react';
import { Upload, X, FileText, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { poApi } from '../api';

const UploadForm = ({ onUploadSuccess, onClose }) => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error'
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(prev => [...prev, ...Array.from(e.target.files)]);
      setUploadStatus(null);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setUploadStatus(null);
    setErrorMessage('');
    
    try {
      // Batch upload
      for (const file of files) {
        const res = await poApi.upload(file);
        if (!res.success) {
            throw new Error(res.error || 'Upload failed');
        }
      }
      setUploadStatus('success');
      setFiles([]);
      if (onUploadSuccess) onUploadSuccess();
      // Auto close after 1.5s on success
      setTimeout(() => onClose(), 1500);
    } catch (err) {
      setUploadStatus('error');
      setErrorMessage(err.message || 'Could not upload files. Please check your connection.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-6 animate-fade-in">
      <div className="bg-white w-full max-w-xl rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col border border-white/20">
        
        <div className="px-10 py-8 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-2xl font-black text-slate-900">Upload Invoices</h3>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Batch PDF & Image Processing</p>
          </div>
          <button 
            onClick={onClose} 
            className="p-3 bg-white border border-slate-200 text-slate-400 hover:text-slate-600 rounded-2xl transition-all shadow-sm active:scale-90"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-10">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[2rem] blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative border-2 border-dashed border-slate-200 rounded-[2rem] p-12 text-center hover:border-indigo-500 transition-all cursor-pointer bg-slate-50/50 group-hover:bg-white">
                <input 
                type="file" 
                multiple 
                onChange={handleFileChange} 
                className="hidden" 
                id="file-upload"
                accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.csv,.txt"
                />
                <label htmlFor="file-upload" className="cursor-pointer block">
                <div className="flex justify-center mb-6">
                    <div className="bg-white p-5 rounded-3xl shadow-xl border border-slate-100 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                    <Upload className="w-10 h-10 text-indigo-500" />
                    </div>
                </div>
                <p className="text-slate-900 font-black text-lg">Drop your invoices here</p>
                <p className="text-slate-400 font-bold text-xs uppercase tracking-widest mt-2">or click to browse local files</p>
                </label>
            </div>
          </div>

          {files.length > 0 && (
            <div className="mt-10 space-y-3 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center">
                  <FileText className="w-3.5 h-3.5 mr-2 text-indigo-500" />
                  Files Selected ({files.length})
              </p>
              {files.map((file, i) => (
                <div key={i} className="flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-sm group animate-fade-in">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
                        <FileText className="w-5 h-5 text-indigo-500" />
                    </div>
                    <div className="min-w-0">
                        <span className="text-sm font-bold text-slate-900 truncate block max-w-[240px]">
                        {file.name}
                        </span>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                            {(file.size / 1024).toFixed(1)} KB
                        </span>
                    </div>
                  </div>
                  <button 
                    onClick={() => removeFile(i)} 
                    className="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="mt-8 flex items-center space-x-4 text-emerald-700 bg-emerald-50 p-5 rounded-[1.5rem] border border-emerald-100 animate-fade-in">
              <div className="bg-white p-2 rounded-xl shadow-sm">
                <CheckCircle2 className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <p className="text-sm font-black uppercase tracking-tight">Upload Successful!</p>
                <p className="text-xs font-bold text-emerald-600/70">Processing has been scheduled for all files.</p>
              </div>
            </div>
          )}

          {uploadStatus === 'error' && (
            <div className="mt-8 flex items-center space-x-4 text-rose-700 bg-rose-50 p-5 rounded-[1.5rem] border border-rose-100 animate-fade-in">
              <div className="bg-white p-2 rounded-xl shadow-sm">
                <AlertCircle className="w-6 h-6 text-rose-500" />
              </div>
              <div>
                <p className="text-sm font-black uppercase tracking-tight">Upload Failed</p>
                <p className="text-xs font-bold text-rose-600/70">{errorMessage}</p>
              </div>
            </div>
          )}

          <div className="mt-10 flex space-x-4">
            <button 
              onClick={onClose}
              className="flex-1 py-4 px-6 border border-slate-200 rounded-[1.5rem] text-sm font-black text-slate-500 hover:bg-slate-50 transition-all uppercase tracking-widest"
            >
              Discard
            </button>
            <button 
              disabled={files.length === 0 || isUploading}
              onClick={handleUpload}
              className="flex-[2] btn-primary flex justify-center items-center py-4 rounded-[1.5rem] shadow-lg shadow-indigo-500/30"
            >
              {isUploading ? (
                <div className="flex items-center space-x-3">
                    <Loader2 className="animate-spin h-5 w-5" />
                    <span className="uppercase tracking-widest text-xs font-black">Processing...</span>
                </div>
              ) : (
                <span className="uppercase tracking-widest text-xs font-black">Process {files.length} Invoices</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadForm;
