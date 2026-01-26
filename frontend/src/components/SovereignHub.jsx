import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Users, AlertTriangle, Zap, Activity, TrendingUp, DollarSign, Database, Share2, Twitter, Linkedin, Globe, Fingerprint, Lock, ShieldCheck } from 'lucide-react'

export default function SovereignHub() {
    const [profiles, setProfiles] = useState([])
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState({ total_sovereign: 0, growth_leads: 0, displacements: 0 })

    useEffect(() => {
        fetchSovereignData()
    }, [])

    const fetchSovereignData = async () => {
        setLoading(true)
        const { data, error } = await supabase
            .from('data_vault')
            .select('*')
            .order('last_verified_at', { ascending: false })
            .limit(20)

        if (!error && data) {
            setProfiles(data)
            const growth = data.filter(p => p.metadata?.velocity_data?.is_viral).length
            const displacements = data.filter(p => p.metadata?.displacement_data?.sovereign_script).length
            setStats({
                total_sovereign: data.length,
                growth_leads: growth,
                displacements: displacements
            })
        }
        setLoading(false)
    }

    return (
        <div className="space-y-6">

            {/* TOP METRICS STRIP */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* METRIC 1 */}
                <div className="glass-panel p-4 flex items-center justify-between group hover:border-pearl/30 hover:bg-white/5">
                    <div>
                        <div className="text-[0.6rem] font-mono font-bold text-slate-500 uppercase tracking-widest mb-1 group-hover:text-pearl transition-colors">Unified Identities</div>
                        <div className="text-2xl font-display font-black text-white">{stats.total_sovereign.toLocaleString()}</div>
                    </div>
                    <div className="h-8 w-8 rounded bg-white/5 border border-white/10 flex items-center justify-center text-slate-500 group-hover:text-pearl group-hover:border-pearl/30 transition-all">
                        <Fingerprint size={16} />
                    </div>
                </div>

                {/* METRIC 2 */}
                <div className="glass-panel p-4 flex items-center justify-between group hover:border-amber-500/30 hover:bg-amber-500/5">
                    <div>
                        <div className="text-[0.6rem] font-mono font-bold text-slate-500 uppercase tracking-widest mb-1 group-hover:text-amber-500 transition-colors">Velocity Alerts</div>
                        <div className="text-2xl font-display font-black text-white">{stats.growth_leads}</div>
                    </div>
                    <div className="h-8 w-8 rounded bg-white/5 border border-white/10 flex items-center justify-center text-slate-500 group-hover:text-amber-500 group-hover:border-amber-500/30 transition-all">
                        <Activity size={16} />
                    </div>
                </div>

                {/* METRIC 3 */}
                <div className="glass-panel p-4 flex items-center justify-between group hover:border-emerald-500/30 hover:bg-emerald-500/5">
                    <div>
                        <div className="text-[0.6rem] font-mono font-bold text-slate-500 uppercase tracking-widest mb-1 group-hover:text-emerald-500 transition-colors">Displacement Ready</div>
                        <div className="text-2xl font-display font-black text-white">{stats.displacements}</div>
                    </div>
                    <div className="h-8 w-8 rounded bg-white/5 border border-white/10 flex items-center justify-center text-slate-500 group-hover:text-emerald-500 group-hover:border-emerald-500/30 transition-all">
                        <Zap size={16} />
                    </div>
                </div>

                {/* METRIC 4 - SYSTEM STATUS */}
                <div className="glass-panel p-4 flex flex-col justify-center relative overflow-hidden">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                        <div className="text-[0.6rem] font-bold text-emerald-500 tracking-widest">NETWORK: ACTIVE</div>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-emerald-500 h-full w-[85%] shadow-[0_0_10px_#10b981]"></div>
                    </div>
                </div>
            </div>

            {/* MAIN HEADER */}
            <div className="flex justify-between items-end border-b border-white/5 pb-4">
                <div>
                    <h2 className="text-3xl font-display font-black text-white tracking-wide">
                        SOVEREIGN <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">NETWORK</span>
                    </h2>
                    <div className="text-xs font-mono text-slate-500 mt-1 flex items-center gap-2">
                        <ShieldCheck size={12} className="text-pearl" />
                        <span>SECURE VAULT CONNECTION ESTABLISHED</span>
                    </div>
                </div>
            </div>

            {/* DATA GRID */}
            {loading ? (
                <div className="py-32 flex flex-col items-center justify-center gap-4">
                    <div className="w-16 h-16 border-4 border-pearl/20 border-t-pearl rounded-full animate-spin"></div>
                    <div className="text-xs font-mono text-pearl animate-pulse tracking-widest">DECRYPTING IDENTITY MATRICES...</div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    {profiles.map((p, i) => (
                        <div key={p.id} className="glass-panel p-0 flex flex-col group hover:-translate-y-1 hover:shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] transition-all duration-300">

                            {/* Card Header (Banner) */}
                            <div className="h-24 bg-gradient-to-br from-white/5 to-transparent relative overflow-hidden p-6">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <Globe size={80} strokeWidth={0.5} />
                                </div>
                                <div className="relative z-10 flex gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-black/50 border border-white/10 flex items-center justify-center text-lg font-bold text-white shadow-lg backdrop-blur-sm">
                                        {p.full_name?.[0] || 'X'}
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white leading-tight group-hover:text-pearl transition-colors">{p.full_name || 'REDACTED'}</h3>
                                        <div className="text-xs text-slate-400 font-mono mt-0.5">{p.company || 'UNKNOWN_CORP'}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Card Body */}
                            <div className="p-6 flex-1 flex flex-col gap-4 border-t border-white/5 bg-black/20">

                                <div className="grid grid-cols-2 gap-2 text-[0.65rem] font-mono text-slate-500">
                                    <div className="bg-white/5 rounded px-2 py-1.5 border border-white/5">
                                        TITLE: <span className="text-slate-300 block mt-0.5 truncate">{p.title || 'N/A'}</span>
                                    </div>
                                    <div className="bg-white/5 rounded px-2 py-1.5 border border-white/5">
                                        LOCATION: <span className="text-slate-300 block mt-0.5 truncate">{p.location || 'GLOBAL'}</span>
                                    </div>
                                    <div className="bg-white/5 rounded px-2 py-1.5 border border-white/5">
                                        EMAIL: <span className="text-emerald-500 block mt-0.5 truncate font-bold">{p.email || 'OFFLINE'}</span>
                                    </div>
                                    <div className="bg-white/5 rounded px-2 py-1.5 border border-white/5">
                                        PHONE: <span className="text-pearl block mt-0.5 truncate font-bold">{p.phone || 'N/A'}</span>
                                    </div>
                                </div>

                                {/* Velocity Bar */}
                                {p.metadata?.velocity_data && (
                                    <div className="space-y-1">
                                        <div className="flex justify-between text-[0.6rem] font-bold uppercase tracking-wider text-slate-500">
                                            <span>MOMENTUM</span>
                                            <span className="text-amber-500">{p.metadata.velocity_data.growth_rate_pct}%</span>
                                        </div>
                                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-pearl to-amber-500 shadow-[0_0_10px_#f59e0b]"
                                                style={{ width: `${Math.min(p.metadata.velocity_data.growth_rate_pct || 10, 100)}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                )}

                                {/* Intelligence Snippet */}
                                {p.metadata?.displacement_data?.sovereign_script && (
                                    <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg text-[0.6rem] text-slate-400 italic leading-relaxed relative overflow-hidden group/intel">
                                        <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
                                        "{p.metadata.displacement_data.sovereign_script.substring(0, 80)}..."
                                    </div>
                                )}

                                <div className="flex-1"></div>

                                {/* Actions */}
                                <div className="flex gap-2 mt-2">
                                    <button
                                        className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-pearl/10 border border-white/10 hover:border-pearl/30 text-[0.65rem] font-bold tracking-wider text-slate-300 hover:text-pearl transition-all uppercase flex items-center justify-center gap-2 group/btn"
                                        onClick={() => window.open(p.linkedin_url, '_blank')}
                                    >
                                        <Linkedin size={12} /> PROFILE
                                    </button>
                                    <button
                                        className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-emerald-500/10 border border-white/10 hover:border-emerald-500/30 text-[0.65rem] font-bold tracking-wider text-slate-300 hover:text-emerald-400 transition-all uppercase flex items-center justify-center gap-2"
                                    >
                                        <Database size={12} /> SYNC
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
