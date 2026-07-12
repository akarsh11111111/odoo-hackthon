import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { motion } from 'framer-motion';
import { MapCanvas } from '../components/MapCanvas';
import { Send, Play, ShieldAlert, CheckCircle2, Sparkles, Navigation } from 'lucide-react';
import { toast } from 'sonner';

export const Dispatcher: React.FC = () => {
  const { vehicles, drivers, trips, addTrip, completeTrip } = useStore();

  const availableVehicles = vehicles.filter(v => v.status === 'Active');
  const availableDrivers = drivers.filter(d => d.status === 'Active');

  // Form states
  const [selectedVehicle, setSelectedVehicle] = useState(availableVehicles[0]?.id || '');
  const [selectedDriver, setSelectedDriver] = useState(availableDrivers[0]?.id || '');
  const [routeFrom, setRouteFrom] = useState('Houston, TX');
  const [routeTo, setRouteTo] = useState('Dallas, TX');
  const [cargoType, setCargoType] = useState('Electronics');
  const [cargoWeight, setCargoWeight] = useState(15000);
  const [priority, setPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
  const [eta, setEta] = useState('12:30');

  // Map overlays state
  const [trafficLayer, setTrafficLayer] = useState(true);
  const [weatherRadar, setWeatherRadar] = useState(false);
  const [satelliteView, setSatelliteView] = useState(false);

  const handleDispatch = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedVehicle || !selectedDriver || !routeFrom || !routeTo) {
      toast.error('All fields must be verified before live dispatch authority.');
      return;
    }

    if (routeFrom === routeTo) {
      toast.error('Destination city cannot equal source dispatch node.');
      return;
    }

    addTrip({
      vehicleId: selectedVehicle,
      driverId: selectedDriver,
      cargoType,
      weight: cargoWeight,
      routeFrom,
      routeTo,
      dispatchTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      eta,
      priority,
      status: 'In-Transit'
    });

    toast.success(`Live Dispatch Authorized: Route transmitted to driver terminal.`);
  };

  const activeTrips = trips.filter(t => t.status !== 'Completed');

  const cityOptions = [
    'Houston, TX',
    'Dallas, TX',
    'Los Angeles, CA',
    'Phoenix, AZ',
    'New York, NY',
    'Boston, MA',
    'Chicago, IL',
    'Indianapolis, IN',
    'Denver, CO',
    'Atlanta, GA'
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative"
    >
      
      {/* Left side: Dispatch Form & AI Optimization */}
      <div className="lg:col-span-4 space-y-6">
        
        {/* Form Container */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-2xl">
          <div className="border-b border-[rgba(255,255,255,0.06)] pb-3 mb-5">
            <h4 className="text-white font-bold text-sm font-sans flex items-center gap-2">
              <Send className="w-4 h-4 text-[#D88A1D]" />
              New Live Run Dispatch
            </h4>
            <p className="text-xs text-gray-500 mt-0.5">Authorize CDL operator route runs</p>
          </div>

          <form onSubmit={handleDispatch} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Select Fleet Asset</label>
              <select
                value={selectedVehicle}
                onChange={(e) => setSelectedVehicle(e.target.value)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
              >
                {availableVehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.id} — {v.model} ({v.type})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Assign Licensed Driver</label>
              <select
                value={selectedDriver}
                onChange={(e) => setSelectedDriver(e.target.value)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
              >
                {availableDrivers.map(d => (
                  <option key={d.id} value={d.id}>{d.name} — CDL Verified (Score: {d.safetyScore}%)</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Route From</label>
                <select
                  value={routeFrom}
                  onChange={(e) => setRouteFrom(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  {cityOptions.map(city => (
                    <option key={`from-${city}`} value={city}>{city}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Route To</label>
                <select
                  value={routeTo}
                  onChange={(e) => setRouteTo(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  {cityOptions.map(city => (
                    <option key={`to-${city}`} value={city}>{city}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Cargo Descriptor</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Frozen Foods"
                  value={cargoType}
                  onChange={(e) => setCargoType(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Cargo Weight (kg)</label>
                <input
                  type="number"
                  required
                  min="0"
                  value={cargoWeight}
                  onChange={(e) => setCargoWeight(Number(e.target.value))}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  <option value="High">High Priority</option>
                  <option value="Medium">Medium Priority</option>
                  <option value="Low">Low Priority</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Estimated ETA</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 14:30"
                  value={eta}
                  onChange={(e) => setEta(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>
            </div>

            {/* Smart CDL warning hint */}
            <div className="p-3 bg-blue-500/10 border border-blue-500/15 rounded-lg text-[10px] text-[#4EA8DE] flex gap-2">
              <ShieldAlert className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>Commercial CDL-A checked. Pre-trip inspection checklist auto-sent to operator cab.</span>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all flex items-center justify-center gap-2 mt-4"
            >
              <Play className="w-4 h-4" />
              Transmit Live Run Order
            </button>
          </form>
        </div>

        {/* AI Route Optimizer Recommendations */}
        <div className="bg-[#161A22] rounded-xl border border-[#D88A1D]/20 p-4 shadow-lg space-y-3">
          <span className="text-[10px] font-bold text-[#D88A1D] uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
            AI Dispatch Optimization Suggestion
          </span>
          <p className="text-[11px] text-gray-300 leading-tight">
            Routing <span className="text-[#4EA8DE] font-mono font-bold">VEH-0987</span> via <span className="font-bold">I-45 North Bypass</span> circumvents a 45-minute congestion bottleneck near Dallas.
          </p>
          <div className="flex justify-between items-center pt-1">
            <span className="text-[9px] text-gray-500">Calculated fuel saving: 6.2%</span>
            <button 
              onClick={() => {
                setRouteTo('Dallas, TX (Bypass)');
                toast.success('AI Optimized Route bypass loaded into dispatch forms.');
              }}
              className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/15 text-white text-[9px] font-bold px-2 py-1 rounded transition"
            >
              Apply Bypass
            </button>
          </div>
        </div>
      </div>

      {/* Right side: Map Canvas & Active dispatch queue table */}
      <div className="lg:col-span-8 space-y-6">
        
        {/* Telemetry Map and overlay controls */}
        <div className="space-y-3 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 shadow-2xl">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Navigation className="w-4 h-4 text-[#D88A1D]" />
              <span className="text-white text-xs font-bold font-sans">Active Satellite Transit Radar</span>
            </div>
            
            {/* Map overlays controllers */}
            <div className="flex gap-2">
              <button 
                onClick={() => setTrafficLayer(!trafficLayer)}
                className={`text-[9px] font-bold px-2 py-1 rounded border transition ${
                  trafficLayer ? 'bg-[#4EA8DE]/10 border-[#4EA8DE]/20 text-[#4EA8DE]' : 'bg-[#0F1117] border-[rgba(255,255,255,0.04)] text-gray-500'
                }`}
              >
                Traffic Overlay
              </button>
              <button 
                onClick={() => setWeatherRadar(!weatherRadar)}
                className={`text-[9px] font-bold px-2 py-1 rounded border transition ${
                  weatherRadar ? 'bg-[#4ADE80]/10 border-[#4ADE80]/20 text-[#4ADE80]' : 'bg-[#0F1117] border-[rgba(255,255,255,0.04)] text-gray-500'
                }`}
              >
                Weather Radar
              </button>
              <button 
                onClick={() => setSatelliteView(!satelliteView)}
                className={`text-[9px] font-bold px-2 py-1 rounded border transition ${
                  satelliteView ? 'bg-[#D88A1D]/10 border-[#D88A1D]/20 text-[#D88A1D]' : 'bg-[#0F1117] border-[rgba(255,255,255,0.04)] text-gray-500'
                }`}
              >
                Satellite View
              </button>
            </div>
          </div>
          
          <MapCanvas />
        </div>

        {/* Dispatch Queue Table */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005]">
            <h5 className="text-white font-bold text-sm">Active Transit Operations Queue</h5>
            <p className="text-xs text-gray-500 mt-0.5">Real-time coordinates and telemetry updates</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                  <th className="p-3.5">Trip ID</th>
                  <th className="p-3.5">Asset / Driver</th>
                  <th className="p-3.5">Route Vector</th>
                  <th className="p-3.5">Load Weight</th>
                  <th className="p-3.5">Cargo Uptime</th>
                  <th className="p-3.5">Est. ETA</th>
                  <th className="p-3.5">Telemetry Progress</th>
                  <th className="p-3.5 text-right">Authority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300 font-mono">
                {activeTrips.map((trip) => {
                  const driverObj = drivers.find(d => d.id === trip.driverId);
                  return (
                    <tr key={trip.id} className="hover:bg-white/[0.01] transition duration-200">
                      <td className="p-3.5 font-mono font-bold text-[#00F5FF]">{trip.id}</td>
                      <td className="p-3.5">
                        <div className="font-bold text-white text-[11px]">{trip.vehicleId}</div>
                        <div className="text-[9px] text-gray-500 uppercase">{driverObj?.name || 'Unassigned'}</div>
                      </td>
                      <td className="p-3.5">
                        <div className="flex items-center gap-1.5 text-[10px]">
                          <span className="text-white font-bold">{trip.routeFrom.split(',')[0].toUpperCase()}</span>
                          <span className="text-[#00F5FF]">➔</span>
                          <span className="text-white font-bold">{trip.routeTo.split(',')[0].toUpperCase()}</span>
                        </div>
                        <div className="text-[7px] text-gray-600 uppercase tracking-widest mt-0.5">Vector Grid Route Link</div>
                      </td>
                      <td className="p-3.5 text-white">
                        <div className="text-[10px] font-bold">{trip.cargoType.toUpperCase()}</div>
                        <div className="text-[8px] text-gray-500">{trip.weight.toLocaleString()} kg payload</div>
                      </td>
                      <td className="p-3.5">
                        <div className="flex flex-col gap-1">
                          <span className="inline-flex items-center gap-1 text-[8px] font-bold text-[#39FF14] bg-[#39FF14]/10 px-2 py-0.5 rounded border border-[#39FF14]/15 w-max">
                            TEMP CTRLD: OK
                          </span>
                          <span className="inline-flex items-center gap-1 text-[8px] font-bold text-[#00F5FF] bg-[#00F5FF]/10 px-2 py-0.5 rounded border border-[#00F5FF]/15 w-max">
                            HAZMAT CLASS 9
                          </span>
                        </div>
                      </td>
                      <td className="p-3.5 font-mono font-bold text-white">{trip.eta}</td>
                      <td className="p-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-800 h-1.5 rounded-full overflow-hidden">
                            <div 
                              className="bg-gradient-to-r from-[#00F5FF] to-[#D88A1D] h-full rounded-full"
                              style={{ width: `${trip.progress}%` }}
                            ></div>
                          </div>
                          <span className="font-mono text-[9px] text-gray-400">{trip.progress}%</span>
                        </div>
                      </td>
                      <td className="p-3.5 text-right">
                        <button
                          onClick={() => {
                            completeTrip(trip.id);
                            toast.success(`Authorized arrival vectors signature for ${trip.id}.`);
                          }}
                          className="bg-[#39FF14]/10 hover:bg-[#39FF14]/20 text-[#39FF14] border border-[#39FF14]/15 px-2.5 py-1 rounded text-[9px] font-bold uppercase tracking-wider transition flex items-center justify-center gap-1.5 ml-auto cursor-pointer"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          Clear Vector
                        </button>
                      </td>
                    </tr>
                  );
                })}

                {activeTrips.length === 0 && (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-gray-500">
                      No active transport runs under surveillance.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </motion.div>
  );
};
