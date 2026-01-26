import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import VelocityView from './VelocityView'
import DisplacementLibrary from './DisplacementLibrary'
import { Brain, Download, Filter, User, MapPin, Factory, Linkedin, Mail, CheckCircle, TrendingUp, Zap, Grid, Activity, ShieldCheck, Cpu } from 'lucide-react'

export default function IntelligenceView({ session }) {
    const [viewMode, setViewMode] = useState('grid') // 'grid', 'velocity', 'scripts'
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // 'all', 'high-intent', 'verified'

    useEffect(() => {
        if (viewMode === 'grid') {
            loadIntelligence()
        }
    }, [filter, viewMode])

    const loadIntelligence = async () => {
        setLoading(true)
        try {
            let query = supabase
                .from('results')
                .select(`
                    *,
                    jobs!inner(target_query, target_platform, user_id, org_id)
                `)
                .eq('jobs.user_id', session.user.id)
                .order('created_at', { ascending: false })
                .limit(50)

            if (filter === 'high-intent') {
                query = query.gte('intent_score', 80)
            } else if (filter === 'verified') {
                query = query.eq('verified', true)
            }

            const { data, error } = await query
            if (error) throw error
            setResults(data || [])
        } catch (error) {
            console.error('Intelligence load error:', error)
        } finally {
            setLoading(false)
        }
    }

    const downloadIntelligenceAsCSV = () => {
        if (results.length === 0) return
        const headers = ["Name", "Title", "Company", "Industry", "Location", "Email", "LinkedIn", "Intent Score", "Oracle Signal", "Clarity Score", "Velocity"]
        const csvRows = [headers.join(",")]
        results.forEach(res => {
            const data = res.data_payload || {}
            const velocity = res.velocity_data || {}
            csvRows.push([
                `"${(data.name || "").replace(/"/g, '""')}"`,
                `"${(data.title || "").replace(/"/g, '""')}"`,
                `"${(data.company || "").replace(/"/g, '""')}"`,
                `"${(data.industry || "General").replace(/"/g, '""')}"`,
                `"${(data.location || "USA").replace(/"/g, '""')}"`,
                `"${data.email || ""}"`,
                `"${(data.linkedin_url || "").replace(/"/g, '""')}"`,
                res.intent_score || 0,
                `"${(res.oracle_signal || "").replace(/"/g, '""')}"`,
                res.clarity_score || 0,
                `"${velocity.scaling_signal || "Steady"}"`
            ].join(","))
        })
        const blob = new Blob([csvRows.join("\n")], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = `clarity_pearl_intelligence_${new Date().toISOString().split('T')[0]}.csv`
        link.click()
    }

    return (
        <div className="space-y-6 animate-slide-up">

            {/* TACTICAL SUB-NAV */}
            <div className="flex justify-center">
                <div className="bg-black/40 backdrop-blur-xl p-1 rounded-xl border border-white/5 flex gap-1 shadow-[0_0_30px_rgba(0,0,0,0.5)]">
                    {[
                        { id: 'grid', label: 'NEURAL GRID', icon: Grid },
                        { id: 'velocity', label: 'TRAJECTORY', icon: Activity },
                        { id: 'scripts', label: 'DISPLACEMENT', icon: Zap },
                    ].map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setViewMode(item.id)}
                            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-[0.65rem] font-display font-black tracking-widest transition-all duration-300 ${viewMode === item.id
                                ? 'bg-pearl text-black shadow-neon scale-105 active:scale-95'
                                : 'text-slate-500 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <item.icon size={14} />
                            {item.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* VIEW CONTENT */}
            {viewMode === 'grid' && (
                <div className="space-y-6">
                    {/* Header Controls */}
                    <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-white/5 pb-6">
                        <div className="space-y-1">
                            <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                                INTELLIGENCE <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">LATTICE</span>
                            </h2>
                            <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                                <ShieldCheck size={12} className="text-pearl" />
                                <span>CROSS-LAYER VALIDATION ACTIVE // {results.length} NODES IDENTIFIED</span>
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <div className="flex bg-black/40 rounded-lg p-1 border border-white/5">
                                {['all', 'high-intent', 'verified'].map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setFilter(f)}
                                        className={`px-4 py-1.5 rounded-md text-[0.6rem] font-black uppercase tracking-widest transition-all ${filter === f
                                            ? 'bg-white/10 text-white shadow-inner'
                                            : 'text-slate-500 hover:text-slate-400'
                                            }`}
                                    >
                                        {f.replace('-', '_')}
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={downloadIntelligenceAsCSV}
                                className="px-4 py-1.5 border border-white/10 rounded-lg text-[0.6rem] font-black tracking-widest text-slate-500 hover:text-white hover:border-pearl/30 transition-all uppercase"
                            >
                                <Download size={12} className="inline mr-2" /> EXPORT_LATTICE
                            </button>
                        </div>
                    </div>

                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {[1, 2, 3, 4, 5, 6].map(i => (
                                <div key={i} className="h-64 glass-panel bg-white/[0.02] border-white/5 animate-pulse relative overflow-hidden">
                                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent"></div>
                                </div>
                            ))}
                        </div>
                    ) : results.length === 0 ? (
                        <div className="py-32 flex flex-col items-center justify-center gap-6 border border-dashed border-white/5 rounded-3xl bg-black/20">
                            <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center text-slate-700">
                                <Cpu size={40} strokeWidth={1} />
                            </div>
                            <div className="text-center">
                                <p className="text-lg font-display font-black text-slate-500 tracking-[0.2em] uppercase">No Intelligence Secured</p>
                                <p className="text-[0.65rem] font-mono text-slate-600 mt-2">Adjust filters or initialize a sweep in Mission Control.</p>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {results.map(result => {
                                const data = result.data_payload || {}
                                const isHot = result.intent_score >= 80

                                return (
                                    <div key={result.id} className={`glass-panel p-0 border group hover:-translate-y-2 transition-all duration-500 relative overflow-hidden flex flex-col ${isHot ? 'border-emerald-500/30' : 'border-white/5 shadow-glass'}`}>

                                        {/* Card Header (Profile Stripe) */}
                                        <div className={`h-24 bg-gradient-to-br from-white/5 to-transparent relative overflow-hidden p-6 ${isHot ? 'bg-emerald-500/5' : ''}`}>
                                            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                                                <Brain size={80} strokeWidth={0.5} className="rotate-12" />
                                            </div>
                                            <div className="relative z-10 flex gap-4">
                                                <div className="w-12 h-12 rounded-xl bg-black/60 border border-white/10 flex items-center justify-center text-lg font-black text-white shadow-lg backdrop-blur-sm group-hover:border-pearl/40 transition-all">
                                                    {(data.name || 'X')[0]}
                                                </div>
                                                <div className="min-w-0">
                                                    <h3 className="text-lg font-bold text-white leading-tight group-hover:text-pearl transition-colors truncate">{data.name || 'REDACTED'}</h3>
                                                    <div className="text-[0.6rem] text-slate-400 font-mono mt-0.5 truncate uppercase tracking-widest">{data.company || 'UNKNOWN_CORP'}</div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Card Body - Intel Slab */}
                                        <div className="p-6 flex-1 flex flex-col gap-5 border-t border-white/5 bg-black/20">

                                            {/* CONTACT HUD */}
                                            <div className="flex flex-col gap-1.5 p-3.5 rounded-2xl bg-black/40 border border-white/5 group-hover:border-pearl/20 transition-all duration-500 shadow-inner">
                                                <div className="flex items-center justify-between text-[0.7rem] font-mono">
                                                    <div className="flex items-center gap-3 text-emerald-400 font-bold">
                                                        <Mail size={12} />
                                                        <span className="truncate max-w-[120px]">{data.email || 'OFFLINE'}</span>
                                                    </div>
                                                </div>
                                                <div className="h-px bg-white/5 w-full"></div>
                                                <div className="flex items-center justify-between text-[0.7rem] font-mono">
                                                    <div className="flex items-center gap-3 text-pearl font-bold">
                                                        <Smartphone size={12} />
                                                        <span className="truncate max-w-[120px]">{data.phone || 'N/A'}</span>
                                                    </div>
                                                </div>
                                                <div className="h-px bg-white/5 w-full"></div>
                                                <div className="flex items-center justify-between text-[0.7rem] font-mono">
                                                    <div className="flex items-center gap-3 text-amber-400 font-bold">
                                                        <Globe size={12} />
                                                        <span className="truncate max-w-[120px]">{data.location || 'GLOBAL'}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Intent Gauge */}
                                            <div className="space-y-1.5 px-1">
                                                <div className="flex justify-between text-[0.6rem] font-black uppercase tracking-widest text-slate-500">
                                                    <span>INTENT_VELOCITY</span>
                                                    <span className={isHot ? 'text-emerald-500' : 'text-amber-500'}>{result.intent_score}%</span>
                                                </div>
                                                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full transition-all duration-1000 ${isHot ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-amber-500 shadow-[0_0_10px_#f59e0b]'}`}
                                                        style={{ width: `${result.intent_score}%` }}
                                                    ></div>
                                                </div>
                                            </div>

                                            <div className="flex-1"></div>

                                            {/* Actions */}
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => data.linkedin_url && window.open(data.linkedin_url, '_blank')}
                                                    className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-pearl/10 border border-white/10 hover:border-pearl/30 text-[0.6rem] font-black tracking-[0.2em] text-slate-400 hover:text-pearl transition-all uppercase flex items-center justify-center gap-2"
                                                >
                                                    <Linkedin size={10} /> SEARCH_PROFILE
                                                </button>
                                                <button className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-emerald-500/10 border border-white/10 hover:border-emerald-500/30 text-[0.6rem] font-black tracking-[0.2em] text-slate-400 hover:text-emerald-500 transition-all uppercase flex items-center justify-center gap-2">
                                                    <CheckCircle size={10} /> VERIFY
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            )}

            {viewMode === 'velocity' && <VelocityView />}
            {viewMode === 'scripts' && <DisplacementLibrary />}
        </div>
    )
}
