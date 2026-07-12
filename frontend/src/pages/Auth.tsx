import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../context/useStore';
import { Shield, ArrowRight, UserCheck, Eye, EyeOff, Lock, User } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

export const Auth: React.FC = () => {
  const navigate = useNavigate();
  const rolesConfig = useStore((state) => state.rolesConfig);
  const setUser = useStore((state) => state.setCurrentUser);

  const [selectedRole, setSelectedRole] = useState<string>('Safety Officer');
  const [email, setEmail] = useState<string>('officer@transops.com');
  const [password, setPassword] = useState<string>('safety123');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [rememberMe, setRememberMe] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  // Password strength calculation
  const getPasswordStrength = () => {
    if (!password) return { label: 'Empty', score: 0, color: 'bg-gray-800' };
    if (password.length < 6) return { label: 'Weak', score: 33, color: 'bg-[#EF4444]' };
    if (password.length < 10) return { label: 'Medium', score: 66, color: 'bg-[#F59E0B]' };
    return { label: 'Strong CDL Vault', score: 100, color: 'bg-[#4ADE80]' };
  };

  // Pre-configured logins
  const roleLogins: Record<string, { email: string; pass: string }> = {
    Admin: { email: 'admin@transops.com', pass: 'admin123' },
    Dispatcher: { email: 'dispatcher@transops.com', pass: 'dispatch123' },
    'Safety Officer': { email: 'officer@transops.com', pass: 'safety123' },
    'Financial Analyst': { email: 'finance@transops.com', pass: 'finance123' }
  };

  const handleRoleSelect = (role: string) => {
    setSelectedRole(role);
    setEmail(roleLogins[role].email);
    setPassword(roleLogins[role].pass);
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error('Please enter both email and password.');
      return;
    }

    setIsSubmitting(true);
    
    // Simulate premium loader
    setTimeout(() => {
      setUser({ email, role: selectedRole });
      toast.success(`Welcome to Command Console: Access granted to ${selectedRole}.`);
      navigate('/dashboard');
    }, 1200);
  };

  const activeRoleData = rolesConfig[selectedRole];
  const pwStrength = getPasswordStrength();

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-[#0F1117] relative overflow-hidden"
    >
      
      {/* Background Animated Blobs */}
      <div className="absolute top-[10%] left-[20%] w-[400px] h-[400px] bg-[#D88A1D]/5 rounded-full filter blur-[100px] animate-float-blob pointer-events-none -z-10" />
      <div className="absolute bottom-[10%] right-[20%] w-[500px] h-[500px] bg-[#4EA8DE]/5 rounded-full filter blur-[120px] animate-float-blob pointer-events-none -z-10" />

      {/* Left panel - Light Theme Branding & Role Switcher */}
      <div className="lg:col-span-5 bg-[#EDF1F6] p-8 lg:p-12 flex flex-col justify-between text-gray-900 border-r border-black/10 z-10 relative">
        <div>
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-[#D88A1D] to-[#F59E0B] flex items-center justify-center shadow-lg shadow-[#D88A1D]/20">
              <span className="text-black font-black text-sm">T</span>
            </div>
            <div>
              <span className="font-extrabold text-gray-900 text-lg tracking-tight">TransOps</span>
              <p className="text-[9px] text-[#D88A1D] uppercase tracking-wider font-extrabold -mt-1.5">Logistics Control</p>
            </div>
          </div>

          <h2 className="text-xl lg:text-2xl font-extrabold text-gray-900 tracking-tight leading-tight mb-2 font-sans">
            Fleet & Transit Command Center
          </h2>
          <p className="text-gray-600 text-xs mb-8">
            Switch role profiles below to load access authorizations and live diagnostic reports.
          </p>

          {/* Interactive Role Switcher list */}
          <div className="space-y-3">
            {Object.keys(rolesConfig).map((roleName) => {
              const role = rolesConfig[roleName];
              const isSelected = selectedRole === roleName;
              return (
                <button
                  key={roleName}
                  onClick={() => handleRoleSelect(roleName)}
                  type="button"
                  className={`w-full text-left p-3.5 rounded-xl border transition-all duration-300 flex items-center justify-between ${
                    isSelected 
                      ? 'bg-white border-[#D88A1D] shadow-md shadow-[#D88A1D]/5 text-[#D88A1D]' 
                      : 'bg-white/60 hover:bg-white border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`h-7 w-7 rounded-lg flex items-center justify-center ${
                      isSelected ? 'bg-[#D88A1D]/10 text-[#D88A1D]' : 'bg-gray-100 text-gray-500'
                    }`}>
                      <UserCheck className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="font-extrabold text-xs block text-gray-900">{role.name}</span>
                      <span className="text-[10px] text-gray-500 font-semibold block truncate max-w-[200px] lg:max-w-[220px]">
                        {role.description}
                      </span>
                    </div>
                  </div>
                  {isSelected && <ArrowRight className="w-3.5 h-3.5 text-[#D88A1D]" />}
                </button>
              );
            })}
          </div>
        </div>

        <div className="text-[10px] text-gray-500 font-bold pt-6 border-t border-gray-300/60 mt-10">
          SECURE CREDENTIAL VAULT • CDL VERIFICATION ACTIVE
        </div>
      </div>

      {/* Right panel - Dark Theme Glassmorphism SignIn Card */}
      <div className="lg:col-span-7 bg-transparent p-8 lg:p-16 flex flex-col justify-center items-center z-10">
        <div className="w-full max-w-md bg-[#161A22]/85 border border-[rgba(255,255,255,0.06)] rounded-2xl p-8 shadow-2xl relative">
          
          <div className="mb-6">
            <h3 className="text-xl font-extrabold text-white tracking-tight mb-1 font-sans">Sign in to your account</h3>
            <p className="text-gray-400 text-xs">Enter your authorization credentials below.</p>
          </div>

          {/* Sign In Form */}
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Email Address</label>
              <div className="relative">
                <User className="absolute left-3 top-3 w-4 h-4 text-gray-600" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg pl-9 pr-3.5 py-2.5 text-xs text-white placeholder-gray-700 outline-none focus:border-[#D88A1D] transition"
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider">Password</label>
                <a href="#forgot" className="text-[10px] font-bold text-[#4EA8DE] hover:underline" onClick={(e) => {
                  e.preventDefault();
                  toast.info('Demo Mode: credentials are auto-filled on role switch.');
                }}>
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-4 h-4 text-gray-600" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg pl-9 pr-10 py-2.5 text-xs text-white placeholder-gray-700 outline-none focus:border-[#D88A1D] transition"
                  placeholder="Password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-500 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Password strength meter */}
            {password && (
              <div className="space-y-1.5 pt-1">
                <div className="flex justify-between items-center text-[9px] font-bold text-gray-500 uppercase">
                  <span>Vault Lock Integrity:</span>
                  <span className={pwStrength.label === 'Strong CDL Vault' ? 'text-[#4ADE80]' : ''}>{pwStrength.label}</span>
                </div>
                <div className="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
                  <div className={`h-full ${pwStrength.color} transition-all duration-300`} style={{ width: `${pwStrength.score}%` }}></div>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded bg-[#0F1117] border-[rgba(255,255,255,0.1)] text-[#D88A1D] focus:ring-[#D88A1D] accent-[#D88A1D]"
                />
                Remember this terminal profile
              </label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-3 rounded-lg shadow-lg hover:brightness-105 active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-4 disabled:opacity-40"
            >
              {isSubmitting ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin mr-1"></span>
                  Verifying Vault Integrity...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Permissions matrix description matching Screen 0 */}
          {activeRoleData && (
            <div className="mt-6 p-4 rounded-xl border border-[rgba(255,255,255,0.06)] bg-[#0F1117]/60 text-xs text-gray-400">
              <div className="flex items-center gap-2 text-white font-extrabold text-[11px] mb-2.5 border-b border-[rgba(255,255,255,0.06)] pb-1.5">
                <Shield className="w-3.5 h-3.5 text-[#D88A1D]" />
                Permissions granted to this role:
              </div>
              <ul className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                <li className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${activeRoleData.permissions.fleet.read ? 'bg-[#4ADE80]' : 'bg-red-400'}`}></span>
                  Fleet: {activeRoleData.permissions.fleet.write ? 'Read/Write' : 'Read'}
                </li>
                <li className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${activeRoleData.permissions.drivers.read ? 'bg-[#4ADE80]' : 'bg-red-400'}`}></span>
                  Drivers: {activeRoleData.permissions.drivers.write ? 'Read/Write' : 'Read'}
                </li>
                <li className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${activeRoleData.permissions.trips.read ? 'bg-[#4ADE80]' : 'bg-red-400'}`}></span>
                  Trips: {activeRoleData.permissions.trips.write ? 'Read/Write' : 'Read'}
                </li>
                <li className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${activeRoleData.permissions.maintenance.read ? 'bg-[#4ADE80]' : 'bg-red-400'}`}></span>
                  Service: {activeRoleData.permissions.maintenance.write ? 'Read/Write' : 'Read'}
                </li>
              </ul>
            </div>
          )}

        </div>
      </div>
    </motion.div>
  );
};
