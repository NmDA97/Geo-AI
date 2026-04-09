import React, { useEffect, useState } from 'react';
import { ShieldAlert, Building2, Droplet, Activity, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';

interface EdaPanelProps {
  selectedLayers: string[];
  toggleLayer: (layer: string) => void;
}

interface StatsData {
  geometric: {
    mean_footprint: number;
    median_footprint: number;
    total_built_area: number;
    large_buildings_count: number;
  };
  risk: {
    total_buildings: number;
    buildings_at_risk: number;
    risk_percentage: number;
    flood_area_sqkm: number;
  };
  infrastructure: {
      total_road_length_km: number;
  };
  metadata: {
    study_area: string;
    last_updated: string;
  };
}

const EdaPanel: React.FC<EdaPanelProps> = ({ selectedLayers, toggleLayer }) => {
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Error loading stats:', err));
  }, []);

  const layers = [
    { id: 'flood', name: 'Flood Risk Areas', icon: ShieldAlert, color: 'text-blue-400', glow: 'shadow-blue-500/20' },
    { id: 'buildings', name: 'Building Footprints', icon: Building2, color: 'text-amber-400', glow: 'shadow-amber-500/20' },
    { id: 'roads', name: 'Road Network', icon: Droplet, color: 'text-slate-400', glow: 'shadow-slate-500/20' },
  ];

  const chartData = stats ? [
    { name: 'Small', value: stats.risk.total_buildings - stats.geometric.large_buildings_count, color: '#3b82f6' },
    { name: 'Large', value: stats.geometric.large_buildings_count, color: '#f59e0b' },
  ] : [];

  return (
    <div className="flex flex-col gap-10">
      {/* Session Header */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <span className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400/60">Data Overview</span>
        </div>
        <h2 className="text-3xl font-black text-white italic tracking-tighter">METRICS</h2>
      </motion.div>

      {/* Layers Section */}
      <div className="space-y-6">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-3">
          <span className="w-8 h-[1px] bg-slate-800" />
          Control Layers
        </h3>
        
        <div className="grid gap-3">
          {layers.map((layer, index) => (
            <motion.button
              key={layer.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toggleLayer(layer.id)}
              className={`flex items-center gap-4 p-5 rounded-2xl border transition-all duration-500 ${
                selectedLayers.includes(layer.id)
                  ? `bg-blue-500/10 border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.1)]`
                  : 'bg-slate-900/40 border-slate-800/50 hover:border-slate-700'
              }`}
            >
              <div className={`p-3 rounded-xl ${selectedLayers.includes(layer.id) ? 'bg-blue-500/20' : 'bg-slate-800/50'}`}>
                <layer.icon className={`w-5 h-5 ${selectedLayers.includes(layer.id) ? layer.color : 'text-slate-500'}`} />
              </div>
              <div className="flex-1 text-left">
                <p className={`text-xs font-black uppercase tracking-wider ${selectedLayers.includes(layer.id) ? 'text-white' : 'text-slate-500'}`}>
                  {layer.name}
                </p>
                <p className="text-[9px] text-slate-600 font-bold uppercase tracking-tight">Active Sensor Vector</p>
              </div>
              <div className={`w-1.5 h-1.5 rounded-full ${selectedLayers.includes(layer.id) ? 'bg-blue-400 shadow-[0_0_8px_#3b82f6]' : 'bg-slate-800'}`} />
            </motion.button>
          ))}
        </div>
      </div>

      {/* Analytics Section */}
      <AnimatePresence>
        {stats && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            <div className="grid grid-cols-2 gap-4">
               <motion.div 
                 whileHover={{ y: -2 }}
                 className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/50"
               >
                  <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-2">Footprints</p>
                  <p className="text-2xl font-black text-white italic">{stats.risk.total_buildings.toLocaleString()}</p>
               </motion.div>
               <motion.div 
                 whileHover={{ y: -2 }}
                 className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800/50"
               >
                  <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-2">Network</p>
                  <p className="text-2xl font-black text-white italic">{Math.round(stats.infrastructure?.total_road_length_km || 0)}<span className="text-xs ml-1 text-slate-600">km</span></p>
               </motion.div>
            </div>

            <div className="space-y-4">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-3">
                <span className="w-8 h-[1px] bg-slate-800" />
                Distribution
              </h3>
              <div className="h-56 w-full glass-panel rounded-3xl p-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" fontSize={9} axisLine={false} tickLine={false} tick={{ fill: '#475569', fontWeight: 900 }} />
                    <Tooltip 
                      cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                      contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(51, 65, 85, 0.5)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                      itemStyle={{ color: '#94a3b8', fontSize: '10px', fontWeight: '900', textTransform: 'uppercase' }}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Critical Alert */}
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-6 rounded-3xl bg-red-500/5 border border-red-500/20 flex gap-4 relative overflow-hidden group"
            >
              <div className="absolute top-0 right-0 p-2 opacity-5">
                <ShieldAlert className="w-16 h-16 text-red-500" />
              </div>
              <div className="p-3 bg-red-500/20 rounded-xl h-fit">
                <ShieldAlert className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <p className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-1">Risk_Protocol_Alpha</p>
                <p className="text-[11px] text-slate-400 leading-relaxed font-medium">
                  {stats.risk.buildings_at_risk > 0 
                    ? `[${stats.risk.buildings_at_risk}] structures identified in flood corridor. Immediate intervention recommended for high-exposure zones.`
                    : "Primary corridors clear. No immediate hydraulic risk detected in study area."}
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer Info */}
      <div className="mt-auto pt-6 border-t border-slate-800/30 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-3 h-3 text-blue-500" />
          <span className="text-[9px] font-black text-slate-600 uppercase">Engine Status: Optimal</span>
        </div>
        <span className="text-[9px] font-black text-slate-700">v1.2.4-stable</span>
      </div>
    </div>
  );
};

export default EdaPanel;
