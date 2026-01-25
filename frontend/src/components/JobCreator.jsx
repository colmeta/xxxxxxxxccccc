import React, { useState } from 'react'
import { supabase } from '../lib/supabase'
import { Rocket, Zap, Target, Search, X } from 'lucide-react'

export default function JobCreator({ session, onClose }) {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [platform, setPlatform] = useState('linkedin')
    const [boostMode, setBoostMode] = useState(false)

    const platforms = [
        { id: 'linkedin', label: 'LinkedIn', icon: '👔' },
        { id: 'google_news', label: 'News', icon: '📡' },
        { id: 'real_estate', label: 'Real Estate', icon: '🏠' },
        { id: 'reddit', label: 'Reddit', icon: '🗨️' },
        { id: 'google_maps', label: 'Maps', icon: '📍' }
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

            if (!response.ok) throw new Error('Mission Rejected')

            onClose && onClose()
            alert('Mission Launched Successfully 🚀')
        } catch (error) {
            alert(error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
            <div className="glass-panel w-full max-w-2xl p-0 overflow-hidden relative">
                {/* Header */}
                <div className="p-6 border-b border-white/5 flex justify-between items-center bg-slate-900/50">
                    <div>
                        <h2 className="text-lg font-black text-white flex items-center gap-2">
                            <Target className="text-pearl" size={20} /> ADVANCED MISSION LAUNCHER
                        </h2>
                        <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mt-1">Manual Override Control</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <X size={20} className="text-slate-400" />
                    </button>
                </div>

                <div className="p-8 space-y-8">
                    {/* Platform Select */}
                    <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 block">Target Frequency</label>
                        <div className="flex flex-wrap gap-2">
                            {platforms.map(p => (
                                <button
                                    key={p.id}
                                    onClick={() => setPlatform(p.id)}
                                    className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${platform === p.id
                                            ? 'bg-pearl text-black shadow-glow scale-105'
                                            : 'bg-white/5 text-slate-400 hover:bg-white/10'
                                        }`}
                                >
                                    <span>{p.icon}</span> {p.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Query Input */}
                    <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 block">Mission Parameters</label>
                        <div className="relative">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="e.g. 'CTOs in Fintech Series A'"
                                className="w-full bg-slate-950/50 border border-white/10 rounded-xl px-5 py-4 text-white placeholder-slate-600 focus:outline-none focus:border-pearl focus:ring-1 focus:ring-pearl transition-all font-medium"
                            />
                            <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-600" size={20} />
                        </div>
                    </div>

                    {/* Boost Toggle */}
                    <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/5">
                        <div className={`p-2 rounded-lg ${boostMode ? 'bg-amber-500/20 text-amber-500' : 'bg-slate-800 text-slate-600'}`}>
                            <Zap size={20} fill={boostMode ? "currentColor" : "none"} />
                        </div>
                        <div className="flex-1">
                            <div className="text-sm font-bold text-white">Priority Boost</div>
                            <div className="text-xs text-slate-400">Allocates 10x worker nodes for speed.</div>
                        </div>
                        <button
                            onClick={() => setBoostMode(!boostMode)}
                            className={`w-12 h-6 rounded-full p-1 transition-colors ${boostMode ? 'bg-amber-500' : 'bg-slate-700'}`}
                        >
                            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${boostMode ? 'translate-x-6' : 'translate-x-0'}`} />
                        </button>
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={loading || !query}
                        className="btn-primary w-full py-4 text-sm tracking-widest shadow-lg"
                    >
                        {loading ? 'INITIALIZING...' : 'LAUNCH MISSION'}
                    </button>
                </div>
            </div>
        </div>
    )
}
