import React, { useState } from 'react'
import { Activity, TrendingUp, Users, ArrowUpRight } from 'lucide-react'

export default function VelocityView() {
    const [timeframe, setTimeframe] = useState('7d')

    // Mock data
    const metrics = {
        growth: '+124%',
        newLeads: 843,
        velocity: 'High',
        displacement: 'Active'
    }

    return (
        <div className="animate-slide-up space-y-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-black flex items-center gap-3 text-white">
                    <Activity className="text-pearl" size={24} />
                    VELOCITY ENGINE
                </h2>
                <div className="flex gap-2 bg-slate-800/50 p-1 rounded-lg border border-white/5">
                    {['24h', '7d', '30d'].map(t => (
                        <button
                            key={t}
                            onClick={() => setTimeframe(t)}
                            className={`px-3 py-1.5 rounded-md text-xs font-bold uppercase transition-all ${timeframe === t
                                    ? 'bg-pearl text-black shadow-glow'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-6 bg-white/5 flex flex-col justify-between">
                    <div className="flex justify-between items-start">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Lead Velocity</div>
                        <TrendingUp size={16} className="text-emerald-400" />
                    </div>
                    <div>
                        <div className="text-4xl font-black text-white mt-4">{metrics.growth}</div>
                        <div className="text-xs font-bold text-emerald-400 mt-2 flex items-center gap-1">
                            <ArrowUpRight size={12} /> Trending Up
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-6 bg-white/5 flex flex-col justify-between">
                    <div className="flex justify-between items-start">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">New Targets</div>
                        <Users size={16} className="text-pearl" />
                    </div>
                    <div>
                        <div className="text-4xl font-black text-white mt-4">{metrics.newLeads}</div>
                        <div className="text-xs text-slate-500 mt-2 font-mono">In last {timeframe}</div>
                    </div>
                </div>

                <div className="glass-panel p-6 bg-white/5 flex flex-col justify-between">
                    <div className="flex justify-between items-start">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Pipeline Health</div>
                        <Activity size={16} className="text-amber-400" />
                    </div>
                    <div>
                        <div className="text-4xl font-black text-pearl mt-4">{metrics.velocity}</div>
                        <div className="text-xs text-slate-500 mt-2">Conversion Optimal</div>
                    </div>
                </div>
            </div>

            <div className="glass-panel p-8 bg-white/5 border border-white/5">
                <h3 className="text-sm font-bold text-slate-300 mb-6 uppercase tracking-wider">Predictive Growth Trajectory</h3>
                <div className="h-48 flex items-end gap-2 sm:gap-4 pb-4 border-b border-white/5">
                    {/* Visual Bar Chart */}
                    {[40, 55, 45, 70, 85, 95, 120].map((h, i) => (
                        <div key={i} className="flex-1 relative group w-full">
                            <div
                                style={{ height: `${h}%` }}
                                className="w-full bg-gradient-to-t from-pearl/20 to-pearl/60 rounded-t-sm group-hover:from-pearl/40 group-hover:to-pearl transition-all duration-300 relative overflow-hidden"
                            >
                                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </div>
                            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[0.6rem] font-bold text-slate-500">
                                {['M', 'T', 'W', 'T', 'F', 'S', 'S'][i]}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
