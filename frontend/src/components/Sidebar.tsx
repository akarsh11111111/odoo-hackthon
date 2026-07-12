import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useStore } from '../context/useStore';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Truck, 
  Users, 
  Send, 
  Wrench, 
  Fuel, 
  BarChart3, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  LogOut,
  ShieldCheck,
  Pin,
  MapPin
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const currentUser = useStore((state) => state.currentUser);
  const setCurrentUser = useStore((state) => state.setCurrentUser);
  const alerts = useStore((state) => state.alerts);
  const trips = useStore((state) => state.trips);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, badge: 0 },
    { name: 'Vehicle Registry', path: '/fleet', icon: Truck, badge: 0 },
    { name: 'Drivers', path: '/drivers', icon: Users, badge: 0 },
    { name: 'Trip Dispatcher', path: '/dispatcher', icon: Send, badge: trips.filter(t => t.status === 'In-Transit').length },
    { name: 'Maintenance', path: '/maintenance', icon: Wrench, badge: alerts.length },
    { name: 'Fuel & Expense', path: '/fuel-expense', icon: Fuel, badge: 0 },
    { name: 'Reports & Analytics', path: '/analytics', icon: BarChart3, badge: 0 },
    { name: 'Settings', path: '/settings', icon: Settings, badge: 0 },
  ];

  const handleLogout = () => {
    setCurrentUser(null);
    navigate('/');
  };

  if (!currentUser) return null;

  return (
    <motion.div 
      layout
      className={`relative h-screen bg-[#111318] border-r border-[rgba(255,255,255,0.06)] flex flex-col justify-between z-40 transition-all duration-300 ${
        isCollapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      <div>
        {/* Workspace Branding */}
        <div className={`h-16 flex items-center border-b border-[rgba(255,255,255,0.06)] px-4 ${
          isCollapsed ? 'justify-center' : 'justify-between'
        }`}>
          {!isCollapsed ? (
            <div className="flex items-center gap-2.5">
              <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-[#D88A1D] to-[#F59E0B] flex items-center justify-center shadow-lg shadow-[#D88A1D]/15">
                <span className="text-black font-extrabold text-sm">T</span>
              </div>
              <div className="text-left">
                <span className="font-extrabold text-white text-sm tracking-tight leading-none block">TransOps Global</span>
                <span className="text-[9px] text-gray-500 font-semibold uppercase tracking-wider block mt-0.5">Enterprise Fleet</span>
              </div>
            </div>
          ) : (
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#D88A1D] to-[#F59E0B] flex items-center justify-center shadow-md">
              <span className="text-black font-extrabold text-sm">T</span>
            </div>
          )}

          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-gray-500 hover:text-white p-1 hover:bg-white/5 rounded hidden md:block transition apple-transition"
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Pinned shortcuts header (if expanded) */}
        {!isCollapsed && (
          <div className="px-4 pt-4 pb-2">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
              <Pin className="w-3 h-3 text-[#D88A1D]" />
              Pinned Operations
            </span>
            <button 
              onClick={() => navigate('/dispatcher')}
              className="w-full text-left p-1.5 rounded-md hover:bg-white/5 text-[11px] text-gray-400 hover:text-white flex items-center gap-2 transition"
            >
              <MapPin className="w-3.5 h-3.5 text-[#4EA8DE]" />
              <span>Live Telemetry Grid</span>
              <span className="h-1.5 w-1.5 rounded-full bg-[#4ADE80] ml-auto animate-ping"></span>
            </button>
          </div>
        )}

        {/* Menu Items */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs transition-all group relative ${
                  isActive 
                    ? 'bg-gradient-to-r from-white/5 to-white/[0.01] text-[#D88A1D] font-bold border-l-2 border-[#D88A1D]' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className={`w-4.5 h-4.5 flex-shrink-0 ${isActive ? 'text-[#D88A1D]' : 'text-gray-500 group-hover:text-white transition'}`} />
                {!isCollapsed && <span className="font-medium">{item.name}</span>}
                
                {/* Active Indicator Slide Highlight */}
                {isActive && !isCollapsed && (
                  <motion.span 
                    layoutId="activeNavigation"
                    className="absolute inset-0 bg-white/[0.02] rounded-lg -z-10"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}

                {/* Badge Count */}
                {item.badge > 0 && !isCollapsed && (
                  <span className="h-4.5 min-w-[18px] px-1 rounded-full bg-[#EF4444]/20 border border-[#EF4444]/35 text-[9px] font-bold text-[#EF4444] flex items-center justify-center ml-auto">
                    {item.badge}
                  </span>
                )}

                {isCollapsed && (
                  <div className="absolute left-16 z-50 rounded bg-gray-900 border border-[rgba(255,255,255,0.06)] px-2.5 py-1 text-xs text-white opacity-0 pointer-events-none group-hover:opacity-100 transition whitespace-nowrap">
                    {item.name} {item.badge > 0 ? `(${item.badge})` : ''}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Session Info */}
      <div className="border-t border-[rgba(255,255,255,0.06)] p-3">
        {!isCollapsed ? (
          <div className="bg-white/[0.01] border border-[rgba(255,255,255,0.04)] rounded-xl p-3 shadow-inner">
            <div className="flex items-center gap-2 mb-2.5">
              <div className="h-7 w-7 rounded-full bg-gray-800 border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-white text-[10px] font-bold">
                {currentUser.email.slice(0, 2).toUpperCase()}
              </div>
              <div className="truncate flex-1 text-left">
                <span className="block text-white text-[11px] font-bold truncate leading-none mb-1">{currentUser.email}</span>
                <span className="inline-flex items-center gap-1 text-[9px] text-[#4EA8DE] bg-[#4EA8DE]/10 px-1.5 py-0.5 rounded font-medium">
                  <ShieldCheck className="w-2.5 h-2.5" />
                  {currentUser.role}
                </span>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 py-1.5 rounded-lg text-[10px] font-bold border border-red-500/15 transition-all"
            >
              <LogOut className="w-3 h-3" />
              Sign Out Hub
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="h-7 w-7 rounded-full bg-gray-800 border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-white text-[10px] font-bold">
              {currentUser.email.slice(0, 2).toUpperCase()}
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition"
              title="Sign Out Hub"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};
