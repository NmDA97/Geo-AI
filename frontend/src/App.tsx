import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronRight,
  Globe,
  Terminal
} from 'lucide-react';
import MapView from './components/MapView';
import Sidebar from './components/Sidebar';
import EdaPanel from './components/EdaPanel';
import ChatPanel from './components/ChatPanel';

const App: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'eda' | 'agent'>('eda');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedLayers, setSelectedLayers] = useState<string[]>(['buildings', 'roads', 'flood']);

  const toggleLayer = (layerId: string) => {
    setSelectedLayers(prev => 
      prev.includes(layerId) 
        ? prev.filter(id => id !== layerId) 
        : [...prev, layerId]
    );
  };

  return (
    <div className="flex h-screen w-full bg-[#020617] overflow-hidden text-slate-200 font-sans relative">
      {/* Background Glows */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 blur-[120px] rounded-full -mr-64 -mt-64 z-0 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-amber-600/5 blur-[120px] rounded-full -ml-64 -mb-64 z-0 pointer-events-none" />

      {/* Navigation Sidebar */}
      <Sidebar 
        activeMode={activeMode} 
        setActiveMode={setActiveMode} 
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      {/* Control Panel */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.div 
            initial={{ x: -400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -400, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-96 glass-panel border-r border-slate-800/50 flex flex-col z-10"
          >
            <div className="p-8 flex-1 overflow-y-auto no-scrollbar">
              <div className="flex items-center gap-4 mb-10">
                <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20">
                  {activeMode === 'eda' ? <Globe className="w-6 h-6 text-blue-400" /> : <Terminal className="w-6 h-6 text-amber-400" />}
                </div>
                <div>
                  <h2 className="text-xl font-black tracking-tight text-white italic">
                    {activeMode === 'eda' ? 'SCANNING_NORTH' : 'GEO_INTEL_AI'}
                  </h2>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">
                    {activeMode === 'eda' ? 'Colombo Spatial Engine' : 'Neural Core Ready'}
                  </p>
                </div>
              </div>

              {activeMode === 'eda' ? (
                <EdaPanel selectedLayers={selectedLayers} toggleLayer={toggleLayer} />
              ) : (
                <ChatPanel />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Map View */}
      <div className="flex-1 relative z-0">
        <MapView selectedLayers={selectedLayers} />
        
        {/* Toggle Panel Button */}
        {!sidebarOpen && (
          <motion.button 
            initial={{ scale: 0, x: -20 }}
            animate={{ scale: 1, x: 0 }}
            onClick={() => setSidebarOpen(true)}
            className="absolute top-8 left-8 z-[1000] p-4 glass-panel rounded-2xl hover:bg-slate-800/80 transition-all group border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.2)]"
          >
            <ChevronRight className="w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        )}

        {/* Floating Stats Card */}
        <AnimatePresence mode="wait">
          {activeMode === 'eda' && (
            <motion.div 
              initial={{ y: -40, opacity: 0, filter: 'blur(10px)' }}
              animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
              exit={{ y: -40, opacity: 0, filter: 'blur(10px)' }}
              className="absolute top-8 right-8 z-[1000] w-80 p-6 glass-panel rounded-3xl pointer-events-none"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                  <h3 className="text-[11px] font-black uppercase tracking-[0.2em] text-blue-400/80">Telemetry Live</h3>
                </div>
                <div className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] text-blue-400 font-black italic">
                  SYNC_OK
                </div>
              </div>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Flood Risk Probability</p>
                    <span className="text-sm font-black text-red-400 neon-text-red">82.4%</span>
                  </div>
                  <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden border border-slate-800/50 p-[1px]">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: '82.4%' }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-red-500 rounded-full" 
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-6 pt-2 border-t border-slate-800/30">
                  <div>
                    <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest">Pop Density</p>
                    <p className="text-2xl font-black text-white italic">14.2k<span className="text-xs text-slate-600 ml-1">avg</span></p>
                  </div>
                  <div>
                    <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest">Zone Status</p>
                    <p className="text-xl font-black text-orange-400 italic leading-tight">ALERT_LV3</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default App;
