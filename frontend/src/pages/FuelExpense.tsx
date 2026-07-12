import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { motion } from 'framer-motion';
import { Fuel, Plus, DollarSign, X, TrendingUp, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  CartesianGrid
} from 'recharts';

export const FuelExpense: React.FC = () => {
  const { vehicles, expenses, addExpense } = useStore();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form states
  const [selectedVehicle, setSelectedVehicle] = useState(vehicles[0]?.id || '');
  const [liters, setLiters] = useState(400);
  const [cost, setCost] = useState(560.00);
  const [odometer, setOdometer] = useState(120400);
  const [location, setLocation] = useState("Pilot Travel Center, TX");
  const [expenseType, setExpenseType] = useState<'Fuel' | 'Repair' | 'Toll' | 'Other'>('Fuel');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedVehicle || !cost || !location) {
      toast.error('All purchase fields must be specified.');
      return;
    }

    addExpense({
      date,
      vehicleId: selectedVehicle,
      liters: expenseType === 'Fuel' ? liters : 0,
      cost,
      odometer,
      location,
      type: expenseType
    });

    toast.success(`Successfully logged ${expenseType} cost of $${cost}`);
    setIsModalOpen(false);

    // reset
    setCost(150.00);
  };

  // Calculations for summary tiles
  const fuelExpenses = expenses.filter(e => e.type === 'Fuel');
  const totalFuelCost = fuelExpenses.reduce((acc, curr) => acc + curr.cost, 0);
  const totalLiters = fuelExpenses.reduce((acc, curr) => acc + curr.liters, 0);
  const avgFuelPrice = totalLiters > 0 ? (totalFuelCost / totalLiters) : 0;
  
  const repairsExpenses = expenses.filter(e => e.type === 'Repair');
  const totalRepairsCost = repairsExpenses.reduce((acc, curr) => acc + curr.cost, 0);
  
  const tollExpenses = expenses.filter(e => e.type === 'Toll');
  const totalTollsCost = tollExpenses.reduce((acc, curr) => acc + curr.cost, 0);

  // Recharts Expense Category Pie data
  const expenseBreakdownData = [
    { name: 'Fuel Refuels', value: totalFuelCost, color: '#4EA8DE' },
    { name: 'Preventive Repair', value: totalRepairsCost, color: '#F59E0B' },
    { name: 'Road Tolls / Other', value: totalTollsCost + 240, color: '#EF4444' }
  ];

  // Budget vs Actual data
  const budgetVsActualData = [
    { month: 'Jan', Budget: 3500, Actual: 3200 },
    { month: 'Feb', Budget: 3500, Actual: 3890 }, // Over budget
    { month: 'Mar', Budget: 4000, Actual: 3670 },
    { month: 'Apr', Budget: 4000, Actual: 4120 }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative"
    >
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Total Fuel Cost</span>
            <span className="text-2xl font-black text-white font-sans mt-1 block">${totalFuelCost.toLocaleString()} USD</span>
            <span className="text-[10px] text-gray-400 block mt-1">Logged over {totalLiters.toLocaleString()} Liters</span>
          </div>
          <div className="h-10 w-10 bg-white/5 rounded-lg flex items-center justify-center text-gray-400">
            <Fuel className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Average Fuel Cost</span>
            <span className="text-2xl font-black text-[#D88A1D] font-sans mt-1 block">${avgFuelPrice.toFixed(2)}/L</span>
            <span className="text-[10px] text-[#4EA8DE] block mt-1 font-semibold">National commercial avg: $1.45</span>
          </div>
          <div className="h-10 w-10 bg-[#D88A1D]/10 rounded-lg flex items-center justify-center text-[#D88A1D]">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-4 flex items-center justify-between shadow-md">
          <div>
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">Repairs & Workshop Bills</span>
            <span className="text-2xl font-black text-white font-sans mt-1 block">${totalRepairsCost.toLocaleString()} USD</span>
            <span className="text-[10px] text-gray-400 block mt-1">Preventive workshop bills</span>
          </div>
          <div className="h-10 w-10 bg-white/5 rounded-lg flex items-center justify-center text-gray-400">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Financial Charts Overview Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Cost category breakdown Donut */}
        <div className="lg:col-span-5 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <h5 className="text-white font-bold text-xs uppercase tracking-wider mb-1">Financial Category distribution</h5>
          <p className="text-[11px] text-gray-500 mb-6">Visual cost allocation between fuel, repairs, and tolls</p>
          
          <div className="h-44 w-full flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenseBreakdownData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {expenseBreakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute text-center">
              <span className="text-xs text-gray-500 uppercase block font-bold">Total Dispersed</span>
              <span className="text-base font-black text-white font-mono leading-none mt-0.5">${(totalFuelCost + totalRepairsCost + totalTollsCost).toLocaleString()}</span>
            </div>
          </div>

          <div className="space-y-1.5 mt-2 border-t border-[rgba(255,255,255,0.04)] pt-3 text-[11px] font-mono">
            {expenseBreakdownData.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-gray-400">
                <div className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span>{item.name}</span>
                </div>
                <span className="text-white font-bold">${item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Budget vs Actual operations */}
        <div className="lg:col-span-7 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg">
          <div className="flex justify-between items-center mb-1">
            <div>
              <h5 className="text-white font-bold text-xs uppercase tracking-wider">Logistics Budget vs Actual Costs</h5>
              <p className="text-[11px] text-gray-500">Track monthly expenditures against scheduled spending boundaries</p>
            </div>
            {/* Warning alert if over budget in recent month */}
            <div className="bg-yellow-500/10 border border-yellow-500/15 text-yellow-400 px-2 py-1 rounded text-[9px] font-bold flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              <span>Feb budget exceeded</span>
            </div>
          </div>

          <div className="h-56 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={budgetVsActualData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.02)" />
                <XAxis dataKey="month" stroke="#52525b" fontSize={9} tickLine={false} />
                <YAxis stroke="#52525b" fontSize={9} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontSize: 10, fontWeight: 'bold' }}
                  itemStyle={{ fontSize: 10 }}
                />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 9 }} />
                <Bar dataKey="Budget" fill="#4EA8DE" radius={[2, 2, 0, 0]} />
                <Bar dataKey="Actual" fill="#D88A1D" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* List Action Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#161A22] p-4 rounded-xl border border-[rgba(255,255,255,0.06)] shadow-md">
        <div>
          <h4 className="text-white font-bold text-sm">Financial Log & Expense registries</h4>
          <p className="text-xs text-gray-500 mt-0.5">Surveillance billing records of fleet operations</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button 
            onClick={() => {
              toast.message('Exporting financial logs...');
              setTimeout(() => toast.success('Fuel invoices exported as CSV.'), 800);
            }}
            className="bg-white/5 border border-[rgba(255,255,255,0.06)] hover:border-white/10 text-white font-bold text-[10px] px-2.5 py-2 rounded-lg transition cursor-pointer"
          >
            Export CSV
          </button>
          <button 
            onClick={() => {
              toast.message('Exporting spreadsheets...');
              setTimeout(() => toast.success('Fuel invoices exported as Excel XLSX.'), 800);
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
            Log Expense Log
          </button>
        </div>
      </div>

      {/* Fuel Expenses Table */}
      <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                <th className="p-3.5">Log Date</th>
                <th className="p-3.5">Vehicle ID</th>
                <th className="p-3.5">Charge Type</th>
                <th className="p-3.5">Fuel Volume (L)</th>
                <th className="p-3.5">Charge Cost</th>
                <th className="p-3.5">Odometer (mi)</th>
                <th className="p-3.5">Purchase Location Node</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300">
              {expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-white/[0.01] transition apple-transition">
                  <td className="p-3.5 font-medium text-white">{expense.date}</td>
                  <td className="p-3.5 font-mono font-bold text-[#4EA8DE]">{expense.vehicleId}</td>
                  <td className="p-3.5">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                      expense.type === 'Fuel' 
                        ? 'bg-[#4EA8DE]/10 text-[#4EA8DE] border border-[#4EA8DE]/15' 
                        : expense.type === 'Repair' 
                        ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/15' 
                        : 'bg-gray-800 text-gray-400'
                    }`}>
                      {expense.type}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-white">
                    {expense.type === 'Fuel' ? `${expense.liters.toLocaleString()} L` : '—'}
                  </td>
                  <td className="p-3.5 font-mono font-bold text-[#4ADE80]">${expense.cost.toFixed(2)}</td>
                  <td className="p-3.5 font-mono text-gray-400">{expense.odometer.toLocaleString()} mi</td>
                  <td className="p-3.5 text-gray-400">{expense.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Log Expense Dialog Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.08)] shadow-2xl p-6 text-gray-300 relative animate-in zoom-in-95 duration-200">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute right-4 top-4 text-gray-500 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h4 className="text-white font-extrabold text-base tracking-tight mb-1">Log Purchase / Expense Record</h4>
            <p className="text-xs text-gray-500 mb-6">Store refuel, tolls or mechanical repair receipts.</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Purchase Date</label>
                  <input
                    type="date"
                    required
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Expense Type</label>
                  <select
                    value={expenseType}
                    onChange={(e) => setExpenseType(e.target.value as any)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  >
                    <option value="Fuel">Fuel Refuel</option>
                    <option value="Repair">Preventive Repair</option>
                    <option value="Toll">Road Tolls</option>
                    <option value="Other">Other Expenses</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Fleet Asset</label>
                <select
                  value={selectedVehicle}
                  onChange={(e) => setSelectedVehicle(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                >
                  {vehicles.map(v => (
                    <option key={v.id} value={v.id}>{v.id} — {v.model}</option>
                  ))}
                </select>
              </div>

              {expenseType === 'Fuel' && (
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Fuel Volume (Liters)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={liters}
                    onChange={(e) => setLiters(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Total Cost ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={cost}
                    onChange={(e) => setCost(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Odometer (mi)</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={odometer}
                    onChange={(e) => setOdometer(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Vendor Location Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Pilot Travel Stop #224, Dallas TX"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all mt-4"
              >
                Log Cost Log
              </button>
            </form>
          </div>
        </div>
      )}

    </motion.div>
  );
};
