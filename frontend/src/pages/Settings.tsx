import React, { useState } from 'react';
import { useStore } from '../context/useStore';
import { motion } from 'framer-motion';
import type { RolePermissions } from '../context/useStore';
import { Settings as SettingsIcon, ShieldAlert, Save, ToggleLeft, ToggleRight, Key, ListFilter } from 'lucide-react';
import { toast } from 'sonner';

export const Settings: React.FC = () => {
  const { rolesConfig, updateRolePermissions } = useStore();
  const [activeTab, setActiveTab] = useState<'access' | 'audit' | 'api' | 'integrations'>('access');

  // General settings local state
  const [companyName, setCompanyName] = useState('TransOps Logistics Global');
  const [timezone, setTimezone] = useState('Central Standard Time (CST)');
  const [alertSpeedLimit, setAlertSpeedLimit] = useState(72);
  const [emailAlerts, setEmailAlerts] = useState(true);

  // API Keys state
  const [apiKeys, setApiKeys] = useState([
    { name: 'SAP Integration Key', key: 'pk_live_51N...8y7x', created: '2024-01-15' },
    { name: 'Amazon Warehouse Sync', key: 'pk_live_38d...9u2c', created: '2024-02-10' }
  ]);

  const generateApiKey = () => {
    const newKey = {
      name: 'Dynamic Command Key',
      key: `pk_live_${Math.random().toString(36).substring(2, 8)}...${Math.random().toString(36).substring(2, 6)}`,
      created: new Date().toISOString().split('T')[0]
    };
    setApiKeys([...apiKeys, newKey]);
    toast.success('Successfully generated new API credential key.');
  };

  const categories: { key: keyof RolePermissions; label: string }[] = [
    { key: 'fleet', label: 'Fleet Registry' },
    { key: 'drivers', label: 'Drivers Registry' },
    { key: 'trips', label: 'Trip Dispatcher' },
    { key: 'maintenance', label: 'Maintenance Logs' },
    { key: 'finance', label: 'Finance Records' },
    { key: 'settings', label: 'System Settings' }
  ];

  const handleCheckboxChange = (roleName: string, category: keyof RolePermissions, type: 'read' | 'write', value: boolean) => {
    updateRolePermissions(roleName, category, type, value);
    toast.message(`RBAC privs changed: ${roleName} ${category} ${type} → ${value ? 'Allowed' : 'Denied'}`);
  };

  const handleSaveGeneralSettings = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('General System Settings compiled and saved.');
  };

  const auditLogs = [
    { time: '10:42:15', user: 'admin@transops.com', action: 'Modified dispatcher write privilege matrix' },
    { time: '09:30:12', user: 'dispatcher@transops.com', action: 'Authorized live run dispatch order TRP-101' },
    { time: '08:15:44', user: 'officer@transops.com', action: 'Resolved coolant temperature warning flag VEH-8831' },
    { time: '07:40:11', user: 'admin@transops.com', action: 'Deregistered decommissioned tractor VEH-2099' }
  ];

  const integrations = [
    { name: 'SAP Fiori logistics', status: 'Connected', desc: 'Syncs active dispatch run sheets with global logistics ledger.' },
    { name: 'Stripe Accounting Logs', status: 'Connected', desc: 'Auto-bills diesel expenses to fuel cards.' },
    { name: 'Amazon Warehouse API', status: 'Disconnected', desc: 'Pulls cargo weights for upcoming load pickups.' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="space-y-6 relative"
    >
      
      {/* Settings Navigation Tabs */}
      <div className="flex border-b border-[rgba(255,255,255,0.06)] gap-6 text-xs font-bold uppercase tracking-wider text-gray-500">
        <button 
          onClick={() => setActiveTab('access')}
          className={`pb-3 transition ${activeTab === 'access' ? 'text-[#D88A1D] border-b-2 border-[#D88A1D]' : 'hover:text-white'}`}
        >
          Access & RBAC Matrix
        </button>
        <button 
          onClick={() => setActiveTab('audit')}
          className={`pb-3 transition ${activeTab === 'audit' ? 'text-[#D88A1D] border-b-2 border-[#D88A1D]' : 'hover:text-white'}`}
        >
          Operations Audit Logs
        </button>
        <button 
          onClick={() => setActiveTab('api')}
          className={`pb-3 transition ${activeTab === 'api' ? 'text-[#D88A1D] border-b-2 border-[#D88A1D]' : 'hover:text-white'}`}
        >
          API Integrations Keys
        </button>
        <button 
          onClick={() => setActiveTab('integrations')}
          className={`pb-3 transition ${activeTab === 'integrations' ? 'text-[#D88A1D] border-b-2 border-[#D88A1D]' : 'hover:text-white'}`}
        >
          Connected ERP Services
        </button>
      </div>

      {activeTab === 'access' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* General settings form */}
          <div className="lg:col-span-4 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 flex flex-col justify-between shadow-2xl">
            <div>
              <div className="border-b border-[rgba(255,255,255,0.06)] pb-3 mb-5">
                <h4 className="text-white font-bold text-sm font-sans flex items-center gap-2">
                  <SettingsIcon className="w-4.5 h-4.5 text-[#D88A1D]" />
                  General System Settings
                </h4>
                <p className="text-xs text-gray-500 mt-0.5">Configure defaults for transponders</p>
              </div>

              <form onSubmit={handleSaveGeneralSettings} className="space-y-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Company Name</label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">System Timezone</label>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2.5 text-xs text-white outline-none focus:border-[#D88A1D]"
                  >
                    <option value="Eastern Standard Time (EST)">Eastern Standard Time (EST)</option>
                    <option value="Central Standard Time (CST)">Central Standard Time (CST)</option>
                    <option value="Pacific Standard Time (PST)">Pacific Standard Time (PST)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1.5">Critical Speed Flag (mph)</label>
                  <input
                    type="number"
                    min="50"
                    max="90"
                    value={alertSpeedLimit}
                    onChange={(e) => setAlertSpeedLimit(Number(e.target.value))}
                    className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-[#D88A1D]"
                  />
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-[rgba(255,255,255,0.06)]">
                  <div>
                    <span className="block text-xs font-semibold text-white">Email dispatch receipts</span>
                    <span className="text-[10px] text-gray-500">Alerts safety leads on violation flags</span>
                  </div>
                  <button 
                    type="button" 
                    onClick={() => setEmailAlerts(!emailAlerts)}
                    className="text-gray-400 hover:text-white transition"
                  >
                    {emailAlerts ? <ToggleRight className="w-9 h-9 text-[#D88A1D]" /> : <ToggleLeft className="w-9 h-9 text-gray-600" />}
                  </button>
                </div>

                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black font-extrabold text-xs py-2.5 rounded-lg shadow-lg hover:brightness-105 transition-all flex items-center justify-center gap-2 mt-4"
                >
                  <Save className="w-4 h-4" />
                  Save Preferences
                </button>
              </form>
            </div>
          </div>

          {/* RBAC Matrix config */}
          <div className="lg:col-span-8 bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-[rgba(255,255,255,0.06)]">
              <h5 className="text-white font-bold text-sm">Role-Based Access Control (RBAC) settings</h5>
              <p className="text-xs text-gray-500 mt-0.5">Customize resource level permissions for operators</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[rgba(255,255,255,0.06)] bg-white/[0.005] text-gray-400 font-bold uppercase tracking-wider">
                    <th className="p-3.5">System Roles</th>
                    {categories.map((c) => (
                      <th key={c.key} className="p-3.5 text-center" colSpan={2}>
                        <span className="block text-[10px] font-bold">{c.label}</span>
                        <span className="inline-flex gap-4 text-[8px] text-gray-500 font-semibold font-mono uppercase mt-0.5">
                          <span>R</span>
                          <span>W</span>
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[rgba(255,255,255,0.06)] text-gray-300">
                  {Object.values(rolesConfig).map((role) => (
                    <tr key={role.name} className="hover:bg-white/[0.01] transition apple-transition">
                      <td className="p-3.5">
                        <span className="font-extrabold text-white text-xs block">{role.name}</span>
                        <span className="text-[10px] text-gray-500 block max-w-[150px] truncate leading-tight mt-0.5">{role.description}</span>
                      </td>
                      {categories.map((c) => {
                        const readVal = role.permissions[c.key].read;
                        const writeVal = role.permissions[c.key].write;
                        return (
                          <React.Fragment key={`${role.name}-${c.key}`}>
                            <td className="p-3.5 text-center border-l border-[rgba(255,255,255,0.02)]">
                              <input
                                type="checkbox"
                                checked={readVal}
                                onChange={(e) => handleCheckboxChange(role.name, c.key, 'read', e.target.checked)}
                                className="rounded bg-[#0F1117] border-[rgba(255,255,255,0.1)] text-[#D88A1D] focus:ring-[#D88A1D] accent-[#D88A1D]"
                              />
                            </td>
                            <td className="p-3.5 text-center border-r border-[rgba(255,255,255,0.02)]">
                              <input
                                type="checkbox"
                                checked={writeVal}
                                onChange={(e) => handleCheckboxChange(role.name, c.key, 'write', e.target.checked)}
                                className="rounded bg-[#0F1117] border-[rgba(255,255,255,0.1)] text-[#D88A1D] focus:ring-[#D88A1D] accent-[#D88A1D]"
                              />
                            </td>
                          </React.Fragment>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-4 bg-yellow-500/10 border-t border-[rgba(255,255,255,0.06)] text-[11px] text-yellow-300 flex gap-2">
              <ShieldAlert className="w-4.5 h-4.5 flex-shrink-0" />
              <span>CAUTION: Editing the RBAC permissions matrix immediately updates system visibility. Ensure that dispatcher and analyst profiles maintain correct reading capabilities to avoid operation disruption.</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-2xl space-y-4">
          <div>
            <h4 className="text-white font-bold text-sm flex items-center gap-2">
              <ListFilter className="w-4.5 h-4.5 text-[#D88A1D]" />
              Operations Security Audit Log
            </h4>
            <p className="text-xs text-gray-500 mt-0.5 font-medium">Surveillance chronological trail of ledger modifications</p>
          </div>

          <div className="space-y-2">
            {auditLogs.map((log, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-[#0F1117]/60 border border-[rgba(255,255,255,0.02)] text-xs text-gray-300 font-mono">
                <div className="flex items-center gap-4">
                  <span className="text-gray-500">{log.time}</span>
                  <span className="text-[#4EA8DE] font-semibold">{log.user}</span>
                  <span className="text-white font-medium">{log.action}</span>
                </div>
                <span className="text-[9px] text-[#4ADE80] bg-[#4ADE80]/15 px-1.5 py-0.5 rounded font-extrabold uppercase">Verified</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'api' && (
        <div className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-2xl space-y-5">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="text-white font-bold text-sm flex items-center gap-2">
                <Key className="w-4.5 h-4.5 text-[#D88A1D]" />
                API Integration Key Manager
              </h4>
              <p className="text-xs text-gray-500 mt-0.5">Manage keys for SAP, Stripe Payment flows or internal databases</p>
            </div>
            <button 
              onClick={generateApiKey}
              className="bg-[#D88A1D] hover:brightness-105 text-black font-extrabold text-xs px-3.5 py-2 rounded-lg transition"
            >
              Generate New API Key
            </button>
          </div>

          <div className="space-y-3 font-mono">
            {apiKeys.map((key, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-[#0F1117]/60 border border-[rgba(255,255,255,0.02)] text-xs">
                <div>
                  <span className="block text-xs font-bold text-white font-sans">{key.name}</span>
                  <span className="text-gray-500 mt-0.5 block">Created: {key.created}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-white bg-[#161A22] px-2.5 py-1 rounded border border-[rgba(255,255,255,0.04)]">{key.key}</span>
                  <button 
                    onClick={() => toast.success('API credential key copied to clipboard.')}
                    className="text-[#4EA8DE] hover:underline font-bold font-sans text-xs"
                  >
                    Copy
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'integrations' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {integrations.map((item, idx) => (
            <div key={idx} className="bg-[#161A22] rounded-xl border border-[rgba(255,255,255,0.06)] p-5 shadow-lg flex flex-col justify-between h-40">
              <div>
                <div className="flex justify-between items-center mb-2.5">
                  <span className="font-bold text-white text-xs">{item.name}</span>
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                    item.status === 'Connected' ? 'bg-[#4ADE80]/15 text-[#4ADE80]' : 'bg-gray-800 text-gray-500'
                  }`}>
                    {item.status}
                  </span>
                </div>
                <p className="text-[11px] text-gray-400 leading-tight">{item.desc}</p>
              </div>
              <button 
                onClick={() => toast.message(`Configuring ${item.name} integration options...`)}
                className="w-full bg-[#0F1117] border border-[rgba(255,255,255,0.04)] hover:border-white/10 text-white font-bold text-[10px] py-1.5 rounded transition"
              >
                Configure Connection
              </button>
            </div>
          ))}
        </div>
      )}

    </motion.div>
  );
};
