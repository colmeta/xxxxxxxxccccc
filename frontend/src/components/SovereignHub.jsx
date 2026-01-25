import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Users, AlertTriangle, Zap, Activity, TrendingUp, DollarSign, Database, Share2, Twitter, Linkedin } from 'lucide-react'

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
        <div className="animate-fade-in space-y-8">
            {/* STATS HUD */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-6 text-center">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Unified Identities</div>
                    <div className="text-3xl font-black text-pearl">{stats.total_sovereign}</div>
                </div>
                <div className="glass-panel p-6 text-center">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Velocity Alerts</div>
                    <div className="text-3xl font-black text-amber-500">{stats.growth_leads}</div>
                </div>
                <div className="glass-panel p-6 text-center">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Displacement Ready</div>
                    <div className="text-3xl font-black text-emerald-500">{stats.displacements}</div>
                </div>
            </div>

            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-black text-white tracking-tight">
                    🧠 THE <span className="text-pearl">SOVEREIGN</span> NETWORK
                </h2>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest hidden sm:block">
                    Auto-Linking Active • Multi-Node Swarm Synced
                </div>
            </div>

            {/* Phase 12: Eternal Forge HUD */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-6 border-l-4 border-l-blue-500">
                    <div className="text-[0.65rem] font-bold text-slate-500 uppercase tracking-widest mb-2">Autonomous Heart</div>
                    <div className="text-lg font-black text-white">PEARL-01 DEBATE</div>
                    <div className="text-xs font-bold text-emerald-500 mt-2 flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500"></span> CRITIQUE SYSTEM ACTIVE
                    </div>
                </div>
                <div className="glass-panel p-6 border-l-4 border-l-emerald-500">
                    <div className="text-[0.65rem] font-bold text-slate-500 uppercase tracking-widest mb-2">Auto-Warmer</div>
                    <div className="text-lg font-black text-white">ACTIVE SCOUTING</div>
                    <div className="text-xs text-slate-400 mt-2">Drafting Viral Leaks @ 300s</div>
                </div>
                <div className="glass-panel p-6 border-l-4 border-l-amber-500">
                    <div className="text-[0.65rem] font-bold text-slate-500 uppercase tracking-widest mb-2">Monetization</div>
                    <div className="text-lg font-black text-white">FLUTTERWAVE DRAFT</div>
                    <div className="text-xs font-bold text-amber-500 mt-2 flex items-center gap-1">
                        <Zap size={12} /> READY FOR ACTIVATION
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="py-20 text-center text-slate-500 animate-pulse font-mono text-xs tracking-widest">
                    SYNCING MEGA-PROFILES...
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {profiles.map((p, i) => (
                        <div key={p.id} className="glass-panel p-8 relative overflow-hidden group">
                            {/* VELOCITY BADGE */}
                            {p.metadata?.velocity_data?.is_viral && (
                                <div className="absolute top-4 right-[-35px] bg-amber-500 text-black py-1 px-10 rotate-45 text-[0.6rem] font-black uppercase shadow-lg z-10">
                                    Viral Growth
                                </div>
                            )}

                            <div className="flex gap-6 items-start">
                                {/* AVATAR */}
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pearl to-secondary flex items-center justify-center text-2xl font-black text-black shrink-0">
                                    {p.full_name?.[0] || 'P'}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <h3 className="text-xl font-black text-white truncate">{p.full_name || 'Anonymous Asset'}</h3>
                                    <div className="text-sm text-slate-400 mb-2 truncate">
                                        {p.title} <span className="text-slate-600">@</span> <span className="text-slate-200 font-bold">{p.company}</span>
                                    </div>

                                    {/* PLATFORM LINKS */}
                                    <div className="flex gap-3 mt-3 opacity-60">
                                        {p.linkedin_url && <Linkedin size={14} />}
                                        {p.twitter_handle && <Twitter size={14} />}
                                        {/* Placeholders for others using generic icons if needed */}
                                    </div>
                                </div>
                            </div>

                            {/* KINETIC VELOCITY HUD */}
                            <div className="mt-6 p-4 bg-white/5 rounded-xl border border-white/5">
                                <div className="flex justify-between text-[0.65rem] font-bold uppercase tracking-widest text-slate-500 mb-2">
                                    <span>Growth Velocity</span>
                                    <span className="text-amber-500">{p.metadata?.velocity_data?.scaling_signal || 'Steady'}</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-pearl to-amber-500"
                                        style={{ width: `${Math.min(p.metadata?.velocity_data?.growth_rate_pct || 10, 100)}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* DISPLACEMENT INTELLIGENCE */}
                            {p.metadata?.displacement_data?.sovereign_script && (
                                <div className="mt-6">
                                    <div className="text-xs font-bold text-emerald-500 mb-2 flex items-center gap-1">
                                        <Zap size={12} /> DISPLACEMENT OPPORTUNITY
                                    </div>
                                    <div className="p-4 bg-emerald-500/5 border-l-2 border-emerald-500 text-xs italic text-slate-400 leading-relaxed rounded-r-lg">
                                        "{p.metadata.displacement_data.sovereign_script.substring(0, 120)}..."
                                    </div>
                                    <button
                                        className="btn-primary w-full mt-4 text-xs py-2"
                                        onClick={() => alert(`FULL DISPLACEMENT SCRIPT:\n\n${p.metadata.displacement_data.sovereign_script}`)}
                                    >
                                        DEPLOY SOVEREIGN SCRIPT
                                    </button>
                                </div>
                            )}

                            <div className="flex gap-2 mt-4">
                                <button
                                    onClick={async () => {
                                        if (window.confirm(`Inject ${p.full_name} into your connected CRM?`)) {
                                            const { data: { session } } = await supabase.auth.getSession()
                                            await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                body: JSON.stringify({ vault_id: p.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                            })
                                            alert("Injection Successful.")
                                        }
                                    }}
                                    className="flex-1 btn-ghost border border-white/10 text-[0.65rem] py-2"
                                >
                                    <Database size={12} className="mr-1" /> SYNC CRM
                                </button>
                                <button className="px-3 py-2 rounded-lg border border-white/5 text-slate-500 hover:text-white hover:bg-white/5 text-[0.65rem] font-bold font-mono transition-all">
                                    ID: {p.sovereign_id?.substring(0, 8)}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
