import React from 'react';
import { FileText, Package, Building2 } from 'lucide-react';

const PurchaseOrdersView = ({ pos }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Purchase Orders</h2>
        <p className="text-slate-500 text-sm">Overview of all structured purchase orders.</p>
      </div>

      {pos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {pos.map((po) => (
            <div key={po.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-all group">
              <div>
                <div className="flex items-center space-x-3 mb-4 text-indigo-600 bg-indigo-50 w-fit px-3 py-1.5 rounded-lg border border-indigo-100">
                  <Building2 className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-wider">Buyer Company</span>
                </div>
                <h3 className="font-bold text-slate-900 text-lg line-clamp-2 leading-tight mb-6" title={po.company_name}>
                  {po.company_name || 'Pending Extraction...'}
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                     <div className="mt-0.5 p-2 bg-slate-50 rounded-lg text-slate-400">
                        <Package className="w-4 h-4" />
                     </div>
                     <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-0.5">Ordered Quantity</p>
                        <p className="text-base font-bold text-slate-700">
                          {po.ordered_quantity > 0 ? `${po.ordered_quantity.toLocaleString()} PCS` : 'N/A'}
                        </p>
                     </div>
                  </div>

                  <div className="flex items-start space-x-3">
                     <div className="mt-0.5 p-2 bg-slate-50 rounded-lg text-slate-400">
                        <FileText className="w-4 h-4" />
                     </div>
                     <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-0.5">Supplier / Vendor</p>
                        <p className="text-sm font-medium text-slate-600 line-clamp-2" title={po.vendor_name}>
                          {po.vendor_name || 'N/A'}
                        </p>
                     </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-20 text-center text-slate-400">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <p className="font-medium text-slate-500">No purchase orders found yet</p>
        </div>
      )}
    </div>
  );
};

export default PurchaseOrdersView;
