import React, { useState } from 'react';
import { SpotlightCard } from '../components/SpotlightCard';
import { motion } from 'framer-motion';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  Cell,
  PieChart,
  Pie,
  Line
} from 'recharts';
import { Download, Calendar, Filter } from 'lucide-react';
import { toast } from 'sonner';

export const Analytics: React.FC = () => {
  const [dateRange, setDateRange] = useState('Last 30 Days');
  const [drillDownGroup, setDrillDownGroup] = useState('All Regions');

  // Mock data for graphs
  const fuelEfficiencyTrend = [
    { month: 'Jan', efficiency: 7.2, target: 7.5 },
    { month: 'Feb', efficiency: 7.5, target: 7.5 },
    { month: 'Mar', efficiency: 7.8, target: 7.5 },
    { month: 'Apr', efficiency: 7.6, target: 7.5 },
    { month: 'May', efficiency: 8.1, target: 7.5 },
    { month: 'Jun', efficiency: 7.9, target: 7.5 }
  ];

  const maintenanceCosts = [
    { type: 'Engine Tuning', cost: 1420 },
    { type: 'Brake Servicing', cost: 2350 },
    { type: 'Tire Flips', cost: 890 },
    { type: 'Body & Chassis', cost: 1100 }
  ];

  const safetyScoreByClass = [
    { range: '95-100%', drivers: 8, color: '#4ADE80' },
    { range: '90-95%', drivers: 14, color: '#4EA8DE' },
    { range: '80-90%', drivers: 5, color: '#F59E0B' },
    { range: '<80%', drivers: 2, color: '#EF4444' }
  ];

  const completedTripsRatio = [
    { name: 'Completed', value: 142 },
    { name: 'Delayed', value: 8 }
  ];

  const COLORS = ['#4ADE80', '#EF4444'];

  const triggerExport = (format: 'PDF' | 'CSV') => {
    toast.message(`Assembling analytical dataset: Exporting report as ${format}...`);
    setTimeout(() => {
      toast.success(`Report exported successfully as TransOps_Analytics_${Date.now()}.${format.toLowerCase()}`);
    }, 1000);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative"
    >
      
      {/* Top Header Filter & Export Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#161A22] p-4 rounded-xl border border-[rgba(255,255,255,0.06)] shadow-md">
        <div className="flex flex-wrap items-center gap-3">
          {/* Date range picker */}
          <div className="flex items-center gap-2 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] px-3 py-2 rounded-lg text-xs">
            <Calendar className="w-3.5 h-3.5 text-gray-500" />
            <select 
              value={dateRange}
              onChange={(e) => {
                setDateRange(e.target.value);
                toast.message(`Date range filter: ${e.target.value}`);
              }}
              className="bg-transparent text-white border-none focus:outline-none cursor-pointer font-medium"
            >
              <option value="Today" className="bg-[#111318]">Today</option>
              <option value="Last 7 Days" className="bg-[#111318]">Last 7 Days</option>
              <option value="Last 30 Days" className="bg-[#111318]">Last 30 Days</option>
              <option value="This Quarter" className="bg-[#111318]">This Quarter</option>
            </select>
          </div>

          {/* Drilldown region filter */}
          <div className="flex items-center gap-2 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] px-3 py-2 rounded-lg text-xs">
            <Filter className="w-3.5 h-3.5 text-gray-500" />
            <select 
              value={drillDownGroup}
              onChange={(e) => {
                setDrillDownGroup(e.target.value);
                toast.message(`Filtered by region: ${e.target.value}`);
              }}
              className="bg-transparent text-white border-none focus:outline-none cursor-pointer font-medium"
            >
              <option value="All Regions" className="bg-[#111318]">All Operations Regions</option>
              <option value="US East" className="bg-[#111318]">US Eastern Hub</option>
              <option value="US West" className="bg-[#111318]">US Western Hub</option>
              <option value="US South" className="bg-[#111318]">US Southern Hub</option>
            </select>
          </div>
        </div>

        {/* Export buttons */}
        <div className="flex gap-2">
          <button 
            onClick={() => triggerExport('CSV')}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-xs px-3 py-2 rounded-lg flex items-center gap-1.5 transition"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </button>
          <button 
            onClick={() => triggerExport('PDF')}
            className="bg-[#D88A1D] hover:brightness-105 text-black font-extrabold text-xs px-3 py-2 rounded-lg flex items-center gap-1.5 transition"
          >
            <Download className="w-3.5 h-3.5 text-black" />
            Export Report PDF
          </button>
        </div>
      </div>

      {/* KPI summaries row matching Screen 7 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SpotlightCard className="p-4">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Average Fuel Efficiency</span>
          <span className="text-2xl font-black text-[#D88A1D] font-sans mt-1 block">7.8 km/l</span>
          <span className="text-[10px] text-gray-400 block mt-1">
            <span className="text-[#4ADE80] font-bold">↑ 4.2%</span> vs last quarter
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Fleet Utilization Rate</span>
          <span className="text-2xl font-black text-white font-sans mt-1 block">91%</span>
          <span className="text-[10px] text-gray-400 block mt-1">
            Target benchmark: 88%
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Total Maintenance cost</span>
          <span className="text-2xl font-black text-white font-sans mt-1 block">$2,560 USD</span>
          <span className="text-[10px] text-gray-400 block mt-1">
            Accumulated repair logs
          </span>
        </SpotlightCard>

        <SpotlightCard className="p-4">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Completed runs queue</span>
          <span className="text-2xl font-black text-[#4ADE80] font-sans mt-1 block">142 runs</span>
          <span className="text-[10px] text-gray-400 block mt-1">
            94.3% on-time delivery rate
          </span>
        </SpotlightCard>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Fuel Efficiency Area Chart */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <h5 className="text-white font-bold text-sm mb-1">Fuel Consumption Trends</h5>
          <p className="text-xs text-gray-500 mb-6">Historical fuel efficiency index against performance targets</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={fuelEfficiencyTrend} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="efficiencyGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D88A1D" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#D88A1D" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.02)" />
                <XAxis dataKey="month" stroke="#52525b" fontSize={9} tickLine={false} />
                <YAxis stroke="#52525b" fontSize={9} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }} 
                  itemStyle={{ fontSize: 10 }}
                  labelStyle={{ color: '#fff', fontSize: 10, fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="efficiency" stroke="#D88A1D" strokeWidth={2} fillOpacity={1} fill="url(#efficiencyGlow)" name="Observed km/l" />
                <Line type="monotone" dataKey="target" stroke="#4EA8DE" strokeDasharray="5 5" dot={false} name="Target Threshold" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Maintenance cost structures Bar chart */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <h5 className="text-white font-bold text-sm mb-1">Preventive Service Expenditure</h5>
          <p className="text-xs text-gray-500 mb-6">Total expenses aggregated by vehicle mechanical categories</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={maintenanceCosts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.02)" />
                <XAxis dataKey="type" stroke="#52525b" fontSize={9} tickLine={false} />
                <YAxis stroke="#52525b" fontSize={9} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}
                  itemStyle={{ fontSize: 10 }}
                  labelStyle={{ color: '#fff', fontSize: 10, fontWeight: 'bold' }}
                />
                <Bar dataKey="cost" fill="#4EA8DE" radius={[4, 4, 0, 0]} name="Expenditure ($)">
                  <Cell fill="#4EA8DE" />
                  <Cell fill="#D88A1D" />
                  <Cell fill="#4ADE80" />
                  <Cell fill="#EF4444" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Safety Distribution */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <h5 className="text-white font-bold text-sm mb-1">Driver Safety Class Distribution</h5>
          <p className="text-xs text-gray-500 mb-6">Commercial drivers safety performance ratings breakdown</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={safetyScoreByClass} layout="vertical" margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.02)" />
                <XAxis type="number" stroke="#52525b" fontSize={9} tickLine={false} />
                <YAxis dataKey="range" type="category" stroke="#52525b" fontSize={9} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}
                  itemStyle={{ fontSize: 10 }}
                  labelStyle={{ color: '#fff', fontSize: 10, fontWeight: 'bold' }}
                />
                <Bar dataKey="drivers" fill="#4ADE80" radius={[0, 4, 4, 0]} name="Drivers count">
                  {safetyScoreByClass.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Delivery Reliability pie/donut chart */}
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <h5 className="text-white font-bold text-sm mb-1">Delivery Reliability Index</h5>
          <p className="text-xs text-gray-500 mb-6">Proportion of scheduled loads successfully delivered on-schedule</p>

          <div className="h-64 w-full flex items-center justify-center relative font-sans">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={completedTripsRatio}
                  cx="50%"
                  cy="45%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {completedTripsRatio.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend layout="horizontal" verticalAlign="bottom" align="center" iconSize={8} wrapperStyle={{ fontSize: 10 }} />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="absolute top-[37%] text-center">
              <span className="text-xl font-black text-white font-mono leading-none">94.6%</span>
              <span className="block text-[8px] text-gray-500 uppercase tracking-wider font-bold mt-1">On-Time Uptime</span>
            </div>
          </div>
        </div>

      </div>

    </motion.div>
  );
};
