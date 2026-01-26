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
                                    <div key={result.id} className={`glass-panel p-6 border group hover:scale-[1.02] transition-all duration-300 relative overflow-hidden ${isHot ? 'border-emerald-500/30 bg-emerald-500/[0.02]' : 'border-white/5 bg-white/[0.01]'
                                        }`}>
                                        {/* Status Glow */}
                                        <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity ${isHot ? 'text-emerald-500' : 'text-pearl'}`}>
                                            <Brain size={120} strokeWidth={0.5} className="translate-x-12 -translate-y-12" />
                                        </div>

                                        <div className="relative z-10 flex flex-col h-full">
                                            {/* Top Identity Block */}
                                            <div className="flex gap-4 items-start mb-6">
                                                <div className="relative shrink-0">
                                                    <div className="w-14 h-14 rounded-2xl bg-black/50 border border-white/10 flex items-center justify-center overflow-hidden shadow-lg">
                                                        {data.avatar_url ? (
                                                            <img src={data.avatar_url} className="w-full h-full object-cover" />
                                                        ) : (
                                                            <div className="w-full h-full bg-gradient-to-br from-slate-800 to-black flex items-center justify-center font-display font-black text-xl text-white/30">
                                                                {(data.name || "U")[0]}
                                                            </div>
                                                        )}
                                                    </div>
                                                    {result.verified && (
                                                        <div className="absolute -bottom-1 -right-1 p-1 bg-emerald-500 rounded-lg border-2 border-black">
                                                            <ShieldCheck size={10} className="text-black" />
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="min-w-0">
                                                    <h3 className="text-lg font-bold text-white leading-tight truncate group-hover:text-pearl transition-colors">
                                                        {data.name || data.company || 'REDACTED_NODE'}
                                                    </h3>
                                                    <p className="text-[0.65rem] font-mono text-slate-500 uppercase tracking-wider mt-1 truncate">
                                                        {data.title || 'Unknown Asset'}
                                                    </p>
                                                    <div className="text-[0.6rem] font-black text-white/30 truncate mt-0.5">{data.company}</div>
                                                </div>
                                            </div>

                                            {/* Info Matrix */}
                                            <div className="grid grid-cols-2 gap-2 mb-6">
                                                <div className="p-2 rounded bg-black/30 border border-white/5">
                                                    <div className="text-[0.55rem] font-bold text-slate-600 tracking-tighter mb-1 uppercase">LOC_COORDINATES</div>
                                                    <div className="text-[0.65rem] text-slate-400 font-mono truncate">{data.location || 'GLOBAL'}</div>
                                                </div>
                                                <div className="p-2 rounded bg-black/30 border border-white/5">
                                                    <div className="text-[0.55rem] font-bold text-slate-600 tracking-tighter mb-1 uppercase">SECTOR_TYPE</div>
                                                    <div className="text-[0.65rem] text-slate-400 font-mono truncate">{data.industry || 'PRIVATE'}</div>
                                                </div>
                                            </div>

                                            <div className="flex-1"></div>

                                            {/* Oracle Signal Ribbon */}
                                            {result.oracle_signal && result.oracle_signal !== 'Baseline' && (
                                                <div className="mb-6 p-3 bg-pearl/5 border-l-2 border-pearl rounded-r text-[0.65rem] font-mono text-pearl/80 italic leading-relaxed">
                                                    "{result.oracle_signal}"
                                                </div>
                                            )}

                                            {/* Footer Metrics */}
                                            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                                <div className="flex flex-col">
                                                    <span className="text-[0.5rem] font-black text-slate-600 uppercase tracking-widest">INTENT_LEVEL</span>
                                                    <span className={`text-lg font-display font-black leading-none mt-1 ${isHot ? 'text-emerald-500' : 'text-amber-500'}`}>
                                                        {result.intent_score}%
                                                    </span>
                                                </div>
                                                <div className="flex gap-2">
                                                    {data.linkedin_url && (
                                                        <a href={data.linkedin_url} target="_blank" className="p-2 rounded-lg bg-white/5 border border-white/10 text-slate-500 hover:text-pearl transition-colors">
                                                            <Linkedin size={14} />
                                                        </a>
                                                    )}
                                                    <button className="p-2 rounded-lg bg-white/5 border border-white/5 text-slate-500 hover:text-white transition-colors">
                                                        <Mail size={14} />
                                                    </button>
                                                </div>
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
