import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useStore } from '../context/useStore';
import { toast } from 'sonner';
import { 
  Bell, 
  Search, 
  Mic, 
  Menu, 
  Sparkles, 
  AlertTriangle,
  X,
  Database,
  Activity,
  RefreshCw,
  Settings as SettingsIcon,
  ChevronRight,
  Globe
} from 'lucide-react';

interface HeaderProps {
  onSearchClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onSearchClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useStore((state) => state.currentUser);
  const alerts = useStore((state) => state.alerts);
  const resolveAlert = useStore((state) => state.resolveAlert);
  
  const [showAlertsDropdown, setShowAlertsDropdown] = useState(false);
  const [showWorkspaceDropdown, setShowWorkspaceDropdown] = useState(false);
  const [isListening, setIsListening] = useState(false);
  
  // Real-time states
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [apiLatency, setApiLatency] = useState(24);
  const [isSyncing, setIsSyncing] = useState(false);

  // Tick the clock every second
  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Simulate API latency changes slightly for telemetry feel
  useEffect(() => {
    const interval = setInterval(() => {
      setApiLatency(prev => {
        const delta = Math.floor(Math.random() * 5) - 2;
        return Math.min(45, Math.max(12, prev + delta));
      });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const triggerSync = () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
      toast.success('Fleet database synchronized with MongoDB Atlas.');
    }, 800);
  };

  // Get breadcrumb hierarchy
  const getBreadcrumbs = () => {
    const base = 'TransOps Console';
    switch (location.pathname) {
      case '/dashboard': return [base, 'Dashboard'];
      case '/fleet': return [base, 'Fleet Assets', 'Registry'];
      case '/drivers': return [base, 'Personnel', 'Drivers'];
      case '/dispatcher': return [base, 'Operations', 'Dispatcher'];
      case '/maintenance': return [base, 'Prevention', 'Maintenance'];
      case '/fuel-expense': return [base, 'Accounting', 'Expenses'];
      case '/analytics': return [base, 'Intelligence', 'Analytics'];
      case '/settings': return [base, 'System Settings', 'RBAC Configuration'];
      default: return [base];
    }
  };

  // Voice Command Web Speech hook
  const startVoiceCommand = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast.error('Speech recognition not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      toast.info('Listening: speak "go to fleet", "dispatch", "analytics", etc.', {
        id: 'voice-active',
        duration: 4000
      });
    };

    recognition.onerror = () => {
      setIsListening(false);
      toast.dismiss('voice-active');
      toast.error('Voice command failed: No audio captured.');
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event: any) => {
      const command = event.results[0][0].transcript.toLowerCase();
      toast.dismiss('voice-active');
      toast.success(`Speech captured: "${command}"`);

      if (command.includes('dashboard') || command.includes('home')) {
        navigate('/dashboard');
      } else if (command.includes('vehicle') || command.includes('fleet') || command.includes('registry')) {
        navigate('/fleet');
      } else if (command.includes('driver')) {
        navigate('/drivers');
      } else if (command.includes('dispatch')) {
        navigate('/dispatcher');
      } else if (command.includes('maintenance')) {
        navigate('/maintenance');
      } else if (command.includes('expense') || command.includes('fuel')) {
        navigate('/fuel-expense');
      } else if (command.includes('analytics') || command.includes('report')) {
        navigate('/analytics');
      } else if (command.includes('settings')) {
        navigate('/settings');
      } else if (command.includes('logout') || command.includes('sign out')) {
        useStore.getState().setCurrentUser(null);
        navigate('/');
      } else {
        toast.error(`Unknown request: "${command}"`);
      }
    };

    recognition.start();
  };

  if (!currentUser) return null;

  return (
    <header className="h-16 border-b border-[rgba(255,255,255,0.06)] bg-[#0F1117] flex items-center justify-between px-6 z-40 relative">
      
      {/* Left Area: Breadcrumbs & Workspace Switcher */}
      <div className="flex items-center gap-4">
        {/* Toggle sidebar button for mobile */}
        <button className="md:hidden text-gray-400 hover:text-white p-1 hover:bg-white/5 rounded transition">
          <Menu className="w-5 h-5" />
        </button>

        {/* Workspace Switcher */}
        <div className="relative">
          <button 
            onClick={() => setShowWorkspaceDropdown(!showWorkspaceDropdown)}
            className="flex items-center gap-1.5 bg-white/[0.02] border border-[rgba(255,255,255,0.06)] hover:border-white/10 px-2.5 py-1 rounded-lg text-xs text-white font-semibold transition"
          >
            <Globe className="w-3.5 h-3.5 text-[#D88A1D]" />
            <span>North American Fleet</span>
            <ChevronRight className="w-3 h-3 rotate-90 text-gray-500" />
          </button>
          
          {showWorkspaceDropdown && (
            <div className="absolute left-0 mt-2 w-48 glass rounded-xl border border-[rgba(255,255,255,0.08)] shadow-2xl p-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
              <span className="block text-[9px] font-bold text-gray-500 uppercase tracking-wider px-2 py-1">Available Workspaces</span>
              <button 
                onClick={() => setShowWorkspaceDropdown(false)}
                className="w-full text-left text-xs text-white bg-white/5 px-2.5 py-1.5 rounded-lg font-medium block"
              >
                🇺🇸 North American Fleet
              </button>
              <button 
                onClick={() => {
                  setShowWorkspaceDropdown(false);
                  toast.message('Simulating change to European Hub...');
                }}
                className="w-full text-left text-xs text-gray-400 hover:text-white hover:bg-white/5 px-2.5 py-1.5 rounded-lg block mt-1 transition"
              >
                🇪🇺 European Transit Hub
              </button>
            </div>
          )}
        </div>

        {/* Breadcrumb Navigation */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-gray-500 font-medium">
          <span className="text-gray-600">/</span>
          {getBreadcrumbs().map((crumb, idx, arr) => (
            <React.Fragment key={idx}>
              <span className={idx === arr.length - 1 ? 'text-gray-300 font-semibold' : 'text-gray-500'}>
                {crumb}
              </span>
              {idx < arr.length - 1 && <ChevronRight className="w-3 h-3 text-gray-700" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Right Area: Status tickers, time, search, controls */}
      <div className="flex items-center gap-4">
        
        {/* Live Status Indicators (Telemetry & DB) */}
        <div className="hidden xl:flex items-center gap-3.5 text-[10px] border-r border-[rgba(255,255,255,0.06)] pr-4">
          {/* Latency */}
          <div className="flex items-center gap-1.5 text-gray-400 font-medium">
            <Activity className="w-3.5 h-3.5 text-[#4EA8DE]" />
            <span>API Latency:</span>
            <span className="text-white font-bold font-mono">{apiLatency}ms</span>
          </div>

          {/* Database */}
          <div className="flex items-center gap-1.5 text-gray-400 font-medium">
            <Database className="w-3.5 h-3.5 text-[#4ADE80]" />
            <span>Atlas MongoDB:</span>
            <span className="text-[#4ADE80] font-bold">Online</span>
          </div>

          {/* Clock */}
          <div className="flex items-center gap-1.5 text-gray-400 font-medium font-mono">
            <span className="h-1.5 w-1.5 rounded-full bg-[#4ADE80]"></span>
            <span>{time}</span>
          </div>

          {/* Database Sync */}
          <button 
            onClick={triggerSync}
            className={`text-gray-500 hover:text-white p-1 hover:bg-white/5 rounded transition-all ${
              isSyncing ? 'animate-spin text-[#D88A1D]' : ''
            }`}
            title="Force Synchronize Ledger"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Global Command Menu Search Bar */}
        <button 
          onClick={onSearchClick}
          className="flex items-center gap-2 bg-[#111318] border border-[rgba(255,255,255,0.06)] hover:border-white/10 px-3 py-1.5 rounded-lg text-xs text-gray-500 w-44 md:w-56 text-left transition apple-transition shadow-inner"
        >
          <Search className="w-3.5 h-3.5 text-gray-500" />
          <span className="flex-1 text-[11px] truncate">Search commands...</span>
          <kbd className="text-[9px] text-gray-500 bg-gray-900 border border-[rgba(255,255,255,0.06)] px-1.5 py-0.5 rounded font-mono">
            Ctrl+K
          </kbd>
        </button>

        {/* Voice Command Microphone Button */}
        <button
          onClick={isListening ? () => {} : startVoiceCommand}
          className={`p-2 rounded-lg border text-xs font-semibold relative transition apple-transition ${
            isListening 
              ? 'bg-red-500/20 text-red-400 border-red-500/30' 
              : 'bg-[#111318] border-[rgba(255,255,255,0.06)] text-gray-400 hover:text-white hover:border-white/10 shadow-sm'
          }`}
          title="Voice Control Navigation"
        >
          {isListening ? (
            <span className="flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-red-400 animate-ping"></span>
              <Mic className="w-3.5 h-3.5 text-red-400" />
            </span>
          ) : (
            <Mic className="w-3.5 h-3.5" />
          )}
        </button>

        {/* Notification Hub */}
        <div className="relative">
          <button 
            onClick={() => setShowAlertsDropdown(!showAlertsDropdown)}
            className={`p-2 bg-[#111318] border border-[rgba(255,255,255,0.06)] rounded-lg hover:border-white/10 text-gray-400 hover:text-white relative transition apple-transition ${
              showAlertsDropdown ? 'border-[#D88A1D] bg-white/[0.02]' : ''
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            {alerts.length > 0 && (
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-[#EF4444] text-[9px] font-bold text-white rounded-full flex items-center justify-center border-2 border-[#0F1117] animate-pulse">
                {alerts.length}
              </span>
            )}
          </button>

          {showAlertsDropdown && (
            <div className="absolute right-0 mt-2.5 w-80 glass rounded-xl border border-[rgba(255,255,255,0.08)] shadow-2xl p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="flex justify-between items-center border-b border-[rgba(255,255,255,0.06)] pb-2 mb-3">
                <span className="text-white text-xs font-bold font-sans">Active Critical Alerts</span>
                <button 
                  onClick={() => setShowAlertsDropdown(false)}
                  className="text-gray-500 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-4 max-h-72 overflow-y-auto pr-1">
                {alerts.length === 0 ? (
                  <div className="py-4 text-center text-xs text-gray-500 flex flex-col items-center gap-2">
                    <Sparkles className="w-4 h-4 text-gray-600" />
                    No active mechanical reports
                  </div>
                ) : (
                  <>
                    {/* Today Section */}
                    <div>
                      <span className="block text-[9px] font-bold text-[#D88A1D] uppercase tracking-wider mb-2">Today</span>
                      <div className="space-y-2.5">
                        {alerts.map((alert) => (
                          <div 
                            key={alert.id} 
                            className={`p-2.5 rounded-lg border flex gap-2.5 text-xs transition relative ${
                              alert.status === 'Critical' 
                                ? 'bg-red-500/10 border-red-500/15 text-red-300' 
                                : 'bg-yellow-500/10 border-yellow-500/15 text-yellow-300'
                            }`}
                          >
                            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                            <div className="flex-1 truncate">
                              <div className="flex justify-between items-center mb-0.5">
                                <span className="font-bold">{alert.vehicleId}</span>
                                <span className="text-[9px] text-gray-500">{alert.time}</span>
                              </div>
                              <p className="text-gray-400 leading-tight text-[11px] truncate">{alert.description}</p>
                            </div>
                            <button 
                              onClick={() => {
                                resolveAlert(alert.id);
                                toast.success(`Acknowledged alert: ${alert.id}`);
                              }}
                              className="text-gray-500 hover:text-white p-0.5 rounded transition absolute right-1.5 top-1.5"
                            >
                              <X className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Yesterday Section */}
                    <div>
                      <span className="block text-[9px] font-bold text-gray-500 uppercase tracking-wider mb-2">Yesterday</span>
                      <div className="p-2.5 rounded-lg border border-[rgba(255,255,255,0.06)] bg-white/[0.01] flex gap-2.5 text-xs relative text-gray-400">
                        <AlertTriangle className="w-4.5 h-4.5 text-gray-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 truncate">
                          <div className="flex justify-between items-center mb-0.5">
                            <span className="font-bold text-white">VEH-2204</span>
                            <span className="text-[9px] text-gray-500">Yesterday</span>
                          </div>
                          <p className="leading-tight text-[11px] truncate text-gray-400">Tire Pressure Deviation Warning</p>
                        </div>
                        <span className="text-[9px] text-[#4ADE80] font-bold absolute right-1.5 top-1.5">Auto-Resolved</span>
                      </div>
                    </div>

                    {/* Earlier Section */}
                    <div>
                      <span className="block text-[9px] font-bold text-gray-500 uppercase tracking-wider mb-2">Earlier</span>
                      <div className="p-2.5 rounded-lg border border-[rgba(255,255,255,0.06)] bg-white/[0.01] flex gap-2.5 text-xs relative text-gray-400">
                        <AlertTriangle className="w-4.5 h-4.5 text-gray-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 truncate">
                          <div className="flex justify-between items-center mb-0.5">
                            <span className="font-bold text-white">VEH-3351</span>
                            <span className="text-[9px] text-gray-500">3 days ago</span>
                          </div>
                          <p className="leading-tight text-[11px] truncate text-gray-400">Scheduled Odometer Service Flag</p>
                        </div>
                        <span className="text-[9px] text-[#4ADE80] font-bold absolute right-1.5 top-1.5 font-mono">Logged</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Settings Direct Shortcut */}
        <button 
          onClick={() => navigate('/settings')}
          className="p-2 bg-[#111318] border border-[rgba(255,255,255,0.06)] rounded-lg hover:border-white/10 text-gray-400 hover:text-white transition apple-transition"
          title="Open System Controls"
        >
          <SettingsIcon className="w-3.5 h-3.5" />
        </button>

        {/* User profile dropdown info */}
        <div className="flex items-center gap-2 border-l border-[rgba(255,255,255,0.06)] pl-4">
          <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-gray-800 to-gray-700 border border-[rgba(255,255,255,0.08)] flex items-center justify-center text-white text-[10px] font-bold shadow-inner">
            {currentUser.email.slice(0, 2).toUpperCase()}
          </div>
          <div className="hidden lg:block text-left">
            <span className="block text-white text-[11px] font-bold leading-none mb-0.5">
              {currentUser.email.split('@')[0]}
            </span>
            <span className="text-[9px] text-[#D88A1D] font-mono leading-none block">
              {currentUser.role}
            </span>
          </div>
        </div>

      </div>
    </header>
  );
};
