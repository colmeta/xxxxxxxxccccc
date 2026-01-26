import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Folder, Database, Download, CheckCircle2, Calendar, Target, ChevronRight, Activity, Filter, RefreshCw, Zap, Mail, Smartphone, Globe, Linkedin } from 'lucide-react'

export default function JobSeparatedResults() {
    const [jobGroups, setJobGroups] = useState([])
    const [loading, setLoading] = useState(false)
    const [selectedCategory, setSelectedCategory] = useState('all')
    const [categories, setCategories] = useState([])

    useEffect(() => {
        fetchJobGroups()
        fetchCategories()
    }, [selectedCategory])

    const fetchCategories = async () => {
        const { data } = await supabase
            .from('jobs')
            .select('category')
            .not('category', 'is', null)

        if (data) {
            const uniqueCategories = [...new Set(data.map(j => j.category).filter(Boolean))]
            setCategories(uniqueCategories.sort())
        }
    }

    const fetchJobGroups = async () => {
        setLoading(true)
        let query = supabase
            .from('jobs')
            .select(`id, target_query, category, target_platform, created_at, result_count, delivery_metadata`)
            .order('created_at', { ascending: false })
            .limit(20)

        if (selectedCategory !== 'all') {
            query = query.eq('category', selectedCategory)
        }

        const { data: jobs } = await query
        if (jobs) {
            const jobsWithResults = await Promise.all(
                jobs.map(async (job) => {
                    const { data: results } = await supabase
                        .from('results')
                        .select('*')
                        .eq('job_id', job.id)
                        .order('clarity_score', { ascending: false })
                        .limit(50)
                    return { ...job, results: results || [] }
                })
            )
            setJobGroups(jobsWithResults.filter(j => j.results.length > 0))
        }
        setLoading(false)
    }

    const exportJobCSV = (job) => {
        const headers = ["Name", "Title", "Company", "Email", "Phone", "Location", "LinkedIn", "Lead Score"]
        const csvRows = [headers.join(",")]
        job.results.forEach(r => {
            const data = r.data_payload || {}
            const row = [
                `"${(data.name || "").replace(/"/g, '""')}"`,
                `"${(data.title || "").replace(/"/g, '""')}"`,
                `"${(data.company || "").replace(/"/g, '""')}"`,
                `"${data.email || ""}"`,
                `"${data.phone || ""}"`,
                `"${data.location || ""}"`,
                `"${data.linkedin_url || ""}"`,
                r.clarity_score || 0
            ]
            csvRows.push(row.join(","))
        })
        const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = `${job.category || 'export'}_${Date.now()}.csv`
        link.click()
    }

    return (
        <div className="space-y-8 animate-slide-up">

            {/* Header HUD */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-pearl/10 pb-8">
                <div className="space-y-1">
                    <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                        DATA <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">SETS</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Database size={12} className="text-pearl" />
                        <span>STRUCTURED_INTEL_VAULT // QUANTIZED_LEAD_GROUPS</span>
                    </div>
                </div>

                <div className="flex gap-4">
                    <div className="relative group/select">
                        <Filter className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-700 group-hover/select:text-pearl transition-colors" size={14} />
                        <select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            className="bg-black/60 border border-white/5 rounded-xl pl-10 pr-10 py-2.5 font-mono text-[0.65rem] text-pearl outline-none focus:border-pearl/40 cursor-pointer appearance-none uppercase tracking-widest"
                        >
                            <option value="all">ALL_CATEGORIES</option>
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat.toUpperCase()}</option>
                            ))}
                        </select>
                    </div>

                    <button onClick={fetchJobGroups} className="p-2.5 bg-white/5 border border-white/10 rounded-xl text-pearl hover:bg-pearl hover:text-black transition-all group">
                        <RefreshCw size={16} className={loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'} />
                    </button>
                </div>
            </div>

            {/* Job Grid */}
            <div className="space-y-6">
                {jobGroups.map((job, idx) => (
                    <div key={job.id} className="glass-panel p-8 bg-black/40 border-white/5 hover:border-pearl/20 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                            <Folder size={120} strokeWidth={0.5} className="text-pearl" />
                        </div>

                        {/* Slab Header */}
                        <div className="flex flex-col lg:flex-row justify-between items-start gap-6 border-b border-white/5 pb-6 mb-8">
                            <div className="space-y-1">
                                <div className="text-xl font-display font-black text-white tracking-widest uppercase">
                                    {job.category || job.target_query}
                                </div>
                                <div className="flex items-center gap-4 text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">
                                    <span className="flex items-center gap-1"><Calendar size={10} /> {new Date(job.created_at).toLocaleDateString()}</span>
                                    <span className="flex items-center gap-1"><Zap size={10} className="text-pearl" /> {job.results.length} NODES</span>
                                    <span className="flex items-center gap-1"><Target size={10} /> {job.target_platform.toUpperCase()}</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => exportJobCSV(job)}
                                    className="px-6 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[0.65rem] font-black tracking-widest text-slate-400 hover:text-pearl hover:border-pearl/40 hover:bg-pearl/5 transition-all flex items-center gap-2 uppercase"
                                >
                                    <Download size={14} /> EXPORT_CSV
                                </button>
                                {job.delivery_metadata?.delivered_at && (
                                    <div className="px-4 py-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-[0.65rem] font-black text-emerald-500 tracking-widest uppercase flex items-center gap-2">
                                        <CheckCircle2 size={14} /> DELIVERED
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Preview HUD - Intelligence Slabs */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {job.results.slice(0, 50).map(r => (
                                <div key={r.id} className="p-5 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-pearl/40 hover:bg-white/[0.06] transition-all duration-500 group/item flex flex-col justify-between relative overflow-hidden backdrop-blur-md">
                                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover/item:opacity-30 transition-opacity">
                                        <Zap size={40} className="text-pearl" />
                                    </div>

                                    <div className="relative z-10">
                                        <div className="text-[0.8rem] font-black text-white group-hover/item:text-pearl transition-colors truncate mb-1 flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
                                            {r.data_payload?.name || 'NODE_UNNAMED'}
                                        </div>
                                        <div className="text-[0.6rem] font-mono text-slate-500 truncate uppercase tracking-widest mb-4">
                                            {r.data_payload?.title || 'CLASS_NULL'}
                                        </div>

                                        {/* READABLE CONTACT INTEL */}
                                        <div className="space-y-2 mb-4 bg-black/40 p-3 rounded-xl border border-white/5">
                                            <div className="flex items-center gap-3 text-[0.65rem] text-slate-300">
                                                <div className="p-1 rounded bg-pearl/10 text-pearl"><Mail size={10} /></div>
                                                <span className="truncate font-mono">{r.data_payload?.email || 'OFFLINE'}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-[0.65rem] text-slate-300">
                                                <div className="p-1 rounded bg-blue-500/10 text-blue-400"><Smartphone size={10} /></div>
                                                <span className="truncate font-mono">{r.data_payload?.phone || 'N/A'}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-[0.65rem] text-slate-300">
                                                <div className="p-1 rounded bg-amber-500/10 text-amber-400"><Globe size={10} /></div>
                                                <span className="truncate font-mono">{r.data_payload?.location || 'Unknown'}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex justify-between items-center bg-black/60 p-2.5 rounded-xl border border-white/10 relative z-10 mt-auto">
                                        <div className="flex items-center gap-2">
                                            <div className="text-[0.5rem] font-black text-slate-600 uppercase tracking-widest">CLARITY</div>
                                            <div className={`text-[0.7rem] font-mono font-black ${r.clarity_score > 80 ? 'text-emerald-500' : 'text-pearl'}`}>
                                                {r.clarity_score}%
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => window.open(r.data_payload?.linkedin_url || r.data_payload?.source_url, '_blank')}
                                            className="p-1.5 rounded bg-white/5 text-slate-500 hover:text-pearl hover:bg-white/10 transition-all"
                                        >
                                            <Linkedin size={12} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {job.results.length > 6 && (
                            <div className="mt-6 flex justify-center">
                                <div className="text-[0.55rem] font-mono text-slate-700 uppercase tracking-[0.4em] flex items-center gap-2">
                                    <Activity size={10} /> +{job.results.length - 6} OVERFLOW_NODES_IN_VAULT
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {jobGroups.length === 0 && !loading && (
                <div className="h-[400px] flex flex-col items-center justify-center gap-6 opacity-20">
                    <Database size={64} strokeWidth={1} />
                    <div className="text-[0.7rem] font-mono tracking-[0.5em] uppercase text-center">
                        NO_STRUCTURED_DATA_DETECTED // <br />
                        INITIALIZE_ORACLE_SWEEP_TO_POPULATE
                    </div>
                </div>
            )}
        </div>
    )
}
