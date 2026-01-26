import React, { useState } from 'react'
import { Activity, TrendingUp, Users, ArrowUpRight, Cpu, Zap, BarChart3, Globe } from 'lucide-react'

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
        <div className="space-y-6 animate-slide-up">

            {/* Header / Toggles */}
            <div className="flex justify-between items-end gap-6 border-b border-white/5 pb-6">
                <div className="space-y-1">
                    <h2 className="text-2xl font-display font-black text-white tracking-widest flex items-center gap-3">
                        <Activity className="text-pearl animate-pulse" size={24} />
                        VELOCITY <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">ENGINE</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <BarChart3 size={12} className="text-pearl" />
                        <span>PREDICTIVE TRAJECTORY CALCULATED // 98.4% CONFIDENCE</span>
                    </div>
                </div>

                <div className="flex gap-2 bg-black/40 p-1 rounded-lg border border-white/5">
                    {['24H', '7D', '30D'].map(t => (
                        <button
                            key={t}
                            onClick={() => setTimeframe(t.toLowerCase())}
                            className={`px-4 py-1.5 rounded-md text-[0.6rem] font-black uppercase tracking-widest transition-all ${timeframe === t.toLowerCase()
                                    ? 'bg-white/10 text-white shadow-inner'
                                    : 'text-slate-500 hover:text-white'
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            {/* Metric Slabs */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Slab 1: Lead Velocity */}
                <div className="glass-panel p-6 border-emerald-500/20 bg-emerald-500/[0.02] flex flex-col justify-between group hover:border-emerald-500/40 transition-all overflow-hidden relative">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TrendingUp size={64} className="text-emerald-500" />
                    </div>
                    <div className="flex justify-between items-start relative z-10">
                        <div className="text-[0.6rem] font-black text-slate-500 uppercase tracking-[0.2em]">Lead Velocity</div>
                        <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-500"><TrendingUp size={14} /></div>
                    </div>
                    <div className="relative z-10 mt-8">
                        <div className="text-4xl font-display font-black text-white tracking-tighter">{metrics.growth}</div>
                        <div className="text-[0.6rem] font-mono font-bold text-emerald-400 mt-2 flex items-center gap-1 uppercase tracking-widest">
                            <ArrowUpRight size={12} /> Trajectory: Aggressive
                        </div>
                    </div>
                </div>

                {/* Slab 2: New Targets */}
                <div className="glass-panel p-6 border-pearl/20 bg-pearl/[0.02] flex flex-col justify-between group hover:border-pearl/40 transition-all overflow-hidden relative">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Users size={64} className="text-pearl" />
                    </div>
                    <div className="flex justify-between items-start relative z-10">
                        <div className="text-[0.6rem] font-black text-slate-500 uppercase tracking-[0.2em]">Synced Nodes</div>
                        <div className="p-1.5 rounded-lg bg-pearl/10 text-pearl"><Users size={14} /></div>
                    </div>
                    <div className="relative z-10 mt-8">
                        <div className="text-4xl font-display font-black text-white tracking-tighter">{metrics.newLeads}</div>
                        <div className="text-[0.6rem] font-mono font-bold text-pearl/60 mt-2 uppercase tracking-widest">Active Verification Flow</div>
                    </div>
                </div>

                {/* Slab 3: Pipeline Health */}
                <div className="glass-panel p-6 border-amber-500/20 bg-amber-500/[0.02] flex flex-col justify-between group hover:border-amber-500/40 transition-all overflow-hidden relative">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Cpu size={64} className="text-amber-500" />
                    </div>
                    <div className="flex justify-between items-start relative z-10">
                        <div className="text-[0.6rem] font-black text-slate-500 uppercase tracking-[0.2em]">Network Load</div>
                        <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-500"><Activity size={14} /></div>
                    </div>
                    <div className="relative z-10 mt-8">
                        <div className="text-4xl font-display font-black text-white tracking-tighter">{metrics.velocity}</div>
                        <div className="text-[0.6rem] font-mono font-bold text-amber-500/60 mt-2 uppercase tracking-widest">Resource Allocation: Peak</div>
                    </div>
                </div>
            </div>

            {/* Predictive Chart Slab */}
            <div className="glass-panel p-8 bg-black/40 border border-white/5 relative overflow-hidden group">
                <div className="flex justify-between items-center mb-10">
                    <h3 className="text-xs font-display font-bold text-white uppercase tracking-[0.3em]">Neural Growth Trajectory</h3>
                    <div className="flex items-center gap-2 text-[0.6rem] font-mono text-slate-500">
                        <Globe size={12} className="animate-spin-slow" />
                        GLOBAL_SWARM_INFLUENCE_MAP
                    </div>
                </div>

                <div className="h-48 flex items-end gap-3 sm:gap-6 pb-6 relative z-10">
                    {/* Visual Bar Chart */}
                    {[45, 65, 50, 80, 75, 95, 110, 85, 100, 130, 115, 140].map((h, i) => (
                        <div key={i} className="flex-1 relative group h-full">
                            <div
                                style={{ height: `${h / 1.5}%` }}
                                className="w-full bg-gradient-to-t from-pearl/0 via-pearl/20 to-pearl/60 rounded-t-sm group-hover:via-pearl/40 group-hover:to-pearl transition-all duration-500 relative overflow-hidden border-t border-pearl/30"
                            >
                                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
                            </div>
                            {/* Hover Tooltip Peek */}
                            <div className="absolute -top-10 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-white/10 backdrop-blur-md px-2 py-1 rounded border border-white/20 text-[0.5rem] font-mono font-bold text-white z-20 pointer-events-none shadow-glow">
                                {h}%
                            </div>
                        </div>
                    ))}

                    {/* Reference Lines */}
                    <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-10">
                        <div className="border-t border-white border-dashed w-full h-[1px]"></div>
                        <div className="border-t border-white border-dashed w-full h-[1px]"></div>
                        <div className="border-t border-white border-dashed w-full h-[1px]"></div>
                    </div>
                </div>

                <div className="flex justify-between mt-4 px-2">
                    {['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI'].map((d, i) => (
                        <div key={i} className="text-[0.5rem] font-mono font-black text-slate-700 uppercase tracking-widest">{d}</div>
                    ))}
                </div>

                {/* Decorative Tech BG */}
                <div className="absolute -bottom-12 -left-12 opacity-5 pointer-events-none rotate-12">
                    <Zap size={240} strokeWidth={0.5} className="text-pearl" />
                </div>
            </div>
        </div>
    )
}
