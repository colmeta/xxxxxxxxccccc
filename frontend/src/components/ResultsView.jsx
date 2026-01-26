import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import AnalyticsDashboard from './AnalyticsDashboard'
import { Download, RefreshCw, Mail, Database, CheckCircle, Smartphone, Linkedin, Globe, ShieldCheck, Zap, Activity, Cpu } from 'lucide-react'

export default function ResultsView() {
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        fetchResults()
    }, [])

    const fetchResults = async () => {
        setLoading(true)
        const { data, error } = await supabase
            .from('results')
            .select(`
                *,
                jobs ( target_query, target_platform )
            `)
            .order('created_at', { ascending: false })
            .limit(100)

        if (!error && data) {
            setResults(data)
        }
        setLoading(false)
    }

    const downloadResultsAsCSV = () => {
        if (results.length === 0) return

        const headers = ["Name", "Title", "Company", "Industry", "Location", "Email", "Clarity Score", "Intent Score", "LinkedIn", "Status"]
        const csvRows = [headers.join(",")]

        results.forEach(res => {
            const data = res.data_payload || {}
            const row = [
                `"${(data.name || "").replace(/"/g, '""')}"`,
                `"${(data.title || "").replace(/"/g, '""')}"`,
                `"${(data.company || "").replace(/"/g, '""')}"`,
                `"${(data.industry || "General").replace(/"/g, '""')}"`,
                `"${(data.location || "USA").replace(/"/g, '""')}"`,
                `"${data.email || ""}"`,
                res.clarity_score || 0,
                res.intent_score || 0,
                `"${data.source_url || ""}"`,
                res.verified ? "Verified" : "Partial"
            ]
            csvRows.push(row.join(","))
        })

        const csvContent = csvRows.join("\n")
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.setAttribute("href", url)
        link.setAttribute("download", `clarity_pearl_export_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const handleOutreach = async (lead) => {
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/outreach/send/${lead.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    platform: 'email',
                    draft_id: 'default',
                    custom_message: "Hi there, I noticed your profile and wanted to connect."
                })
            })

            const data = await response.json()
            if (!response.ok) throw new Error(data.error || 'Outreach failed')

            alert(`Outreach ${data.status === 'sent' ? 'Sent' : 'Queued'}.`)
            fetchResults()
        } catch (error) {
            console.error('Outreach error:', error)
            alert(error.message || 'Failed to initiate outreach.')
        }
    }

    return (
        <div className="space-y-8 animate-slide-up">
            {/* TOP ANALYTICS STRIP */}
            <AnalyticsDashboard />

            {/* THE VAULT CONTAINER */}
            <div className="glass-panel min-h-[600px] flex flex-col relative overflow-hidden group border-pearl/10 shadow-[inner_0_0_40px_rgba(0,0,0,0.4)]">

                {/* Holographic Header */}
                <div className="flex flex-col md:flex-row justify-between items-center p-8 border-b border-white/5 bg-black/20 backdrop-blur-sm relative z-10">
                    <div>
                        <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                            SENSORY <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">VAULT</span>
                        </h2>
                        <div className="text-[0.6rem] font-mono text-pearl/50 mt-2 uppercase tracking-[0.4em] flex items-center gap-2">
                            <ShieldCheck size={12} className="text-pearl" />
                            <span>LEVEL 4 CLEARANCE ACCESS GRANTED</span>
                        </div>
                    </div>

                    <div className="flex gap-4 mt-6 md:mt-0">
                        <button
                            onClick={downloadResultsAsCSV}
                            className="btn-ghost text-[0.65rem] py-2 px-5 border-white/10 hover:border-pearl/30 hover:bg-white/5 text-slate-400 hover:text-white font-mono tracking-widest transition-all"
                            disabled={results.length === 0}
                        >
                            <Download size={14} className="mr-2" /> EXPORT_CSV
                        </button>
                        <button
                            onClick={fetchResults}
                            className="bg-pearl text-black font-display font-bold py-2 px-6 rounded-lg text-xs tracking-widest hover:shadow-neon hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                            disabled={loading}
                        >
                            {loading ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                            SYNC_RESOURCES
                        </button>
                    </div>
                </div>

                {/* DATA SLABS VIEWPORT */}
                <div className="flex-1 p-6 overflow-y-auto custom-scrollbar relative z-10">

                    {results.length === 0 && !loading ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-6 py-24">
                            <div className="relative">
                                <div className="absolute -inset-8 bg-pearl/10 blur-3xl rounded-full animate-pulse-slow"></div>
                                <Database size={80} className="text-slate-800 relative z-10" strokeWidth={1} />
                            </div>
                            <div className="text-center space-y-2">
                                <p className="text-xl tracking-widest font-display text-white/30 uppercase leading-none">The Vault is Silent</p>
                                <p className="text-xs opacity-40 font-mono text-pearl">Initialize a mission in the Nexus to secure intelligence.</p>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                            {results.map((r) => (
                                <div key={r.id} className="p-0 bg-white/[0.02] rounded-xl border border-white/5 hover:border-pearl/30 hover:bg-white/[0.04] transition-all duration-300 group/slab relative overflow-hidden flex flex-col sm:flex-row group animate-slide-up">

                                    {/* Sidebar Status Strip */}
                                    <div className={`w-1 transition-all duration-500 ${r.clarity_score > 80 ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-amber-500 shadow-[0_0_10px_#f59e0b]'}`}></div>

                                    {/* Content Wrapper */}
                                    <div className="p-5 flex-1 flex flex-col sm:flex-row gap-6 items-start">

                                        {/* Identity Section */}
                                        <div className="flex gap-4 items-start min-w-[240px]">
                                            <div className="relative">
                                                <div className="w-14 h-14 rounded-xl bg-black border border-white/10 flex items-center justify-center overflow-hidden shadow-2xl relative z-10">
                                                    {r.data_payload?.avatar_url ? (
                                                        <img src={r.data_payload.avatar_url} className="w-full h-full object-cover group-hover/slab:scale-110 transition-transform duration-500" />
                                                    ) : (
                                                        <span className="text-2xl font-display font-black text-white/50">{(r.data_payload?.name || "X")[0]}</span>
                                                    )}
                                                </div>
                                                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-black z-20 flex items-center justify-center">
                                                    <CheckCircle size={8} className="text-black" />
                                                </div>
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="text-lg font-bold text-white group-hover/slab:text-pearl transition-colors leading-tight">
                                                    {r.data_payload?.name || 'REDACTED_IDENTITY'}
                                                </h3>
                                                <p className="text-xs text-slate-400 font-mono mt-1 line-clamp-1">{r.data_payload?.title || 'Unknown Rank'}</p>
                                                <div className="mt-2 text-[0.6rem] font-black text-white/30 uppercase tracking-[0.2em]">{r.data_payload?.company}</div>
                                            </div>
                                        </div>

                                        {/* Contact Slab */}
                                        <div className="flex-1 grid grid-cols-1 gap-1.5 min-w-[180px]">
                                            <div className="flex items-center gap-3 text-xs group/link">
                                                <div className="p-1.5 rounded bg-white/5 text-slate-600 group-hover/link:text-emerald-500 transition-colors">
                                                    <Mail size={12} />
                                                </div>
                                                <span className="text-slate-400 font-mono truncate max-w-[150px]">{r.data_payload?.email || 'OFFLINE'}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-xs group/link">
                                                <div className="p-1.5 rounded bg-white/5 text-slate-600 group-hover/link:text-pearl transition-colors">
                                                    <Linkedin size={12} />
                                                </div>
                                                <span className="text-slate-400 font-mono truncate max-w-[150px]">{r.data_payload?.linkedin_url?.split('/').pop() || 'N/A'}</span>
                                            </div>
                                        </div>

                                        {/* Metrics Slab */}
                                        <div className="flex flex-col gap-4 w-full sm:w-auto sm:min-w-[160px] text-right">
                                            <div className="flex flex-col items-end gap-1">
                                                <div className="flex justify-between w-full text-[0.6rem] font-black text-slate-500 uppercase tracking-widest">
                                                    <span>CLARITY</span>
                                                    <span className={r.clarity_score > 80 ? 'text-emerald-500' : 'text-amber-500'}>{r.clarity_score}%</span>
                                                </div>
                                                <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full transition-all duration-1000 ${r.clarity_score > 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                                                        style={{ width: `${r.clarity_score}%` }}
                                                    ></div>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center bg-black/40 rounded px-2 py-1.5 border border-white/5">
                                                <span className="text-[0.6rem] font-bold text-slate-600 uppercase tracking-widest">INTENT</span>
                                                <div className="flex items-center gap-1.5">
                                                    <Zap size={10} className={r.intent_score > 70 ? 'text-pearl' : 'text-slate-700'} />
                                                    <span className="text-xs font-mono font-bold text-white">{r.intent_score}%</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Action Bar */}
                                        <div className="flex flex-wrap sm:flex-col gap-2 w-full sm:w-auto">
                                            <button
                                                onClick={() => handleOutreach(r)}
                                                className="flex-1 py-1.5 px-4 bg-white/5 border border-white/10 rounded-lg text-[0.65rem] font-bold uppercase tracking-widest text-slate-400 hover:bg-emerald-500 hover:text-black hover:border-emerald-500 hover:shadow-neon transition-all duration-300"
                                            >
                                                INIT_COMM
                                            </button>
                                            <button
                                                onClick={async () => {
                                                    const { data: { session } } = await supabase.auth.getSession()
                                                    await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                        method: 'POST',
                                                        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                        body: JSON.stringify({ vault_id: r.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                                    })
                                                    alert("RESOURCE LOGGED")
                                                }}
                                                className="flex-1 py-1.5 px-4 bg-white/5 border border-white/10 rounded-lg text-[0.65rem] font-bold uppercase tracking-widest text-slate-400 hover:bg-pearl/20 hover:text-pearl hover:border-pearl/40 transition-all duration-300"
                                            >
                                                VAULT_SYNC
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Ambient Decorative Elements */}
                <div className="absolute bottom-0 right-0 p-8 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                    <Cpu size={240} strokeWidth={0.5} className="text-pearl" />
                </div>
            </div>
        </div>
    )
}
