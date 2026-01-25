import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import VelocityView from './VelocityView'
import DisplacementLibrary from './DisplacementLibrary'
import { Brain, Download, Filter, User, MapPin, Factory, Linkedin, Mail, CheckCircle, TrendingUp, Zap, Grid, Activity } from 'lucide-react'

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

    // CSV Export logic
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
        <div className="space-y-8 mt-4">
            {/* SUB-NAVIGATION for Intelligence Pillar */}
            <div className="flex justify-center mb-8">
                <div className="bg-slate-900/80 p-1.5 rounded-xl border border-white/10 flex gap-1 shadow-lg backdrop-blur-md">
                    <button
                        onClick={() => setViewMode('grid')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'grid' ? 'bg-pearl text-black shadow-glow' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        <Grid size={16} /> DATA GRID
                    </button>
                    <button
                        onClick={() => setViewMode('velocity')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'velocity' ? 'bg-pearl text-black shadow-glow' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        <Activity size={16} /> VELOCITY
                    </button>
                    <button
                        onClick={() => setViewMode('scripts')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'scripts' ? 'bg-pearl text-black shadow-glow' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        <Zap size={16} /> SCRIPTS
                    </button>
                </div>
            </div>

            {/* VIEW CONTENT */}
            {viewMode === 'grid' && (
                <div className="animate-slide-up">
                    <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                        <h2 className="text-xl font-black text-white flex items-center gap-3">
                            <Brain className="text-pearl" size={24} /> INTELLIGENCE GRID
                        </h2>

                        <div className="flex gap-2">
                            <button onClick={downloadIntelligenceAsCSV} className="btn-ghost text-xs border border-white/10">
                                <Download size={14} /> EXPORT
                            </button>
                            <div className="flex bg-slate-800/50 rounded-lg p-1 border border-white/5">
                                {['all', 'high-intent', 'verified'].map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setFilter(f)}
                                        className={`px-3 py-1.5 rounded-md text-[0.65rem] font-bold uppercase transition-all ${filter === f ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'
                                            }`}
                                    >
                                        {f.replace('-', ' ')}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {[1, 2, 3].map(i => <div key={i} className="h-64 glass-panel bg-white/5 animate-pulse"></div>)}
                        </div>
                    ) : results.length === 0 ? (
                        <div className="col-span-full py-12 text-center text-slate-500">
                            No intelligence data matching filters.
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-4">
                            {results.map(result => {
                                const data = result.data_payload || {}
                                const isHot = result.intent_score >= 80

                                return (
                                    <div key={result.id} className={`glass-panel p-6 border transition-all hover:bg-white/5 ${isHot ? 'border-emerald-500/30' : 'border-white/5'}`}>
                                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">

                                            {/* Profile Info */}
                                            <div className="flex items-start gap-4">
                                                <div className="relative">
                                                    {data.avatar_url ? (
                                                        <img src={data.avatar_url} className="w-12 h-12 rounded-xl object-cover ring-1 ring-white/10" />
                                                    ) : (
                                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center font-black text-lg text-pearl border border-white/10">
                                                            {(data.name || "U")[0]}
                                                        </div>
                                                    )}
                                                    {data.logo_url && <img src={data.logo_url} className="absolute -bottom-1 -right-1 w-5 h-5 rounded bg-white p-0.5 border border-slate-900" />}
                                                </div>

                                                <div>
                                                    <h3 className="text-lg font-bold text-white leading-tight">{data.name || data.company || 'Unknown Target'}</h3>
                                                    <div className="text-sm text-slate-400 mt-1 flex items-center gap-2 flex-wrap">
                                                        {data.title}
                                                        {data.company && <span className="text-slate-500">@ {data.company}</span>}
                                                    </div>
                                                    <div className="flex gap-2 mt-2">
                                                        {data.location && <span className="badge bg-white/5 text-slate-400 border-white/5 flex items-center gap-1"><MapPin size={10} /> {data.location}</span>}
                                                        {data.industry && <span className="badge bg-purple-500/10 text-purple-400 border-purple-500/20 flex items-center gap-1"><Factory size={10} /> {data.industry}</span>}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Scores */}
                                            <div className="flex items-center gap-4">
                                                <div className="text-center">
                                                    <div className="text-[0.6rem] text-slate-500 font-bold uppercase tracking-wider mb-1">INTENT</div>
                                                    <div className={`text-2xl font-black ${isHot ? 'text-emerald-400' : 'text-amber-500'}`}>{result.intent_score}</div>
                                                </div>
                                                <div className="w-px h-8 bg-white/10"></div>
                                                <div className="text-center">
                                                    <div className="text-[0.6rem] text-slate-500 font-bold uppercase tracking-wider mb-1">CLARITY</div>
                                                    <div className="text-xl font-bold text-pearl">{result.clarity_score}</div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Oracle Insight */}
                                        {result.oracle_signal && result.oracle_signal !== 'Baseline' && (
                                            <div className="mt-4 p-3 bg-purple-500/5 rounded-lg border border-purple-500/20 flex items-start gap-3">
                                                <div className="p-1 bg-purple-500/20 rounded text-purple-400"><Brain size={14} /></div>
                                                <div>
                                                    <div className="text-[0.65rem] font-bold text-purple-400 uppercase tracking-widest mb-0.5">Oracle Signal</div>
                                                    <div className="text-sm text-purple-200 font-medium">{result.oracle_signal}</div>
                                                </div>
                                            </div>
                                        )}
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
