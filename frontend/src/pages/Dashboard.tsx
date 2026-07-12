import React, { useState, useEffect } from 'react';
import { useStore } from '../context/useStore';
import { SpotlightCard } from '../components/SpotlightCard';
import { motion } from 'framer-motion';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { 
  Truck, 
  Users, 
  Send, 
  AlertOctagon, 
  Zap, 
  CalendarClock, 
  TrendingUp, 
  Sparkles,
  CloudLightning,
  CheckSquare,
  Activity,
  Radar
} from 'lucide-react';
import { toast } from 'sonner';

export const Dashboard: React.FC = () => {
  const { vehicles, trips, alerts, resolveAlert } = useStore();

  // Simulated animated counts
  const [vehCount, setVehCount] = useState(0);
  const [driverCount, setDriverCount] = useState(0);
  const [tripCount, setTripCount] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 30;
    const stepTime = duration / steps;
    
    let currentStep = 0;
    const timer = setInterval(() => {
      currentStep++;
      setVehCount(Math.floor((93 / steps) * currentStep));
      setDriverCount(Math.floor((42 / steps) * currentStep));
      setTripCount(Math.floor((28 / steps) * currentStep));
      
      if (currentStep >= steps) {
        setVehCount(93);
        setDriverCount(42);
        setTripCount(28);
        clearInterval(timer);
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, []);

  const activeVehiclesCount = vehicles.filter(v => v.status === 'Active').length + 77;
  const inactiveVehiclesCount = 11;
  const pendingDispatchesCount = trips.filter(t => t.status === 'Scheduled').length + 11;
  const maintenanceAlertsCount = alerts.length;
  const fuelEfficiency = 7.8;
  const onTimeRate = 94;

  const fleetDistributionData = [
    { name: 'ACTIVE', value: activeVehiclesCount, color: '#39FF14' },
    { name: 'MAINTENANCE', value: 5, color: '#F59E0B' },
    { name: 'IDLE', value: inactiveVehiclesCount, color: '#FF3131' }
  ];

  const performanceData = [
    { name: 'Mon', trips: 18, delay: 2 },
    { name: 'Tue', trips: 24, delay: 1 },
    { name: 'Wed', trips: 28, delay: 3 },
    { name: 'Thu', trips: 22, delay: 1 },
    { name: 'Fri', trips: 31, delay: 2 },
    { name: 'Sat', trips: 15, delay: 0 },
    { name: 'Sun', trips: 12, delay: 0 }
  ];

  const [tasks, setTasks] = useState([
    { id: 1, text: 'Calibrate speed sensors on VEH-0987', checked: false },
    { id: 2, text: 'Confirm CDL Class A license clearances for dispatch logs', checked: true },
    { id: 3, text: 'Review preventive emissions compliance logs', checked: false }
  ]);

  const toggleTask = (id: number) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, checked: !t.checked } : t));
    toast.message('Mission task parameters updated.');
  };

  const handleInspectVehicle = (vehicleId: string) => {
    toast.message(`Routing satellite visual diagnostics to ${vehicleId}...`);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative font-mono text-xs"
    >
      
      {/* AI Mission Command Directive */}
      <div className="bg-gradient-to-r from-[#D88A1D]/10 via-[#00F5FF]/5 to-transparent border border-[#00F5FF]/10 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 scanline">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-[#00F5FF]/10 border border-[#00F5FF]/20 flex items-center justify-center text-[#00F5FF] flex-shrink-0">
            <Sparkles className="w-4.5 h-4.5 animate-pulse" />
          </div>
          <div>
            <span className="text-[#00F5FF] text-xs font-bold uppercase tracking-wider block">AI Operational Optimization Directive</span>
            <p className="text-[10px] text-gray-400 mt-0.5 leading-relaxed font-mono">
              PREDICTION: Rerouting <span className="text-[#D88A1D] font-bold">VEH-0987</span> to bypass I-45 bottlenecks improves fuel safety index by <span className="text-[#39FF14] font-bold">4.2%</span>.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[9px] text-gray-600 font-bold uppercase">Sweep latency: 0.2s</span>
          <button 
            onClick={() => toast.success('Optimization vector transmitted to dispatcher console.')}
            className="bg-[#D88A1D]/10 hover:bg-[#D88A1D]/20 border border-[#D88A1D]/30 text-[#D88A1D] text-[9px] font-bold px-3 py-1.5 rounded-lg transition uppercase tracking-wider cursor-pointer"
          >
            Apply Route Vector
          </button>
        </div>
      </div>

      {/* Tactical Telemetry Pods (Stat cards) */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#00F5FF]/30 transition duration-300" glowColor="rgba(0, 245, 255, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <Truck className="w-3.5 h-3.5 text-[#00F5FF]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Tractors</span>
          </div>
          <span className="text-xl font-black text-white block font-mono">{vehCount}</span>
          <span className="text-[8px] text-gray-500 mt-1 block">
            <span className="text-[#39FF14] font-bold">{activeVehiclesCount} Active</span> • {inactiveVehiclesCount} Idle
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#00F5FF]/30 transition duration-300" glowColor="rgba(0, 245, 255, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <Users className="w-3.5 h-3.5 text-[#00F5FF]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">CDL Operators</span>
          </div>
          <span className="text-xl font-black text-white block font-mono">{driverCount}</span>
          <span className="text-[8px] text-[#39FF14] mt-1 block font-bold">
            100% CDL Verified
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#D88A1D]/30 transition duration-300" glowColor="rgba(216, 138, 29, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <Send className="w-3.5 h-3.5 text-[#D88A1D]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Active Vectors</span>
          </div>
          <span className="text-xl font-black text-white block font-mono">{tripCount}</span>
          <span className="text-[8px] text-[#00F5FF] mt-1 block font-bold">
            SATELLITE SYNC OK
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#D88A1D]/30 transition duration-300" glowColor="rgba(216, 138, 29, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <CalendarClock className="w-3.5 h-3.5 text-[#D88A1D]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Queue</span>
          </div>
          <span className="text-xl font-black text-white block font-mono">{pendingDispatchesCount}</span>
          <span className="text-[8px] text-gray-500 mt-1 block">
            Awaiting dispatch
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#FF3131]/30 transition duration-300" glowColor="rgba(255, 49, 49, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <AlertOctagon className="w-3.5 h-3.5 text-[#FF3131]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Fault Flags</span>
          </div>
          <span className={`text-xl font-black block font-mono ${maintenanceAlertsCount > 0 ? 'text-[#FF3131]' : 'text-[#39FF14]'}`}>
            {maintenanceAlertsCount}
          </span>
          <span className="text-[8px] text-gray-500 mt-1 block">
            Telemetry issues
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#00F5FF]/30 transition duration-300" glowColor="rgba(0, 245, 255, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <Zap className="w-3.5 h-3.5 text-[#00F5FF]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Fuel index</span>
          </div>
          <span className="text-xl font-black text-white block font-mono">{fuelEfficiency}</span>
          <span className="text-[8px] text-gray-500 mt-1 block">
            Avg km per Liter
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4 bg-[#11141B] border border-white/[0.03] hover:border-[#00F5FF]/30 transition duration-300" glowColor="rgba(0, 245, 255, 0.05)">
          <div className="flex items-center gap-2 text-gray-500 mb-1">
            <TrendingUp className="w-3.5 h-3.5 text-[#00F5FF]" />
            <span className="text-[9px] font-bold uppercase tracking-wider">On-Time Uptime</span>
          </div>
          <span className="text-xl font-black text-[#39FF14] block font-mono">{onTimeRate}%</span>
          <span className="text-[8px] text-gray-500 mt-1 block">
            Global target: 92%
          </span>
        </SpotlightCard>
      </div>

      {/* Tactical Center Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Warning Logs Console (Left) */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-[#11141B] rounded-xl border border-[rgba(0,245,255,0.08)] overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-[rgba(255,255,255,0.04)] flex items-center justify-between bg-white/[0.005]">
              <div>
                <h4 className="text-white font-bold text-sm font-sans flex items-center gap-2">
                  <Activity className="w-4 h-4 text-[#00F5FF]" />
                  SYS_ALERT: ACTIVE SENSOR DIAGNOSTICS
                </h4>
                <p className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wide">Real-time transponder faults registered</p>
              </div>
              <span className="h-1.5 w-1.5 rounded-full bg-[#FF3131] animate-pulse"></span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[rgba(255,255,255,0.04)] bg-white/[0.002] text-gray-500 font-bold uppercase tracking-wider">
                    <th className="p-3.5">Asset ID</th>
                    <th className="p-3.5">Sys Severity</th>
                    <th className="p-3.5">Assigned Operator</th>
                    <th className="p-3.5">Diagnostic Code Descriptor</th>
                    <th className="p-3.5 text-right">Surveillance Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[rgba(255,255,255,0.04)] text-gray-300 font-mono">
                  {alerts.map((alert) => (
                    <tr key={alert.id} className="hover:bg-white/[0.01] transition duration-200">
                      <td className="p-3.5 font-bold text-[#00F5FF]">{alert.vehicleId}</td>
                      <td className="p-3.5">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[9px] font-bold ${
                          alert.status === 'Critical' 
                            ? 'bg-[#FF3131]/10 text-[#FF3131] border border-[#FF3131]/15' 
                            : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/15'
                        }`}>
                          <span className={`h-1 w-1 rounded-full ${alert.status === 'Critical' ? 'bg-[#FF3131] animate-ping' : 'bg-yellow-400'}`}></span>
                          {alert.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-3.5 text-white font-bold">{alert.driver}</td>
                      <td className="p-3.5 text-gray-400 text-[11px] truncate max-w-[200px]" title={alert.description}>
                        {alert.description}
                      </td>
                      <td className="p-3.5 text-right">
                        <div className="inline-flex gap-2">
                          <button 
                            onClick={() => handleInspectVehicle(alert.vehicleId)}
                            className="bg-[#00F5FF]/10 hover:bg-[#00F5FF]/20 border border-[#00F5FF]/25 text-[#00F5FF] px-2 py-1 rounded text-[9px] font-bold uppercase tracking-wider transition cursor-pointer"
                          >
                            Inspect
                          </button>
                          <button 
                            onClick={() => {
                              resolveAlert(alert.id);
                              toast.success(`Acknowledge logged: Alert ${alert.id} resolved.`);
                            }}
                            className="bg-[#D88A1D]/15 hover:bg-[#D88A1D]/25 text-[#D88A1D] border border-[#D88A1D]/20 px-2.5 py-1 rounded text-[9px] font-bold uppercase tracking-wider transition cursor-pointer"
                          >
                            Clear
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  
                  <tr className="hover:bg-white/[0.01] transition">
                    <td className="p-3.5 font-bold text-[#00F5FF]">VEH-3351</td>
                    <td className="p-3.5">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[9px] font-bold bg-[#39FF14]/15 text-[#39FF14] border border-[#39FF14]/10">
                        NOMINAL
                      </span>
                    </td>
                    <td className="p-3.5 text-white font-bold">Jane Smith</td>
                    <td className="p-3.5 text-gray-500">Transponder signal routing nominal. No faults.</td>
                    <td className="p-3.5 text-right text-gray-500">—</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Operational Task List Checklist Card */}
          <div className="bg-[#11141B] rounded-xl border border-[rgba(255,255,255,0.04)] p-4 shadow-lg">
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-3.5 flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-[#D88A1D]" />
              COMMAND CENTER PENDING CHECKLIST
            </h4>
            <div className="space-y-2">
              {tasks.map(task => (
                <label 
                  key={task.id} 
                  className={`flex items-start gap-3 p-2.5 rounded-lg border border-[rgba(255,255,255,0.02)] cursor-pointer select-none transition ${
                    task.checked ? 'bg-[#08090C]/30 text-gray-600 line-through' : 'bg-[#08090C]/60 hover:bg-white/[0.01] text-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={task.checked}
                    onChange={() => toggleTask(task.id)}
                    className="mt-0.5 rounded bg-[#11141B] border-[rgba(255,255,255,0.1)] text-[#D88A1D] focus:ring-[#D88A1D] accent-[#D88A1D]"
                  />
                  <span className="text-xs font-mono">{task.text}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right Section: Radar Sweep & Charts */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Circular vector sweeps / Health Radar */}
          <div className="bg-[#11141B] rounded-xl border border-[rgba(0,245,255,0.08)] p-5 shadow-2xl radar-sweep">
            <h4 className="text-white font-bold text-xs uppercase tracking-wider mb-1 flex items-center gap-2">
              <Radar className="w-4 h-4 text-[#00F5FF]" />
              SYSTEM HEALTH COMPLIANCE RADAR
            </h4>
            <p className="text-[9px] text-gray-500 mb-6 font-mono">Telemetry diagnostics sweep active</p>

            <div className="h-44 w-full flex items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={fleetDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={70}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {fleetDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              
              <div className="absolute text-center">
                <span className="text-2xl font-black text-white font-mono leading-none">94.3%</span>
                <span className="block text-[8px] text-[#39FF14] uppercase tracking-wider font-bold mt-1 font-mono">NOMINAL</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 border-t border-[rgba(255,255,255,0.04)] pt-4 mt-2">
              {fleetDistributionData.map((item, idx) => (
                <div key={idx} className="text-center font-mono">
                  <div className="flex items-center justify-center gap-1.5 mb-0.5">
                    <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="text-gray-500 text-[8px] font-bold uppercase">{item.name}</span>
                  </div>
                  <span className="text-xs font-bold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Environmental parameters and delay warnings */}
          <div className="bg-[#11141B] rounded-xl border border-[rgba(255,255,255,0.04)] p-4 shadow-lg space-y-3">
            <h4 className="text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2">
              <CloudLightning className="w-4 h-4 text-yellow-400" />
              ROUTE BOTTLENECK WARNINGS
            </h4>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="p-3 bg-[#FF3131]/10 border border-[#FF3131]/15 text-[#FF3131] rounded-lg">
                <span className="font-bold block">GRID-NODE: HOUSTON SECTOR</span>
                <p className="text-gray-400 mt-1 leading-relaxed">Severe electrical storm alerts. Telemetry indicates route latency variance increases.</p>
              </div>
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/15 text-yellow-400 rounded-lg">
                <span className="font-bold block">GRID-NODE: PHOENIX TRANSIT HUB</span>
                <p className="text-gray-400 mt-1 leading-relaxed">Congested heavy transit volumes logged. Alternative bypassing loaded in dispatcher.</p>
              </div>
            </div>
          </div>

          {/* Bar Chart volumes */}
          <div className="bg-[#11141B] rounded-xl border border-[rgba(255,255,255,0.04)] p-4 shadow-lg">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h4 className="text-white font-bold text-xs uppercase tracking-wider">Weekly Dispatch Vectors</h4>
                <p className="text-[9px] text-gray-500 font-mono">Transit volumes comparative analysis</p>
              </div>
            </div>

            <div className="h-32 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                  <XAxis dataKey="name" stroke="#4b5563" fontSize={8} tickLine={false} axisLine={false} />
                  <YAxis stroke="#4b5563" fontSize={8} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#08090C', border: '1px solid rgba(0,245,255,0.1)', borderRadius: '8px' }} 
                    labelStyle={{ color: '#fff', fontSize: 9, fontWeight: 'bold' }}
                    itemStyle={{ fontSize: 9 }}
                  />
                  <Bar dataKey="trips" fill="#00F5FF" radius={[2, 2, 0, 0]} name="Completed" />
                  <Bar dataKey="delay" fill="#FF3131" radius={[2, 2, 0, 0]} name="Delayed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
        </div>
      </div>
    </motion.div>
  );
};
