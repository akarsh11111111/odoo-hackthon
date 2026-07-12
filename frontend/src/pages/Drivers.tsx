import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, UserPlus, ShieldAlert, Award, Star, Trash2, X, Activity, User, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

export const Drivers: React.FC = () => {
  const { drivers, addDriver, deleteDriver, updateDriver } = useStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Selected driver for details side drawer
  const [selectedDriverId, setSelectedDriverId] = useState<string | null>(null);

  // Modal form states
  const [formName, setFormName] = useState('');
  const [formLicense, setFormLicense] = useState('');
  const [formLicenseType, setFormLicenseType] = useState('CDL-A');
  const [formStatus, setFormStatus] = useState<'Active' | 'On Leave' | 'Suspended'>('Active');
  const [formSafetyScore, setFormSafetyScore] = useState<number>(95);

  const handleAddDriverSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formName || !formLicense) {
      toast.error('Please fill in driver name and commercial license number.');
      return;
    }

    addDriver({
      name: formName,
      licenseNo: formLicense,
      licenseType: formLicenseType,
      expiryDate: new Date(Date.now() + 365 * 4 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 4 years validity
      status: formStatus,
      safetyScore: formSafetyScore,
      safeHours: 0
    });

    toast.success(`Registered driver profile for ${formName}`);
    setIsModalOpen(false);

    // reset
    setFormName('');
    setFormLicense('');
    setFormSafetyScore(95);
    setFormStatus('Active');
  };

  const filteredDrivers = drivers.filter((d) => {
    const matchesSearch = d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          d.licenseNo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || d.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // Scorecard stats
  const avgSafetyScore = Math.round(drivers.reduce((acc, curr) => acc + curr.safetyScore, 0) / drivers.length);
  const totalSafeHours = drivers.reduce((acc, curr) => acc + curr.safeHours, 0);

  const activeDrawerDriver = drivers.find(d => d.id === selectedDriverId);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative"
    >
      
      {/* Top Level Safety Scorecard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Average Safety Rating</span>
            <span className="text-2xl font-black text-[#4ADE80] font-sans mt-1 block">{avgSafetyScore}%</span>
            <span className="text-[10px] text-gray-400 block mt-1">Class A rating target met</span>
          </div>
          <div className="h-10 w-10 bg-[#4ADE80]/10 rounded-lg flex items-center justify-center text-[#4ADE80]">
            <Award className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Total Safe Hours Run</span>
            <span className="text-2xl font-black text-white font-sans mt-1 block">{totalSafeHours.toLocaleString()} hrs</span>
            <span className="text-[10px] text-[#4EA8DE] block mt-1 font-semibold">Accumulated without delays</span>
          </div>
          <div className="h-10 w-10 bg-[#4EA8DE]/10 rounded-lg flex items-center justify-center text-[#4EA8DE]">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Speeding Flagged</span>
            <span className="text-2xl font-black text-[#F59E0B] font-sans mt-1 block">2</span>
            <span className="text-[10px] text-gray-400 block mt-1">This calendar month</span>
          </div>
          <div className="h-10 w-10 bg-[#F59E0B]/10 rounded-lg flex items-center justify-center text-[#F59E0B]">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Harsh Braking</span>
            <span className="text-2xl font-black text-white font-sans mt-1 block">4</span>
            <span className="text-[10px] text-gray-400 block mt-1">Sensors automated metrics</span>
          </div>
          <div className="h-10 w-10 bg-white/5 rounded-lg flex items-center justify-center text-gray-400">
            <Star className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and search row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#161A22] p-4 rounded-xl border border-[rgba(255,255,255,0.06)] shadow-md">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="relative flex-1 min-w-[240px] max-w-sm">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by driver name or commercial license..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] hover:border-white/10 rounded-lg pl-9 pr-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#D88A1D] transition"
            />
          </div>

          <div className="flex items-center gap-2 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] px-3 py-2 rounded-lg">
            <span className="text-[10px] font-bold text-gray-500 uppercase">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-xs text-white border-none focus:outline-none cursor-pointer"
            >
              <option value="All" className="bg-[#111318]">All Drivers</option>
              <option value="Active" className="bg-[#111318]">Active</option>
              <option value="On Leave" className="bg-[#111318]">On Leave</option>
              <option value="Suspended" className="bg-[#111318]">Suspended</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button 
            onClick={() => {
              toast.message('Assembling personnel records: exporting CSV...');
              setTimeout(() => toast.success('Drivers roster exported as CSV.'), 800);
            }}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-2 rounded-lg transition cursor-pointer"
          >
            Export CSV
          </button>
          <button 
            onClick={() => {
              toast.message('Generating personnel sheet: exporting Excel...');
              setTimeout(() => toast.success('Drivers roster exported as Excel XLSX.'), 800);
            }}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-2 rounded-lg transition cursor-pointer"
          >
            Export Excel
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs px-4 py-2.5 rounded-lg shadow-lg hover:brightness-105 transition flex items-center justify-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            Add Driver
          </button>
        </div>
      </div>

      {/* Main layout grid for drivers registry */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* Drivers Table Registry Panel */}
        <div className={`bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl transition-all duration-300 ${
          selectedDriverId ? 'xl:col-span-8' : 'xl:col-span-12'
        }`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                  <th className="p-4">Driver Name</th>
                  <th className="p-4">License No</th>
                  <th className="p-4">Class</th>
                  <th className="p-4">License Expiration</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Safe Driving Record</th>
                  <th className="p-4">Safety Score</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300">
                {filteredDrivers.map((driver) => (
                  <tr 
                    key={driver.id} 
                    onClick={() => setSelectedDriverId(driver.id)}
                    className={`hover:bg-white/[0.01] cursor-pointer transition apple-transition ${
                      selectedDriverId === driver.id ? 'bg-white/[0.02]' : ''
                    }`}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="h-7 w-7 rounded-full bg-gray-800 border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-white text-[10px] font-bold">
                          {driver.name.slice(0, 2).toUpperCase()}
                        </div>
                        <span className="font-bold text-white text-xs">{driver.name}</span>
                      </div>
                    </td>
                    <td className="p-4 font-mono text-gray-400">{driver.licenseNo}</td>
                    <td className="p-4 text-white font-medium">{driver.licenseType}</td>
                    <td className="p-4 text-gray-500">{driver.expiryDate}</td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold ${
                        driver.status === 'Active' 
                          ? 'bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/15' 
                          : driver.status === 'On Leave' 
                          ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/15' 
                          : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/15'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${
                          driver.status === 'Active' ? 'bg-[#4ADE80] animate-pulse' : driver.status === 'On Leave' ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
                        }`}></span>
                        {driver.status}
                      </span>
                    </td>
                    <td className="p-4 font-mono font-semibold text-white">{driver.safeHours.toLocaleString()} hours</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-800 h-2 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${
                              driver.safetyScore >= 90 ? 'bg-[#4ADE80]' : driver.safetyScore >= 80 ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
                            }`}
                            style={{ width: `${driver.safetyScore}%` }}
                          ></div>
                        </div>
                        <span className={`font-bold font-mono text-[11px] ${
                          driver.safetyScore >= 90 ? 'text-[#4ADE80]' : driver.safetyScore >= 80 ? 'text-[#F59E0B]' : 'text-[#EF4444]'
                        }`}>
                          {driver.safetyScore}%
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="inline-flex gap-2">
                        <button 
                          onClick={() => {
                            const targetStatus = driver.status === 'Active' ? 'On Leave' : 'Active';
                            updateDriver(driver.id, { status: targetStatus });
                            toast.success(`Status updated for ${driver.name}`);
                          }}
                          className="bg-white/[0.04] hover:bg-white/10 text-white px-2.5 py-1 rounded text-[10px] font-semibold transition"
                        >
                          Adjust
                        </button>
                        <button 
                          onClick={() => {
                            deleteDriver(driver.id);
                            if (selectedDriverId === driver.id) setSelectedDriverId(null);
                            toast.success(`Deregistered driver: ${driver.name}`);
                          }}
                          className="text-gray-500 hover:text-red-400 p-1 rounded hover:bg-red-500/10 transition"
                          title="Delete profile"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Slide-out details drawer for selected driver */}
        <AnimatePresence>
          {activeDrawerDriver && (
            <motion.div 
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              className="xl:col-span-4 bg-[#11141B] rounded-xl border border-[#00F5FF]/15 shadow-2xl p-5 space-y-5 relative font-mono text-xs"
            >
              <button 
                onClick={() => setSelectedDriverId(null)}
                className="absolute right-4 top-4 text-gray-500 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Identity Header */}
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-full bg-gray-800 border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-white text-xs font-bold font-sans">
                  {activeDrawerDriver.name.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <h4 className="text-white font-extrabold text-xs leading-none">{activeDrawerDriver.name.toUpperCase()}</h4>
                  <span className="text-[9px] text-gray-500 font-mono block mt-1.5">NODE: {activeDrawerDriver.id} // CLASS: {activeDrawerDriver.licenseType}</span>
                </div>
              </div>

              {/* Safety Score Circle */}
              <div className="p-3 bg-[#08090C] rounded-xl border border-[rgba(0,245,255,0.06)] flex items-center justify-between">
                <div>
                  <span className="text-[8px] font-bold text-gray-500 uppercase tracking-wider block">Operator Safety Index</span>
                  <span className={`text-base font-black font-sans mt-0.5 block ${
                    activeDrawerDriver.safetyScore >= 90 ? 'text-[#39FF14]' : activeDrawerDriver.safetyScore >= 80 ? 'text-yellow-400' : 'text-[#FF3131]'
                  }`}>
                    {activeDrawerDriver.safetyScore}% Compliance
                  </span>
                </div>
                <div className="h-8 w-8 bg-white/5 rounded-lg flex items-center justify-center text-gray-400">
                  <User className="w-4.5 h-4.5" />
                </div>
              </div>

              {/* Safety recommendation alerts */}
              {activeDrawerDriver.safetyScore < 90 && (
                <div className="p-3 bg-red-500/10 border border-red-500/15 text-red-300 rounded-lg text-[10px] flex gap-2">
                  <ShieldAlert className="w-4.5 h-4.5 flex-shrink-0" />
                  <div>
                    <span className="font-bold">AI Safety Notification</span>
                    <p className="mt-0.5 leading-tight text-red-400">Safety compliance score is below class standard. Mandatory route briefing recommended.</p>
                  </div>
                </div>
              )}
              
              {activeDrawerDriver.safetyScore >= 90 && (
                <div className="p-3 bg-[#4ADE80]/10 border border-[#4ADE80]/15 text-[#4ADE80] rounded-lg text-[10px] flex gap-2">
                  <CheckCircle className="w-4.5 h-4.5 flex-shrink-0" />
                  <div>
                    <span className="font-bold">Elite Driver Standard</span>
                    <p className="mt-0.5 leading-tight text-gray-400">Operator qualifies for high-priority heavy cargo dispatches.</p>
                  </div>
                </div>
              )}

              {/* License Logs */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Licensing Credentials logs</span>
                <div className="space-y-1.5 text-xs text-gray-300 font-mono">
                  <div className="flex justify-between items-center p-2 bg-[#0F1117]/40 rounded">
                    <span>CDL License:</span>
                    <span className="text-white">{activeDrawerDriver.licenseNo}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-[#0F1117]/40 rounded">
                    <span>Expiration Date:</span>
                    <span className="text-white">{activeDrawerDriver.expiryDate}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-[#0F1117]/40 rounded">
                    <span>Hours Logged:</span>
                    <span className="text-white">{activeDrawerDriver.safeHours.toLocaleString()} hrs</span>
                  </div>
                </div>
              </div>

              {/* Driver transit violation timeline */}
              <div className="space-y-2 pt-2 border-t border-[rgba(255,255,255,0.06)]">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Sensor Violations timeline</span>
                <div className="space-y-2 pl-2 border-l border-[rgba(255,255,255,0.06)]">
                  <div className="text-[11px] relative">
                    <span className="h-1.5 w-1.5 bg-[#4ADE80] rounded-full absolute -left-[11.5px] top-1"></span>
                    <span className="text-white font-bold block">No severe sensor violations</span>
                    <span className="text-[9px] text-gray-500 font-medium">Auto-scanned logs clean this month</span>
                  </div>
                </div>
              </div>

            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Driver Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.08)] shadow-2xl p-6 text-gray-300 relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute right-4 top-4 text-gray-500 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h4 className="text-white font-extrabold text-base tracking-tight mb-1">Add Driver Profile</h4>
            <p className="text-xs text-gray-500 mb-6">Create safety profile credentials for commercial CDL drivers.</p>

            <form onSubmit={handleAddDriverSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Driver Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">CDL License Number</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. DL-987654"
                  value={formLicense}
                  onChange={(e) => setFormLicense(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">License Class</label>
                  <select
                    value={formLicenseType}
                    onChange={(e) => setFormLicenseType(e.target.value)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  >
                    <option value="CDL-A">Class CDL-A</option>
                    <option value="CDL-B">Class CDL-B</option>
                    <option value="Standard">Standard Operator</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Starting Safety Score (%)</label>
                  <input
                    type="number"
                    min="50"
                    max="100"
                    required
                    value={formSafetyScore}
                    onChange={(e) => setFormSafetyScore(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Status</label>
                <select
                  value={formStatus}
                  onChange={(e) => setFormStatus(e.target.value as any)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  <option value="Active">Active</option>
                  <option value="On Leave">On Leave</option>
                  <option value="Suspended">Suspended</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all mt-4"
              >
                Register Driver Profile
              </button>
            </form>
          </div>
        </div>
      )}

    </motion.div>
  );
};
