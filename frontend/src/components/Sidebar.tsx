import React from 'react';
import { 
  BarChart3, 
  MessageSquare, 
  Settings,
  ChevronLeft,
  LayoutDashboard,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface SidebarProps {
  activeMode: 'eda' | 'agent';
  setActiveMode: (mode: 'eda' | 'agent') => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeMode, setActiveMode, isOpen, setIsOpen }) => {
  return (
    <div className="w-24 glass-panel border-r border-slate-800/50 flex flex-col items-center py-10 gap-16 z-[1100] h-full shadow-[20px_0_40px_rgba(0,0,0,0.3)]">
      {/* Brand Icon */}
      <motion.div 
        whileHover={{ scale: 1.1, rotate: 5 }}
        className="w-12 h-12 bg-blue-600/20 rounded-2xl flex items-center justify-center border-2 border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.3)] cursor-pointer"
      >
        <LayoutDashboard className="w-6 h-6 text-blue-400" />
      </motion.div>

      {/* Main Navigation */}
      <nav className="flex-1 flex flex-col gap-10">
        <div className="relative group">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveMode('eda')}
            className={`p-4 rounded-2xl transition-all duration-500 relative ${
              activeMode === 'eda' 
                ? 'bg-blue-600 text-white shadow-[0_0_30px_rgba(59,130,246,0.5)] border border-blue-400/50' 
                : 'text-slate-500 hover:text-blue-400 hover:bg-blue-500/5'
            }`}
          >
            <BarChart3 className="w-6 h-6" />
            {activeMode === 'eda' && (
              <motion.div 
                layoutId="active-indicator"
                className="absolute -right-12 top-1/2 -translate-y-1/2 w-2 h-8 bg-blue-500 rounded-full blur-[4px]"
              />
            )}
          </motion.button>
          <span className="absolute left-full ml-6 px-3 py-1.5 glass-panel text-blue-400 text-[10px] font-black uppercase tracking-widest rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0 whitespace-nowrap pointer-events-none z-[1200] border border-blue-500/30">
            Explorer
          </span>
        </div>

        <div className="relative group">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveMode('agent')}
            className={`p-4 rounded-2xl transition-all duration-500 relative ${
              activeMode === 'agent' 
                ? 'bg-amber-600 text-white shadow-[0_0_30px_rgba(245,158,11,0.5)] border border-amber-400/50' 
                : 'text-slate-500 hover:text-amber-400 hover:bg-amber-500/5'
            }`}
          >
            <MessageSquare className="w-6 h-6" />
            {activeMode === 'agent' && (
              <motion.div 
                layoutId="active-indicator"
                className="absolute -right-12 top-1/2 -translate-y-1/2 w-2 h-8 bg-amber-500 rounded-full blur-[4px]"
              />
            )}
          </motion.button>
          <span className="absolute left-full ml-6 px-3 py-1.5 glass-panel text-amber-400 text-[10px] font-black uppercase tracking-widest rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0 whitespace-nowrap pointer-events-none z-[1200] border border-amber-500/30">
            Geo_AI
          </span>
        </div>
      </nav>

      {/* Bottom Actions */}
      <div className="flex flex-col gap-8 mt-auto mb-4">
        <motion.button 
          whileHover={{ rotate: 90 }}
          className="p-3 text-slate-600 hover:text-slate-400 transition-colors"
        >
          <Settings className="w-6 h-6" />
        </motion.button>
        
        <motion.button 
          whileHover={{ scale: 1.2 }}
          onClick={() => setIsOpen(!isOpen)}
          className="p-4 bg-slate-900/50 border border-slate-800 rounded-2xl text-slate-500 hover:text-white transition-all shadow-xl"
        >
          <ChevronLeft className={`w-6 h-6 transition-transform duration-500 ${!isOpen ? 'rotate-180' : ''}`} />
        </motion.button>
      </div>
    </div>
  );
};

export default Sidebar;
