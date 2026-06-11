import React, { useState, useEffect, useMemo } from 'react';
import { LogOut, LayoutDashboard, FileText, Settings, Bell, Search, Plus, RefreshCcw, Download } from 'lucide-react';
import { poApi } from '../api';
import UploadForm from '../components/UploadForm';
import POTable from '../components/POTable';
import DocumentViewerModal from '../components/DocumentViewerModal';
import PurchaseOrdersView from '../components/PurchaseOrdersView';
import SettingsView from '../components/SettingsView';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const DashboardPage = ({ user }) => {
  const [pos, setPos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedViewPo, setSelectedViewPo] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [feePercentage, setFeePercentage] = useState(4);
  const [activeTab, setActiveTab] = useState('dashboard');

  const fetchPos = async (search = '') => {
    setIsLoading(true);
    try {
      const response = await poApi.list({ search });
      if (response && response.success) {
        setPos(response.data || []);
      } else {
        setPos([]);
      }
    } catch (err) {
      console.error('Failed to fetch POs', err);
      setPos([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPos(searchTerm);
  }, [searchTerm]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (pos.some(po => po.status === 'PROCESSING')) {
        fetchPos(searchTerm);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [pos.some(po => po.status === 'PROCESSING')]);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this invoice?')) {
      try {
        await poApi.delete(id);
        fetchPos(searchTerm);
      } catch (err) {
        alert('Delete failed');
      }
    }
  };

  const handleDownload = async (po) => {
    try {
      console.log('Generating PDF for PO:', po);
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      
      // Header
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('PURCHASE ORDER VOUCHER', pageWidth / 2, 20, { align: 'center' });
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Exported on: ${new Date().toLocaleString()}`, pageWidth / 2, 28, { align: 'center' });
      
      doc.setDrawColor(200, 200, 200);
      doc.line(15, 35, pageWidth - 15, 35);
      
      // Details Section (Manually drawn for better compatibility)
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Order Details', 15, 45);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      let currentY = 52;
      const drawLine = (label, val) => {
        doc.setFont('helvetica', 'bold');
        doc.text(`${label}:`, 15, currentY);
        doc.setFont('helvetica', 'normal');
        doc.text(String(val || 'N/A'), 50, currentY);
        currentY += 7;
      };

      drawLine('Supplier', po.vendor_name);
      drawLine('Company', po.company_name);
      drawLine('Tracking #', po.order_tracking);
      drawLine('Terms', `Net ${po.credit_days || 0} days`);
      drawLine('Status', po.status);
      
      // Financials Section using autoTable
      currentY += 10;
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Financial Breakdown', 15, currentY);
      
      const formatCurrency = (amt) => `Rs. ${Number(amt || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
      
      const dynamicFee = po.base_amount * (feePercentage / 100);

      const tableData = [
        ['Base Amount (Excl. GST)', formatCurrency(po.base_amount)],
        ['GST (18%)', formatCurrency(po.gst_amount)],
        [`Fee (${feePercentage}%)`, formatCurrency(dynamicFee)],
        ['GRAND TOTAL (Incl. GST)', formatCurrency(po.total_amount)]
      ];

      autoTable(doc, {
        startY: currentY + 5,
        head: [['Description', 'Amount (INR)']],
        body: tableData,
        theme: 'grid',
        headStyles: { fillColor: [79, 70, 229] },
        columnStyles: { 1: { halign: 'right' } },
        didParseCell: function(data) {
          if (data.row.index === 3) {
            data.cell.styles.fontStyle = 'bold';
            data.cell.styles.fillColor = [240, 240, 240];
          }
        }
      });
      
      doc.save(`PO_Voucher_${po.order_tracking || 'Export'}.pdf`);
    } catch (err) {
      console.error('CRITICAL PDF ERROR:', err);
      alert(`PDF Error: ${err.message}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  const totalAmount = pos.reduce((acc, po) => acc + Number(po.total_amount || 0), 0);
  const totalGst = pos.reduce((acc, po) => acc + Number(po.gst_amount || 0), 0);
  const totalPcs = pos.reduce((acc, po) => acc + Number(po.ordered_quantity || 0), 0);
  const totalFee = pos.reduce((acc, po) => acc + (Number(po.base_amount || 0) * (feePercentage / 100)), 0);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar - Fixed width */}
      <aside className="w-60 bg-[#1e293b] text-white flex flex-col fixed inset-y-0 z-20">
        <div className="p-6">
          <h1 className="text-xl font-bold tracking-tight text-white">PO Dashboard</h1>
        </div>
        
        <nav className="flex-1 px-4 space-y-2">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${activeTab === 'dashboard' ? 'bg-white/10 text-indigo-400' : 'hover:bg-white/5 text-slate-300'}`}
          >
            <LayoutDashboard className="w-5 h-5" />
            <span className="font-medium">Dashboard</span>
          </button>
          <button 
            onClick={() => setActiveTab('purchase_orders')}
            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${activeTab === 'purchase_orders' ? 'bg-white/10 text-indigo-400' : 'hover:bg-white/5 text-slate-300'}`}
          >
            <FileText className="w-5 h-5" />
            <span className="font-medium">Purchase Orders</span>
          </button>
          <button 
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all ${activeTab === 'settings' ? 'bg-white/10 text-indigo-400' : 'hover:bg-white/5 text-slate-300'}`}
          >
            <Settings className="w-5 h-5" />
            <span className="font-medium">Settings</span>
          </button>
        </nav>

        <div className="p-4 border-t border-white/10">
          <div className="flex items-center space-x-3 mb-4 px-2">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-white uppercase">
              {user?.first_name?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.first_name} {user?.last_name}</p>
              <p className="text-[10px] text-slate-400 truncate uppercase">{user?.company_name}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-white/5 transition-all text-slate-300"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* Main Content - Pushed by sidebar width */}
      <main className="flex-1 flex flex-col ml-60 min-w-0 overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="relative w-full max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search by supplier, company or PO#..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 transition-all"
            />
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
              <label htmlFor="feeSelector" className="text-xs font-bold text-slate-500 mr-2 uppercase tracking-wider">Fee:</label>
              <select 
                id="feeSelector"
                value={feePercentage} 
                onChange={(e) => setFeePercentage(Number(e.target.value))}
                className="bg-transparent text-sm font-bold text-indigo-600 focus:outline-none cursor-pointer"
              >
                <option value={4}>4.0%</option>
                <option value={3.75}>3.75%</option>
              </select>
            </div>
            <button onClick={() => fetchPos(searchTerm)} className="p-2 text-slate-400 hover:text-slate-600 transition-all">
              <RefreshCcw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button className="p-2 text-slate-400 hover:text-slate-600 transition-all">
              <Bell className="w-5 h-5" />
            </button>
            <button 
              onClick={() => setShowUpload(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-bold text-sm flex items-center space-x-2 shadow-sm transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>+ New Invoice</span>
            </button>
          </div>
        </header>

        <div className="p-6 lg:p-8 space-y-6 overflow-y-auto">
          {activeTab === 'dashboard' ? (
            <>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Dashboard Overview</h2>
                <p className="text-slate-500 text-sm">Welcome back, {user?.first_name}.</p>
              </div>

              {/* Stats Grid - Fixed wrap issue */}
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
                {[
                  { label: 'Total Invoices', value: pos.length, detail: searchTerm ? 'Filtered records' : 'Lifetime uploads' },
                  { label: 'Total PCS', value: totalPcs.toLocaleString('en-IN'), detail: 'Ordered Quantity' },
                  { label: `Total ${feePercentage}% Amount`, value: `₹${totalFee.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: 'Fee Calculation', color: 'text-indigo-600' },
                  { label: 'GST Total', value: `₹${totalGst.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: '18% Component' },
                  { label: 'Total Amount', value: `₹${totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: 'Incl. GST' },
                ].map((stat, i) => (
                  <div key={i} className="bg-white border border-slate-200 p-5 rounded-xl shadow-sm">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{stat.label}</p>
                    <p className={`text-2xl font-bold mt-1 ${stat.color || 'text-slate-900'}`}>{stat.value}</p>
                    <p className="text-[10px] text-slate-400 mt-1 font-medium italic">{stat.detail}</p>
                  </div>
                ))}
              </div>

              {/* Table Container */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="font-bold text-slate-900">Recent Purchase Orders</h3>
                  <div className="flex items-center space-x-4">
                    <button onClick={() => poApi.exportCsv()} className="text-xs font-bold text-indigo-600 hover:underline">CSV</button>
                    <button onClick={() => poApi.exportExcel()} className="text-xs font-bold text-indigo-600 hover:underline">Excel</button>
                    <span className="text-slate-300">|</span>
                    <button className="text-xs font-bold text-slate-500 hover:text-slate-700">View all</button>
                  </div>
                </div>
                
                <div className="p-0 overflow-x-auto">
                    {pos.length > 0 ? (
                    <POTable 
                        pos={pos} 
                        onDelete={handleDelete} 
                        onView={(po) => setSelectedViewPo(po)}
                        onDownload={(po) => handleDownload(po)}
                        userEmail={user?.email}
                        feePercentage={feePercentage}
                    />
                    ) : searchTerm ? (
                    <div className="p-20 text-center text-slate-400">
                        <Search className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p className="font-medium text-slate-500">No records found for "{searchTerm}"</p>
                        <button onClick={() => setSearchTerm('')} className="mt-2 text-indigo-600 font-bold hover:underline">Clear search</button>
                    </div>
                    ) : (
                    <div className="p-20 text-center text-slate-400">
                        <FileText className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p className="font-medium text-slate-500">No invoices found yet</p>
                        <button onClick={() => setShowUpload(true)} className="mt-2 text-indigo-600 font-bold hover:underline">Upload your first PO</button>
                    </div>
                    )}
                </div>
              </div>
            </>
          ) : activeTab === 'settings' ? (
            <SettingsView user={user} onLogout={handleLogout} />
          ) : (
            <PurchaseOrdersView pos={pos} />
          )}
        </div>
      </main>

      {showUpload && (
        <UploadForm 
          onUploadSuccess={() => fetchPos(searchTerm)} 
          onClose={() => setShowUpload(false)} 
        />
      )}

      {selectedViewPo && (
        <DocumentViewerModal 
          po={selectedViewPo} 
          onClose={() => setSelectedViewPo(null)} 
        />
      )}
    </div>
  );
};

export default DashboardPage;
