import { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

import { useStore } from './context/useStore';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { CommandPalette } from './components/CommandPalette';
import { Auth } from './pages/Auth';
import { Dashboard } from './pages/Dashboard';
import { Fleet } from './pages/Fleet';
import { Drivers } from './pages/Drivers';
import { Dispatcher } from './pages/Dispatcher';
import { Maintenance } from './pages/Maintenance';
import { FuelExpense } from './pages/FuelExpense';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { Toaster } from 'sonner';
import { Sparkles, X, MessageSquare, Send as SendIcon, Bot } from 'lucide-react';
import { toast } from 'sonner';

interface ChatMessage {
  sender: 'ai' | 'user';
  text: string;
  time: string;
}

function App() {
  const currentUser = useStore((state) => state.currentUser);
  const fetchVehicles = useStore((state) => state.fetchVehicles);
  const fetchDrivers = useStore((state) => state.fetchDrivers);
  const fetchTrips = useStore((state) => state.fetchTrips);
  const fetchMaintenanceLogs = useStore((state) => state.fetchMaintenanceLogs);
  const fetchExpenses = useStore((state) => state.fetchExpenses);

  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    if (currentUser) {
      fetchVehicles();
      fetchDrivers();
      fetchTrips();
      fetchMaintenanceLogs();
      fetchExpenses();
    }
  }, [currentUser, fetchVehicles, fetchDrivers, fetchTrips, fetchMaintenanceLogs, fetchExpenses]);
  
  // AI Copilot states
  const [aiOpen, setAiOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { 
      sender: 'ai', 
      text: 'Hello! I am your TransOps Copilot. I can inspect vehicle telemetry logs, optimize active dispatch routes, or check driver safety scorecards.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, aiOpen]);

  const handleSendAiMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userText = inputMessage.trim();
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add user message
    const newMessages = [...messages, { sender: 'user' as const, text: userText, time: currentTime }];
    setMessages(newMessages);
    setInputMessage('');

    // Trigger AI response calculation
    setTimeout(() => {
      let aiResponseText = "I can help you review vehicle telemetry, check driver logs, or optimize route runs. Try asking 'Which truck needs maintenance?'";
      
      const normalized = userText.toLowerCase();
      if (normalized.includes('truck') || normalized.includes('vehicle') || normalized.includes('maintenance') || normalized.includes('service') || normalized.includes('broke')) {
        aiResponseText = "Telemetry diagnostics check: Tractor VEH-1243 has active brake sensor warning logs. Scheduled for Speedy Fleet Workshop Bay 01.";
      } else if (normalized.includes('route') || normalized.includes('dallas') || normalized.includes('houston') || normalized.includes('dispatch') || normalized.includes('optimize') || normalized.includes('map')) {
        aiResponseText = "AI Route Optimizer suggests bypassing congestion on I-45 North to save 45 minutes on Houston -> Dallas transit.";
      } else if (normalized.includes('safety') || normalized.includes('driver') || normalized.includes('cdl') || normalized.includes('violat')) {
        aiResponseText = "Safety compliance rating is at 94.3% average. Driver Alice Brown CDL license renewal is in 12 days.";
      }

      setMessages(prev => [...prev, { sender: 'ai' as const, text: aiResponseText, time: currentTime }]);
      toast.message('Copilot telemetry response loaded.');
    }, 700);
  };

  return (
    <BrowserRouter>
      <div className="flex h-screen w-screen overflow-hidden bg-[#0F1117] text-gray-200 relative">
        
        {/* Render Sidebar Navigation if user logged in */}
        {currentUser && <Sidebar />}

        {/* Content Shell */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          
          {/* Render Header if user logged in */}
          {currentUser && <Header onSearchClick={() => setSearchOpen(true)} />}

          {/* Scrollable Main View Area */}
          <main className="flex-1 overflow-y-auto p-6 scrollbar-thin">
            <Routes>
              {/* Unauthenticated / Login Route */}
              <Route 
                path="/" 
                element={!currentUser ? <Auth /> : <Navigate to="/dashboard" replace />} 
              />

              {/* Authenticated Application Routes */}
              <Route 
                path="/dashboard" 
                element={currentUser ? <Dashboard /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/fleet" 
                element={currentUser ? <Fleet /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/drivers" 
                element={currentUser ? <Drivers /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/dispatcher" 
                element={currentUser ? <Dispatcher /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/maintenance" 
                element={currentUser ? <Maintenance /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/fuel-expense" 
                element={currentUser ? <FuelExpense /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/analytics" 
                element={currentUser ? <Analytics /> : <Navigate to="/" replace />} 
              />
              <Route 
                path="/settings" 
                element={currentUser ? <Settings /> : <Navigate to="/" replace />} 
              />

              {/* Wildcard Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>

        {/* Floating AI Panel (Collapsible Chat Widget) */}
        {currentUser && (
          <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            <AnimatePresence>
              {aiOpen && (
                <motion.div 
                  initial={{ opacity: 0, y: 30, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 30, scale: 0.95 }}
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                  className="w-80 h-96 glass rounded-2xl border border-[rgba(255,255,255,0.08)] shadow-2xl flex flex-col mb-4 overflow-hidden"
                >
                  {/* Copilot Header */}
                  <div className="p-3.5 border-b border-[rgba(255,255,255,0.06)] bg-white/[0.01] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded bg-[#D88A1D]/15 text-[#D88A1D] flex items-center justify-center">
                        <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                      </div>
                      <div>
                        <span className="text-white text-xs font-bold font-sans block">TransOps Copilot</span>
                        <span className="text-[9px] text-gray-500 font-semibold uppercase tracking-wider block">Operational Safety Assistant</span>
                      </div>
                    </div>
                    <button 
                      onClick={() => setAiOpen(false)}
                      className="text-gray-500 hover:text-white p-1 hover:bg-white/5 rounded transition"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Messages Stream */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin text-xs">
                    {messages.map((msg, idx) => (
                      <div 
                        key={idx} 
                        className={`flex gap-2 max-w-[85%] ${
                          msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
                        }`}
                      >
                        {msg.sender === 'ai' && (
                          <div className="h-6.5 w-6.5 rounded-full bg-gray-800 border border-[rgba(255,255,255,0.06)] flex-shrink-0 flex items-center justify-center text-white">
                            <Bot className="w-3.5 h-3.5 text-[#D88A1D]" />
                          </div>
                        )}
                        <div>
                          <div className={`p-2.5 rounded-xl border text-[11px] leading-relaxed ${
                            msg.sender === 'user'
                              ? 'bg-[#D88A1D]/15 border-[#D88A1D]/20 text-white rounded-tr-none'
                              : 'bg-[#161A22] border-[rgba(255,255,255,0.06)] text-gray-300 rounded-tl-none'
                          }`}>
                            {msg.text}
                          </div>
                          <span className={`text-[8px] text-gray-500 block mt-1 ${
                            msg.sender === 'user' ? 'text-right' : ''
                          }`}>
                            {msg.time}
                          </span>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input Form */}
                  <form onSubmit={handleSendAiMessage} className="p-3 border-t border-[rgba(255,255,255,0.06)] bg-white/[0.01] flex gap-2">
                    <input
                      type="text"
                      placeholder="Ask copilot..."
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      className="flex-1 bg-[#0F1117] border border-[rgba(255,255,255,0.06)] rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-600 outline-none focus:border-[#D88A1D]"
                    />
                    <button
                      type="submit"
                      className="h-8 w-8 rounded-lg bg-gradient-to-r from-[#D88A1D] to-[#F59E0B] text-black flex items-center justify-center hover:brightness-105 active:scale-[0.97] transition flex-shrink-0"
                    >
                      <SendIcon className="w-3.5 h-3.5 text-black" />
                    </button>
                  </form>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Chat Trigger Button */}
            <button
              onClick={() => setAiOpen(!aiOpen)}
              className="h-12 w-12 rounded-full bg-gradient-to-tr from-[#D88A1D] to-[#F59E0B] text-black shadow-lg shadow-[#D88A1D]/20 flex items-center justify-center hover:scale-105 active:scale-95 transition-all duration-300 relative group border border-[#D88A1D]/15"
              title="Open AI Command Copilot"
            >
              <AnimatePresence mode="wait">
                {aiOpen ? (
                  <motion.div key="close" initial={{ rotate: -90 }} animate={{ rotate: 0 }} exit={{ rotate: 90 }}>
                    <X className="w-5.5 h-5.5 text-black" />
                  </motion.div>
                ) : (
                  <motion.div key="chat" initial={{ rotate: 90 }} animate={{ rotate: 0 }} exit={{ rotate: -90 }} className="relative">
                    <MessageSquare className="w-5.5 h-5.5 text-black" />
                    <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-[#4ADE80] border-2 border-[#0F1117] animate-pulse"></span>
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          </div>
        )}

        {/* Command Palette Search Overlay */}
        <CommandPalette open={searchOpen} setOpen={setSearchOpen} />

        {/* Sonner Toast Notification Center */}
        <Toaster theme="dark" position="top-right" closeButton expand={false} />
      </div>
    </BrowserRouter>
  );
}

export default App;
