import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { Wrench, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

export const Maintenance: React.FC = () => {
  const { vehicles, maintenanceLogs, addMaintenanceLog, updateMaintenanceLog } = useStore();

  // Form states
  const [selectedVehicle, setSelectedVehicle] = useState(vehicles[0]?.id || '');
  const [serviceType, setServiceType] = useState('Brake Wear Replacement & Inspection');
  const [provider, setProvider] = useState('Speedy Fleet Services');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [cost, setCost] = useState(450);
  const [status, setStatus] = useState<'Scheduled' | 'In Progress' | 'Completed'>('Scheduled');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedVehicle || !serviceType || !provider || !date) {
      toast.error('All maintenance log fields must be specified.');
      return;
    }

    addMaintenanceLog({
      vehicleId: selectedVehicle,
      serviceType,
      provider,
      date,
      cost,
      status
    });

    toast.success(`Maintenance logged for asset ${selectedVehicle}`);
    
    // Clear cost
    setCost(450);
  };

  const handleToggleStatus = (id: string, currentStatus: string) => {
    let nextStatus: 'Scheduled' | 'In Progress' | 'Completed' = 'Completed';
    if (currentStatus === 'Scheduled') nextStatus = 'In Progress';
    if (currentStatus === 'In Progress') nextStatus = 'Completed';

    updateMaintenanceLog(id, { status: nextStatus });
    toast.success(`Maintenance status advanced to ${nextStatus}`);
  };

  // Workshop mechanics bays workload state
  const serviceBays = [
    { bay: 'Bay 01 (Heavy Systems)', state: 'Busy', vehicle: 'VEH-1243', mechanic: 'Mark R.' },
    { bay: 'Bay 02 (Diagnostics Hub)', state: 'Available', vehicle: '—', mechanic: 'Alice S.' },
    { bay: 'Bay 03 (Alignments Hub)', state: 'Busy', vehicle: 'VEH-0987', mechanic: 'Greg T.' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative"
    >
      
      {/* Left Column: Form & Workshop Bay Queues */}
      <div className="lg:col-span-4 space-y-6">
        
        {/* Form */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-2xl">
          <div className="border-b border-[rgba(255,255,255,0.06)] pb-3 mb-5">
            <h4 className="text-white font-bold text-sm font-sans flex items-center gap-2">
              <Wrench className="w-4.5 h-4.5 text-[#D88A1D]" />
              Schedule Mechanical Service
            </h4>
            <p className="text-xs text-gray-500 mt-0.5">Log preventives and repair invoices</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Fleet Asset</label>
              <select
                value={selectedVehicle}
                onChange={(e) => setSelectedVehicle(e.target.value)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
              >
                {vehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.id} — {v.model} ({v.type})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
              >
                <option value="Oil & Fluid Flush">Oil & Fluid Flush</option>
                <option value="Brake Wear Replacement & Inspection">Brake Wear Replacement & Inspection</option>
                <option value="Tire Rotation & Wheel Alignment">Tire Rotation & Wheel Alignment</option>
                <option value="Engine Tuning & Filter Replacement">Engine Tuning & Filter Replacement</option>
                <option value="Air Conditioning Repair">Air Conditioning Repair</option>
                <option value="Transmission Inspection">Transmission Inspection</option>
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Service Provider Shop</label>
              <input
                type="text"
                required
                placeholder="e.g. Speedy Fleet Services"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Scheduled Date</label>
                <input
                  type="date"
                  required
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Estimated Cost ($)</label>
                <input
                  type="number"
                  min="0"
                  required
                  value={cost}
                  onChange={(e) => setCost(Number(e.target.value))}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Service Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as any)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
              >
                <option value="Scheduled">Scheduled</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all flex items-center justify-center gap-2 mt-4"
            >
              <Plus className="w-4 h-4" />
              Schedule Service Run
            </button>
          </form>
        </div>

        {/* Mechanic Shop Queues */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg space-y-4">
          <h5 className="text-white font-bold text-xs uppercase tracking-wider">Active Workshop Service Bays</h5>
          <div className="space-y-2">
            {serviceBays.map((bay, idx) => (
              <div key={idx} className="flex justify-between items-center p-2.5 rounded-lg bg-[#0F1117]/60 border border-[rgba(255,255,255,0.02)]">
                <div>
                  <span className="block text-xs font-bold text-white">{bay.bay}</span>
                  <span className="text-[9px] text-gray-500 font-medium">Assigned Lead: {bay.mechanic}</span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  bay.state === 'Busy' ? 'bg-[#D88A1D]/15 text-[#D88A1D]' : 'bg-[#4ADE80]/15 text-[#4ADE80]'
                }`}>
                  {bay.state === 'Busy' ? `Active: ${bay.vehicle}` : 'Available'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Column: Service logs registry table & downtime analytics */}
      <div className="lg:col-span-8 space-y-6">
        
        {/* Downtime Analytics Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 shadow-lg">
          <div className="p-2 border-r border-[rgba(255,255,255,0.04)] last:border-none">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Aggregate Downtime Hours</span>
            <span className="text-xl font-black text-white font-mono mt-1 block">42 hours lost</span>
            <p className="text-[9px] text-gray-500 mt-1">Total mechanical hours logged in bays</p>
          </div>
          <div className="p-2 border-r border-[rgba(255,255,255,0.04)] last:border-none">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Avg Service Speed</span>
            <span className="text-xl font-black text-[#4EA8DE] font-mono mt-1 block">4.8 hours</span>
            <p className="text-[9px] text-gray-500 mt-1">Average repair turnaround speed</p>
          </div>
          <div className="p-2 border-r border-[rgba(255,255,255,0.04)] last:border-none">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Repairs completed rating</span>
            <span className="text-xl font-black text-[#4ADE80] font-mono mt-1 block">98.4% success</span>
            <p className="text-[9px] text-gray-500 mt-1">Post-repair quality inspection checks passed</p>
          </div>
        </div>

        {/* Main Service Registry Table */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl flex flex-col justify-between">
          <div>
            <div className="p-4 border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] flex justify-between items-center">
              <div>
                <h5 className="text-white font-bold text-sm">Upcoming & Historical Maintenance Records</h5>
                <p className="text-xs text-gray-500 mt-0.5">Asset health telemetry service logs</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => {
                    toast.message('Exporting mechanical logs data...');
                    setTimeout(() => toast.success('Maintenance records exported as CSV.'), 800);
                  }}
                  className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-1.5 rounded transition cursor-pointer"
                >
                  CSV
                </button>
                <button 
                  onClick={() => {
                    toast.message('Exporting service spreadsheets...');
                    setTimeout(() => toast.success('Maintenance records exported as Excel XLSX.'), 800);
                  }}
                  className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-1.5 rounded transition cursor-pointer"
                >
                  Excel
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                    <th className="p-3.5">Vehicle ID</th>
                    <th className="p-3.5">Mechanical Service Description</th>
                    <th className="p-3.5">Service Provider Shop</th>
                    <th className="p-3.5">Scheduled Date</th>
                    <th className="p-3.5">Cost</th>
                    <th className="p-3.5">Uptime Status</th>
                    <th className="p-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300">
                  {maintenanceLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-white/[0.01] transition apple-transition">
                      <td className="p-3.5 font-mono font-bold text-[#4EA8DE]">{log.vehicleId}</td>
                      <td className="p-3.5 font-bold text-white">
                        <div>{log.serviceType}</div>
                        
                        {/* Repair Steps Visual Progress Timeline */}
                        {log.status !== 'Completed' && (
                          <div className="flex gap-4 text-[9px] font-bold uppercase text-gray-600 mt-2 font-mono">
                            <span className={log.status === 'Scheduled' || log.status === 'In Progress' ? 'text-[#D88A1D]' : ''}>• Diagnostics</span>
                            <span className={log.status === 'In Progress' ? 'text-[#D88A1D]' : ''}>• Sourcing Parts</span>
                            <span>• Assemble</span>
                          </div>
                        )}
                      </td>
                      <td className="p-3.5 text-gray-400">{log.provider}</td>
                      <td className="p-3.5 text-gray-500">{log.date}</td>
                      <td className="p-3.5 font-mono font-bold text-white">${log.cost.toLocaleString()}</td>
                      <td className="p-3.5">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold ${
                          log.status === 'Completed' 
                            ? 'bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/15' 
                            : log.status === 'In Progress' 
                            ? 'bg-[#4EA8DE]/10 text-[#4EA8DE] border border-[#4EA8DE]/15' 
                            : 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/15'
                        }`}>
                          <span className={`h-1.5 w-1.5 rounded-full ${
                            log.status === 'Completed' ? 'bg-[#4ADE80]' : log.status === 'In Progress' ? 'bg-[#4EA8DE] animate-pulse' : 'bg-[#F59E0B]'
                          }`}></span>
                          {log.status}
                        </span>
                      </td>
                      <td className="p-3.5 text-right">
                        {log.status !== 'Completed' ? (
                          <button
                            onClick={() => handleToggleStatus(log.id, log.status)}
                            className="bg-white/[0.03] border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white px-2.5 py-1.5 rounded text-[10px] font-bold transition"
                          >
                            {log.status === 'Scheduled' ? 'Start Repair' : 'Log Completed'}
                          </button>
                        ) : (
                          <span className="text-[10px] text-gray-500 font-bold">Logged Archive</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Totals Summary Footer */}
          <div className="border-t border-[rgba(255,255,255,0.06)] bg-white/[0.005] px-5 py-4 flex justify-between items-center text-xs">
            <span className="text-gray-500 font-semibold">Cumulative Maintenance Expenditure:</span>
            <span className="font-mono text-sm font-extrabold text-white">
              ${maintenanceLogs.reduce((acc, curr) => acc + curr.cost, 0).toLocaleString()} USD
            </span>
          </div>

        </div>
      </div>

    </motion.div>
  );
};
