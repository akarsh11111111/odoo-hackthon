import React, { useEffect } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../context/useStore';
import { 
  LayoutDashboard, 
  Truck, 
  Users, 
  Send, 
  Wrench, 
  Fuel, 
  BarChart3, 
  Settings, 
  Plus, 
  Search,
  Key
} from 'lucide-react';

interface CommandPaletteProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ open, setOpen }) => {
  const navigate = useNavigate();
  const currentUser = useStore((state) => state.currentUser);
  const setCurrentUser = useStore((state) => state.setCurrentUser);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(!open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [open, setOpen]);

  const handleNavigate = (path: string) => {
    navigate(path);
    setOpen(false);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setOpen(false);
    navigate('/');
  };

  if (!open) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={() => setOpen(false)}
    >
      <div 
        className="w-full max-w-2xl overflow-hidden rounded-xl border border-[rgba(255,255,255,0.08)] bg-[#111318] shadow-2xl text-gray-300 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <Command label="Global Command Menu">
          <div className="flex items-center border-b border-[rgba(255,255,255,0.06)] px-4">
            <Search className="w-5 h-5 text-gray-500 mr-3" />
            <Command.Input
              autoFocus
              placeholder="Search sections, settings, or log transactions..."
              className="w-full h-14 bg-transparent py-4 text-sm text-white placeholder-gray-500 outline-none"
            />
            <span className="text-[10px] text-gray-600 bg-gray-900 border border-[rgba(255,255,255,0.06)] px-1.5 py-0.5 rounded font-mono">
              ESC
            </span>
          </div>

          <Command.List className="max-h-[360px] overflow-y-auto p-2 scrollbar-thin">
            <Command.Empty className="py-6 text-center text-sm text-gray-500">
              No results found for your query.
            </Command.Empty>

            <Command.Group heading="Navigation" className="px-2 py-1.5 text-[11px] font-bold text-gray-500 uppercase tracking-wider">
              <Command.Item
                onSelect={() => handleNavigate('/dashboard')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <LayoutDashboard className="w-4 h-4 text-gray-400" />
                <span>Dashboard Command Console</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/fleet')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Truck className="w-4 h-4 text-gray-400" />
                <span>Vehicle Registry List</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/drivers')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Users className="w-4 h-4 text-gray-400" />
                <span>Drivers & Safety Profiles</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/dispatcher')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Send className="w-4 h-4 text-gray-400" />
                <span>Trip Dispatcher Control</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/maintenance')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Wrench className="w-4 h-4 text-gray-400" />
                <span>Maintenance Schedules & Logs</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/fuel-expense')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Fuel className="w-4 h-4 text-gray-400" />
                <span>Fuel Logs & Expense Tracking</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/analytics')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <BarChart3 className="w-4 h-4 text-gray-400" />
                <span>Reports & Analytical Performance</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/settings')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Settings className="w-4 h-4 text-gray-400" />
                <span>RBAC & System Config Settings</span>
              </Command.Item>
            </Command.Group>

            <div className="h-px bg-white/5 my-2" />

            <Command.Group heading="Quick Actions" className="px-2 py-1.5 text-[11px] font-bold text-gray-500 uppercase tracking-wider">
              <Command.Item
                onSelect={() => handleNavigate('/fleet')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Plus className="w-4 h-4 text-gray-400" />
                <span>Register New Fleet Asset</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/dispatcher')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Plus className="w-4 h-4 text-gray-400" />
                <span>Dispatch Live Route Run</span>
              </Command.Item>
              <Command.Item
                onSelect={() => handleNavigate('/fuel-expense')}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer hover:bg-white/5 aria-selected:bg-white/5 aria-selected:text-white transition"
              >
                <Plus className="w-4 h-4 text-gray-400" />
                <span>Log Vehicle Refuel / Repair Charge</span>
              </Command.Item>
            </Command.Group>

            {currentUser && (
              <>
                <div className="h-px bg-white/5 my-2" />
                <Command.Group heading="Session" className="px-2 py-1.5 text-[11px] font-bold text-gray-500 uppercase tracking-wider">
                  <Command.Item
                    onSelect={handleLogout}
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer text-red-400 hover:bg-red-500/10 aria-selected:bg-red-500/10 transition"
                  >
                    <Key className="w-4 h-4" />
                    <span>Log Out of TransOps Portal ({currentUser.role})</span>
                  </Command.Item>
                </Command.Group>
              </>
            )}
          </Command.List>
        </Command>
      </div>
    </div>
  );
};
