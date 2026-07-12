import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Plus, Trash2, Edit3, X, HelpCircle, ShieldCheck, Heart, ClipboardList, Fuel } from 'lucide-react';
import { toast } from 'sonner';

export const Fleet: React.FC = () => {
  const { vehicles, addVehicle, deleteVehicle, updateVehicle } = useStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  // Selected vehicle for details side drawer
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);

  // State for adding a vehicle manually
  const [formType, setFormType] = useState('Dry Van');
  const [formPlate, setFormPlate] = useState('');
  const [formModel, setFormModel] = useState('');
  const [formStatus, setFormStatus] = useState<'Active' | 'Maintenance' | 'Inactive'>('Active');
  const [formMileage, setFormMileage] = useState<number>(0);

  const handleAddVehicleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formPlate || !formModel) {
      toast.error('Please fill in the plate number and vehicle model.');
      return;
    }

    addVehicle({
      type: formType,
      plate: formPlate,
      model: formModel,
      status: formStatus,
      lastMaintenance: new Date().toISOString().split('T')[0],
      nextMaintenance: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      mileage: formMileage
    });

    toast.success(`Successfully registered new asset: ${formPlate}`);
    setIsModalOpen(false);
    
    // Clear form
    setFormPlate('');
    setFormModel('');
    setFormMileage(0);
    setFormStatus('Active');
  };

  const filteredVehicles = vehicles.filter((v) => {
    const matchesSearch = v.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          v.plate.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          v.model.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'All' || v.status === statusFilter;
    const matchesType = typeFilter === 'All' || v.type === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  // Pagination details
  const totalPages = Math.ceil(filteredVehicles.length / itemsPerPage);
  const paginatedVehicles = filteredVehicles.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const activeDrawerVehicle = vehicles.find(v => v.id === selectedVehicleId);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative"
    >
      
      {/* Search and Filters Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#161A22] p-4 rounded-xl border border-[rgba(255,255,255,0.06)] shadow-md">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          {/* Search */}
          <div className="relative flex-1 min-w-[240px] max-w-sm">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by vehicle ID, model, plate..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] hover:border-white/10 rounded-lg pl-9 pr-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#D88A1D] transition"
            />
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] px-3 py-2 rounded-lg">
            <span className="text-[10px] font-bold text-gray-500 uppercase">Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent text-xs text-white border-none focus:outline-none cursor-pointer"
            >
              <option value="All" className="bg-[#111318]">All Types</option>
              <option value="Flatbed" className="bg-[#111318]">Flatbed</option>
              <option value="Dry Van" className="bg-[#111318]">Dry Van</option>
              <option value="Reefer" className="bg-[#111318]">Reefer</option>
              <option value="Tanker" className="bg-[#111318]">Tanker</option>
              <option value="Box Truck" className="bg-[#111318]">Box Truck</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] px-3 py-2 rounded-lg">
            <span className="text-[10px] font-bold text-gray-500 uppercase">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent text-xs text-white border-none focus:outline-none cursor-pointer"
            >
              <option value="All" className="bg-[#111318]">All Status</option>
              <option value="Active" className="bg-[#111318]">Active</option>
              <option value="Maintenance" className="bg-[#111318]">Maintenance</option>
              <option value="Inactive" className="bg-[#111318]">Inactive</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button 
            onClick={() => {
              toast.message('Compiling registry dataset: exporting CSV...');
              setTimeout(() => toast.success('Fleet registry exported as CSV.'), 800);
            }}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-2 rounded-lg transition cursor-pointer"
          >
            Export CSV
          </button>
          <button 
            onClick={() => {
              toast.message('Generating spreadsheet: exporting Excel...');
              setTimeout(() => toast.success('Fleet spreadsheet exported as Excel XLSX.'), 800);
            }}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-2 rounded-lg transition cursor-pointer"
          >
            Export Excel
          </button>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs px-4 py-2.5 rounded-lg shadow-lg hover:brightness-105 transition flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Vehicle
          </button>
        </div>
      </div>

      {/* Grid container to accommodate drawer layout when open */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        
        {/* Vehicles Table Registry Panel */}
        <div className={`bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl transition-all duration-300 ${
          selectedVehicleId ? 'xl:col-span-8' : 'xl:col-span-12'
        }`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                  <th className="p-4">Vehicle ID</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Model Description</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Mileage</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300">
                {paginatedVehicles.map((vehicle) => (
                  <tr 
                    key={vehicle.id} 
                    onClick={() => setSelectedVehicleId(vehicle.id)}
                    className={`hover:bg-white/[0.01] cursor-pointer transition apple-transition ${
                      selectedVehicleId === vehicle.id ? 'bg-white/[0.02]' : ''
                    }`}
                  >
                    <td className="p-4 font-mono font-bold text-[#4EA8DE]">{vehicle.id}</td>
                    <td className="p-4 text-white font-medium">{vehicle.type}</td>
                    <td className="p-4 font-mono text-gray-400">{vehicle.plate}</td>
                    <td className="p-4 text-white">{vehicle.model}</td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold ${
                        vehicle.status === 'Active' 
                          ? 'bg-[#4ADE80]/10 text-[#4ADE80] border border-[#4ADE80]/15' 
                          : vehicle.status === 'Maintenance' 
                          ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/15' 
                          : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/15'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${
                          vehicle.status === 'Active' ? 'bg-[#4ADE80] animate-pulse' : vehicle.status === 'Maintenance' ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'
                        }`}></span>
                        {vehicle.status}
                      </span>
                    </td>
                    <td className="p-4 font-mono font-semibold text-white">{vehicle.mileage.toLocaleString()} mi</td>
                    <td className="p-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="inline-flex gap-2.5">
                        <button 
                          onClick={() => {
                            const targetStatus = vehicle.status === 'Active' ? 'Maintenance' : 'Active';
                            updateVehicle(vehicle.id, { status: targetStatus });
                            toast.success(`Uptime status toggled for ${vehicle.id}`);
                          }}
                          className="text-gray-400 hover:text-white p-1 rounded hover:bg-white/5 transition"
                          title="Toggle Maintenance State"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => {
                            deleteVehicle(vehicle.id);
                            if (selectedVehicleId === vehicle.id) setSelectedVehicleId(null);
                            toast.success(`Deregistered asset: ${vehicle.id}`);
                          }}
                          className="text-gray-500 hover:text-red-400 p-1 rounded hover:bg-red-500/10 transition"
                          title="Deregister Asset"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {filteredVehicles.length === 0 && (
                  <tr>
                    <td colSpan={7} className="p-12 text-center text-gray-500">
                      <HelpCircle className="w-8 h-8 text-gray-600 mx-auto mb-3" />
                      No registered assets matched your active search query.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Table Pagination Footer */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-[rgba(255,255,255,0.06)] px-4 py-3.5 bg-white/[0.005]">
              <span className="text-xs text-gray-500">
                Showing page {currentPage} of {totalPages}
              </span>
              <div className="inline-flex gap-2">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((c) => c - 1)}
                  className="bg-white/[0.04] border border-[rgba(255,255,255,0.06)] px-3 py-1.5 rounded text-[11px] text-white disabled:opacity-40 transition"
                >
                  Previous
                </button>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((c) => c + 1)}
                  className="bg-white/[0.04] border border-[rgba(255,255,255,0.06)] px-3 py-1.5 rounded text-[11px] text-white disabled:opacity-40 transition"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Slide-out details drawer when a vehicle is selected */}
        <AnimatePresence>
          {activeDrawerVehicle && (
            <motion.div 
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              className="xl:col-span-4 bg-[#11141B] rounded-xl border border-[#00F5FF]/15 shadow-2xl p-5 space-y-5 relative font-mono text-xs"
            >
              <button 
                onClick={() => setSelectedVehicleId(null)}
                className="absolute right-4 top-4 text-gray-500 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Title / Make */}
              <div>
                <span className="font-mono text-[9px] font-bold text-[#00F5FF]">{activeDrawerVehicle.id}</span>
                <h4 className="text-white font-extrabold text-sm mt-0.5 leading-none">{activeDrawerVehicle.model.toUpperCase()}</h4>
                <p className="text-[9px] text-gray-500 font-bold uppercase mt-1.5">{activeDrawerVehicle.type} // PLATE: {activeDrawerVehicle.plate}</p>
              </div>

              {/* Cybernetic Wireframe SVG Diagram */}
              <div className="border border-[rgba(0,245,255,0.06)] bg-[#08090C] rounded-lg p-3 flex flex-col items-center justify-center relative overflow-hidden">
                <span className="absolute top-1 left-2 text-[7px] text-gray-600 font-bold uppercase">Telemetry Vector Chassis Scan</span>
                <svg className="w-48 h-16 mt-2 text-[#00F5FF] opacity-60" viewBox="0 0 120 40" fill="none" stroke="currentColor" strokeWidth="0.8">
                  {/* Truck cab */}
                  <path d="M15,30 L15,18 L25,18 L32,24 L32,30 Z" />
                  {/* Cargo container box */}
                  <rect x="35" y="10" width="70" height="20" />
                  {/* Connector axle */}
                  <line x1="32" y1="28" x2="35" y2="28" />
                  {/* Wheels Cab */}
                  <circle cx="20" cy="32" r="3.5" />
                  {/* Wheels Container */}
                  <circle cx="50" cy="32" r="3.5" />
                  <circle cx="85" cy="32" r="3.5" />
                  <circle cx="95" cy="32" r="3.5" />
                  {/* Axle connector lines */}
                  <line x1="20" y1="32" x2="95" y2="32" strokeDasharray="2,2" />
                  {/* Active Sensor Nodes (Flashing Dots) */}
                  <circle cx="25" cy="18" r="1.5" fill="#39FF14" stroke="none" />
                  <circle cx="70" cy="10" r="1.5" fill="#00F5FF" stroke="none" />
                  <circle cx="100" cy="20" r="1.5" fill="#39FF14" stroke="none" strokeWidth="0" />
                </svg>
                <div className="flex gap-4 text-[7px] text-gray-500 uppercase mt-2">
                  <span>Cab: <span className="text-[#39FF14]">SECURE</span></span>
                  <span>Payload: <span className="text-[#00F5FF]">NOMINAL</span></span>
                  <span>Sensor Sync: <span className="text-[#39FF14]">OK</span></span>
                </div>
              </div>

              {/* Health Score Gauge */}
              <div className="p-3 bg-[#08090C] rounded-xl border border-[rgba(0,245,255,0.06)] flex items-center justify-between">
                <div>
                  <span className="text-[8px] font-bold text-gray-500 uppercase tracking-wider block">Mechanical Health coefficient</span>
                  <span className="text-base font-black text-[#39FF14] font-mono mt-0.5 block">96 / 100</span>
                </div>
                <div className="h-8 w-8 bg-[#39FF14]/10 rounded-lg flex items-center justify-center text-[#39FF14] border border-[#39FF14]/20">
                  <Heart className="w-4 h-4" />
                </div>
              </div>

              {/* Documents & Credentials Checked */}
              <div className="space-y-2">
                <span className="text-[8px] font-bold text-gray-500 uppercase tracking-wider block">Security Registry Logs</span>
                <div className="grid grid-cols-2 gap-2 text-[9px] font-mono text-gray-400">
                  <div className="flex items-center gap-1.5 p-2 bg-[#08090C] border border-[rgba(0,245,255,0.04)] rounded">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#39FF14]" />
                    <span>Insurance: Valid</span>
                  </div>
                  <div className="flex items-center gap-1.5 p-2 bg-[#08090C] border border-[rgba(0,245,255,0.04)] rounded">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#39FF14]" />
                    <span>Emissions: Clear</span>
                  </div>
                  <div className="flex items-center gap-1.5 p-2 bg-[#08090C] border border-[rgba(0,245,255,0.04)] rounded">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#39FF14]" />
                    <span>RC License: Logged</span>
                  </div>
                  <div className="flex items-center gap-1.5 p-2 bg-[#08090C] border border-[rgba(0,245,255,0.04)] rounded">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#39FF14]" />
                    <span>Permits: Verified</span>
                  </div>
                </div>
              </div>

              {/* Telemetry log summaries */}
              <div className="space-y-2 pt-2 border-t border-[rgba(255,255,255,0.06)]">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Maintenance Reminders</span>
                <div className="space-y-1.5 text-xs text-gray-300">
                  <div className="flex justify-between items-center bg-[#0F1117]/40 p-2 rounded">
                    <div className="flex items-center gap-2">
                      <ClipboardList className="w-3.5 h-3.5 text-[#F59E0B]" />
                      <span className="text-[11px]">Air filter service required</span>
                    </div>
                    <span className="text-[9px] text-[#F59E0B] font-bold">12 days left</span>
                  </div>
                  <div className="flex justify-between items-center bg-[#0F1117]/40 p-2 rounded">
                    <div className="flex items-center gap-2">
                      <Fuel className="w-3.5 h-3.5 text-[#4EA8DE]" />
                      <span className="text-[11px]">Last logged refuel</span>
                    </div>
                    <span className="text-[10px] font-mono text-gray-400">450 L @ TX Hub</span>
                  </div>
                </div>
              </div>

              {/* Route run timeline */}
              <div className="space-y-2 pt-2 border-t border-[rgba(255,255,255,0.06)]">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Active Transit History</span>
                <div className="space-y-2 pl-2 border-l border-[rgba(255,255,255,0.06)]">
                  <div className="text-[11px] relative">
                    <span className="h-1.5 w-1.5 bg-[#4ADE80] rounded-full absolute -left-[11.5px] top-1"></span>
                    <span className="text-white font-bold block">Houston → Dallas route run</span>
                    <span className="text-[9px] text-gray-500 font-medium">Logged completed by John Doe • 4 hrs</span>
                  </div>
                  <div className="text-[11px] relative">
                    <span className="h-1.5 w-1.5 bg-gray-600 rounded-full absolute -left-[11.5px] top-1"></span>
                    <span className="text-gray-400 block">General Preventive Mechanical check</span>
                    <span className="text-[9px] text-gray-500 font-medium">Logged at Speedy Fleet workshop • 01/10/24</span>
                  </div>
                </div>
              </div>

            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Add Vehicle Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.08)] shadow-2xl p-6 text-gray-300 relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute right-4 top-4 text-gray-500 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h4 className="text-white font-extrabold text-base tracking-tight mb-1">Register New Fleet Asset</h4>
            <p className="text-xs text-gray-500 mb-6">Assign license plate telemetry and make to start logs.</p>

            <form onSubmit={handleAddVehicleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Asset Type</label>
                <select
                  value={formType}
                  onChange={(e) => setFormType(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  <option value="Dry Van">Dry Van</option>
                  <option value="Flatbed">Flatbed</option>
                  <option value="Reefer">Reefer</option>
                  <option value="Tanker">Tanker</option>
                  <option value="Box Truck">Box Truck</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">License Plate</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TX-7890"
                  value={formPlate}
                  onChange={(e) => setFormPlate(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Model Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Peterbilt 579"
                  value={formModel}
                  onChange={(e) => setFormModel(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Odometer (mi)</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={formMileage}
                    onChange={(e) => setFormMileage(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Status</label>
                  <select
                    value={formStatus}
                    onChange={(e) => setFormStatus(e.target.value as any)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  >
                    <option value="Active">Active</option>
                    <option value="Maintenance">Maintenance</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all mt-4"
              >
                Register Asset
              </button>
            </form>
          </div>
        </div>
      )}

    </motion.div>
  );
};
