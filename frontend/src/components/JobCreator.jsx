import React, { useState } from 'react'
import { supabase } from '../lib/supabase'
import { Rocket, Zap, Target, Search, X, Activity, Cpu, Globe, ShieldAlert } from 'lucide-react'

export default function JobCreator({ session, onClose }) {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [platform, setPlatform] = useState('linkedin')
    const [boostMode, setBoostMode] = useState(false)

    const platforms = [
        { id: 'linkedin', label: 'LINKEDIN_CORE', icon: Globe },
        { id: 'google_news', label: 'NEWS_FEED', icon: Activity },
        { id: 'real_estate', label: 'ASSET_RADAR', icon: Target },
        { id: 'reddit', label: 'SOCIAL_INTEL', icon: Cpu },
        { id: 'google_maps', label: 'GEOSPATIAL', icon: Globe }
    ]

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!query.trim()) return

        setLoading(true)
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/jobs/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: query,
                    platform: platform,
                    compliance_mode: boostMode ? 'strict' : 'standard',
                    priority: boostMode ? 10 : 1,
                    search_metadata: { source: 'advanced_modal' }
                })
            })

            if (!response.ok) throw new Error('MISSION_REJECTED: Unauthorized or insufficient credits.')

            onClose && onClose()
            alert('MISSION_LAUNCHED: Global swarm engaged.')
        } catch (error) {
            alert(error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center p-6 bg-black/95 backdrop-blur-xl animate-fade-in">
            {/* Ambient Background Content */}
            <div className="absolute inset-0 bg-hero-pattern opacity-10 animate-pulse-slow"></div>

            <div className="glass-panel w-full max-w-2xl p-0 overflow-hidden relative border-pearl/20 shadow-glow-sm">
                {/* Status Bar */}
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-pearl/40 to-transparent"></div>

                {/* Header HUD */}
                <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                    <div className="space-y-1">
                        <h2 className="text-xl font-display font-black text-white tracking-widest flex items-center gap-3">
                            <Target className="text-pearl animate-pulse" size={24} />
                            MISSION <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">LAUNCHER</span>
                        </h2>
                        <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-[0.3em]">
                            <Cpu size={12} />
                            <span>MANUAL_OVERRIDE_ACTIVE // FREQ: {platform.toUpperCase()}</span>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-xl transition-all group">
                        <X size={20} className="text-slate-600 group-hover:text-white transition-colors" />
                    </button>
                </div>

                <div className="p-10 space-y-10">

                    {/* Platform Selection */}
                    <div className="space-y-4">
                        <div className="text-[0.6rem] font-mono font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            INPUT_TARGET_SOURCE
                            <div className="h-px flex-1 bg-white/5"></div>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            {platforms.map(p => (
                                <button
                                    key={p.id}
                                    onClick={() => setPlatform(p.id)}
                                    className={`px-4 py-2.5 rounded-xl text-[0.6rem] font-black tracking-widest flex items-center gap-3 transition-all border ${platform === p.id
                                            ? 'bg-pearl border-pearl text-black shadow-neon scale-105'
                                            : 'bg-white/5 border-white/5 text-slate-500 hover:border-white/20 hover:text-white'
                                        }`}
                                >
                                    <p.icon size={14} /> {p.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Query Terminal */}
                    <div className="space-y-4">
                        <div className="text-[0.6rem] font-mono font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            DEFINE_MISSION_QUERY
                            <div className="h-px flex-1 bg-white/5"></div>
                        </div>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                <Search size={18} className="text-slate-700 group-focus-within:text-pearl transition-colors" />
                            </div>
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="e.g. 'CTOs in Fintech Series A'..."
                                className="w-full bg-black/60 border border-white/10 rounded-2xl pl-14 pr-6 py-5 text-sm font-mono text-pearl focus:border-pearl/40 outline-none transition-all placeholder:text-slate-800"
                            />
                        </div>
                    </div>

                    {/* Boost Protocol Toggle */}
                    <div
                        onClick={() => setBoostMode(!boostMode)}
                        className={`p-6 rounded-2xl border cursor-pointer transition-all duration-300 flex items-center gap-6 group/boost ${boostMode
                                ? 'bg-amber-500/10 border-amber-500/40 shadow-[0_0_20px_rgba(245,158,11,0.1)]'
                                : 'bg-white/[0.02] border-white/5 hover:border-white/10'
                            }`}
                    >
                        <div className={`p-4 rounded-xl transition-all ${boostMode ? 'bg-amber-500 text-black shadow-glow' : 'bg-slate-800 text-slate-600'
                            }`}>
                            <Zap size={24} fill={boostMode ? "black" : "none"} strokeWidth={boostMode ? 2 : 1} />
                        </div>
                        <div className="flex-1">
                            <div className="text-xs font-display font-black text-white tracking-widest uppercase mb-1">PRIORITY_BOOST_PROTOCOL</div>
                            <div className="text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">ALLOCATE 10X WORKER NODES // REDUCED STEALTH</div>
                        </div>
                        <div className={`w-12 h-6 rounded-full p-1 transition-colors relative ${boostMode ? 'bg-amber-500' : 'bg-slate-700'}`}>
                            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${boostMode ? 'translate-x-6' : 'translate-x-0'}`} />
                        </div>
                    </div>

                    {/* Launch Action */}
                    <button
                        onClick={handleSubmit}
                        disabled={loading || !query}
                        className="w-full bg-white text-black font-display font-black py-5 rounded-2xl text-[0.7rem] tracking-[0.5em] hover:shadow-neon hover:scale-[1.02] transition-all flex items-center justify-center gap-4 disabled:opacity-30 group"
                    >
                        {loading ? (
                            <Activity size={20} className="animate-spin" />
                        ) : (
                            <>
                                <Rocket size={20} className="group-hover:-translate-y-1 transition-transform" />
                                LAUNCH_GLOBAL_MISSION
                            </>
                        )}
                    </button>

                    {/* Compliance Hint */}
                    <div className="flex items-center justify-center gap-2 text-[0.5rem] font-mono text-slate-700 uppercase tracking-widest">
                        <ShieldAlert size={10} />
                        BY RELAUNCHING, YOU ADHERE TO SOVEREIGN DATA COMPLIANCE PROTOCOLS
                    </div>
                </div>
            </div>
        </div>
    )
}
