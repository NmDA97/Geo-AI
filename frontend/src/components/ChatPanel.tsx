import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, MapPin } from 'lucide-react';

const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your Geo-AI assistant. You can ask me questions about urban planning, flood risks, or building regulations in Colombo North. Try clicking on the map to analyze a specific location.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages([...messages, { role: 'user', content: input }]);
    setInput('');

    // Mock AI response for now
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I am currently in "Mock Mode". Once the backend is integrated, I will analyze your request using spatial data and legal regulations. For now, I can see you are interested in "' + input + '".' 
      }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full gap-4 animate-in fade-in slide-in-from-right duration-500">
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30">
          <Sparkles className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-bold leading-none mb-1">Geo-AI Agent</h2>
          <p className="text-xs text-emerald-500 flex items-center gap-1 font-medium">
             Online
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center border ${
              m.role === 'user' ? 'bg-slate-800 border-slate-700' : 'bg-primary/20 border-primary/30 text-primary'
            }`}>
              {m.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            <div className={`p-3 rounded-2xl text-sm leading-relaxed ${
              m.role === 'user' 
                ? 'bg-primary text-white rounded-tr-none' 
                : 'bg-slate-900 border border-slate-800 rounded-tl-none'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto space-y-4">
        {/* Sample tooltips for map clicks */}
        <div className="flex items-center gap-2 px-2 py-1 bg-slate-900 border border-slate-800 rounded-lg text-[10px] text-slate-400">
          <MapPin className="w-3 h-3 text-risk-medium" />
          <span>Click a map location to auto-query</span>
        </div>

        <div className="relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about site suitability..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-4 pr-12 text-sm focus:outline-none focus:border-primary/50 transition-all placeholder:text-slate-600"
          />
          <button 
            onClick={handleSend}
            className="absolute right-2 top-1.5 p-1.5 rounded-lg bg-primary hover:bg-primary-dark transition-colors"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
