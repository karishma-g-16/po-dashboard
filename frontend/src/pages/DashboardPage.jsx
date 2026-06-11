import React, { useState, useEffect } from 'react';
import { LogOut, LayoutDashboard, FileText, Settings, Bell, Search, Plus, RefreshCcw, Layers, Activity, Receipt, Wallet } from 'lucide-react';
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

  const isAdmin = user && ['karishmagautam178@gmail.com', 'ng965118@gmail.com'].includes(user.email?.toLowerCase());

  return (
    <div className="min-h-screen bg-[#fafafa] flex font-sans text-slate-900">
      {/* Sidebar - Fixed width */}
      <aside className="w-64 bg-[#111827] text-white flex flex-col fixed inset-y-0 z-20 shadow-xl border-r border-slate-800">
        <div className="p-6">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center shadow-inner">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-bold tracking-tight text-white">PO Dashboard</h1>
          </div>
        </div>
        
        <nav className="flex-1 px-4 py-4 space-y-1.5">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`relative w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${activeTab === 'dashboard' ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
          >
            {activeTab === 'dashboard' && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-500 rounded-r-full shadow-[0_0_8px_rgba(99,102,241,0.6)]" />}
            <LayoutDashboard className="w-5 h-5 shrink-0" />
            <span className="font-medium text-[14px]">Dashboard</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('purchase_orders')}
            className={`relative w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${activeTab === 'purchase_orders' ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
          >
            {activeTab === 'purchase_orders' && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-500 rounded-r-full shadow-[0_0_8px_rgba(99,102,241,0.6)]" />}
            <FileText className="w-5 h-5 shrink-0" />
            <span className="font-medium text-[14px]">Purchase Orders</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('settings')}
            className={`relative w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${activeTab === 'settings' ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
          >
            {activeTab === 'settings' && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-500 rounded-r-full shadow-[0_0_8px_rgba(99,102,241,0.6)]" />}
            <Settings className="w-5 h-5 shrink-0" />
            <span className="font-medium text-[14px]">Settings</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800/80 bg-slate-900/30">
          <div className="flex items-center space-x-3 mb-4 px-2">
            <div className="relative shrink-0">
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white uppercase shadow-sm">
                {user?.first_name?.charAt(0) || 'U'}
              </div>
              <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-400 border-2 border-[#111827] rounded-full"></div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-slate-100 truncate">{user?.first_name} {user?.last_name}</p>
              <div className="flex items-center space-x-1.5 mt-0.5">
                <span className="text-[10px] uppercase tracking-wider font-semibold text-indigo-400">{isAdmin ? 'Admin' : 'User'}</span>
                <span className="w-1 h-1 rounded-full bg-slate-600"></span>
                <p className="text-[11px] text-slate-400 truncate">{user?.company_name}</p>
              </div>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-colors text-slate-400"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-[13px] font-medium">Sign out</span>
          </button>
        </div>
      </aside>

      {/* Main Content - Pushed by sidebar width */}
      <main className="flex-1 flex flex-col ml-64 min-w-0 overflow-hidden">
        {activeTab !== 'settings' && (
          <header className="h-14 bg-white/80 backdrop-blur-md border-b border-slate-200/80 flex items-center justify-between px-8 sticky top-0 z-10">
            <div className="relative w-full max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search orders, suppliers..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 bg-slate-100/50 border border-slate-200/60 rounded-md text-[13px] focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400 shadow-sm"
              />
            </div>
            
            <div className="flex items-center space-x-3">
              {isAdmin && (
                <div className="flex items-center bg-white px-2 py-1 rounded-md border border-slate-200 shadow-sm">
                  <label htmlFor="feeSelector" className="text-[11px] font-bold text-slate-500 mr-2 uppercase tracking-widest">Fee</label>
                  <select 
                    id="feeSelector"
                    value={feePercentage} 
                    onChange={(e) => setFeePercentage(Number(e.target.value))}
                    className="bg-transparent text-[13px] font-semibold text-indigo-600 focus:outline-none cursor-pointer"
                  >
                    <option value={4}>4.0%</option>
                    <option value={3.75}>3.75%</option>
                  </select>
                </div>
              )}
              
              <div className="h-4 w-px bg-slate-200 mx-1"></div>
              
              <button onClick={() => fetchPos(searchTerm)} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors" title="Refresh Data">
                <RefreshCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
              
              <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors relative" title="Notifications">
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full border border-white"></span>
              </button>
              
              <button 
                onClick={() => setShowUpload(true)}
                className="ml-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white px-3.5 py-1.5 rounded-md font-medium text-[13px] flex items-center space-x-2 shadow-sm transition-all"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Invoice</span>
              </button>
            </div>
          </header>
        )}

        <div className={`overflow-y-auto ${activeTab === 'settings' ? 'bg-[#fafafa]' : 'p-8 space-y-8'}`}>
          {activeTab === 'dashboard' ? (
            <div className="max-w-[1400px] mx-auto w-full">
              {/* Dashboard Header */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Dashboard Overview</h2>
                <p className="text-slate-500 mt-1 text-[14px]">Welcome back, {user?.first_name}. Here's what's happening today.</p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-5">
                {[
                  { label: 'Total Invoices', value: pos.length, detail: searchTerm ? 'Filtered records' : 'Lifetime uploads', icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50/80', border: 'border-blue-100' },
                  { label: 'Total PCS', value: totalPcs.toLocaleString('en-IN'), detail: 'Ordered Quantity', icon: Layers, color: 'text-emerald-600', bg: 'bg-emerald-50/80', border: 'border-emerald-100' },
                  { label: `Fee Amount (${feePercentage}%)`, value: `₹${totalFee.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: 'Platform fee calculation', icon: Activity, color: 'text-indigo-600', bg: 'bg-indigo-50/80', border: 'border-indigo-100' },
                  { label: 'Total GST', value: `₹${totalGst.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: '18% Component', icon: Receipt, color: 'text-amber-600', bg: 'bg-amber-50/80', border: 'border-amber-100' },
                  { label: 'Total Volume', value: `₹${totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, detail: 'Incl. GST', icon: Wallet, color: 'text-slate-700', bg: 'bg-slate-100/80', border: 'border-slate-200' },
                ].map((stat, i) => (
                  <div key={i} className="bg-white border border-slate-200/80 p-5 rounded-2xl shadow-sm hover:shadow-md transition-shadow group flex flex-col justify-between h-[130px]">
                    <div className="flex justify-between items-start">
                      <p className="text-[13px] font-semibold text-slate-500 tracking-wide">{stat.label}</p>
                      <div className={`p-1.5 rounded-lg ${stat.bg} ${stat.border} border shadow-sm`}>
                        <stat.icon className={`w-4 h-4 ${stat.color}`} />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-slate-900 tracking-tight mt-2">{stat.value}</h3>
                      <p className="text-[11px] text-slate-400 mt-1 font-medium">{stat.detail}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Table Container */}
              <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden mt-8">
                <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-white/50 backdrop-blur-sm">
                  <h3 className="text-lg font-bold text-slate-900 tracking-tight">Recent Purchase Orders</h3>
                  <div className="flex items-center space-x-2">
                    <button onClick={() => poApi.exportCsv()} className="px-3 py-1.5 text-[13px] font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent hover:border-slate-200 rounded-lg transition-all shadow-sm">CSV Export</button>
                    <button onClick={() => poApi.exportExcel()} className="px-3 py-1.5 text-[13px] font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent hover:border-slate-200 rounded-lg transition-all shadow-sm">Excel Export</button>
                  </div>
                </div>
                
                <div className="p-0">
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
                    <div className="py-24 text-center text-slate-400 bg-slate-50/30">
                        <Search className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <p className="font-medium text-slate-600 text-[15px]">No records found for "{searchTerm}"</p>
                        <p className="text-slate-400 text-[13px] mt-1">Try adjusting your search criteria</p>
                        <button onClick={() => setSearchTerm('')} className="mt-4 text-indigo-600 font-semibold text-[14px] hover:text-indigo-700 transition-colors">Clear search</button>
                    </div>
                    ) : (
                    <div className="py-24 text-center text-slate-400 bg-slate-50/30">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <p className="font-medium text-slate-600 text-[15px]">No invoices uploaded yet</p>
                        <p className="text-slate-400 text-[13px] mt-1">Get started by uploading your first Purchase Order</p>
                        <button onClick={() => setShowUpload(true)} className="mt-4 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-700 font-semibold px-4 py-2 rounded-lg transition-colors text-[14px]">Upload Invoice</button>
                    </div>
                    )}
                </div>
              </div>
            </div>
          ) : activeTab === 'settings' ? (
            <SettingsView user={user} onLogout={handleLogout} />
          ) : (
            <div className="max-w-[1400px] mx-auto w-full">
              <PurchaseOrdersView pos={pos} />
            </div>
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
