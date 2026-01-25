import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import AnalyticsDashboard from './AnalyticsDashboard'
import { Download, RefreshCw, Mail, Database, CheckCircle, Smartphone, Linkedin, Globe, AlertTriangle } from 'lucide-react'

export default function ResultsView() {
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(false)
    const [expandedRows, setExpandedRows] = useState(new Set())

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
                    draft_id: 'default', // Force default template
                    custom_message: "Hi there, I noticed your profile and wanted to connect."
                })
            })

            const data = await response.json()
            if (!response.ok) throw new Error(data.error || 'Outreach failed')

            alert(`Outreach ${data.status === 'sent' ? 'Sent' : 'Queued'}. (Provider: ${data.provider})`)
            fetchResults()
        } catch (error) {
            console.error('Outreach error:', error)
            alert(error.message || 'Failed to initiate outreach.')
        }
    }

    return (
        <div className="mt-8">
            <AnalyticsDashboard />

            <div className="glass-panel p-8 mt-8">
                {/* Header Actions */}
                <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                    <h2 className="text-2xl font-black flex items-center gap-3">
                        <span className="text-pearl text-3xl">💎</span>
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            SALES INTELLIGENCE VAULT
                        </span>
                    </h2>

                    <div className="flex gap-3">
                        <button
                            onClick={downloadResultsAsCSV}
                            className="btn-ghost text-xs"
                            disabled={results.length === 0}
                        >
                            <Download size={14} /> CSV EXPORT
                        </button>
                        <button
                            onClick={fetchResults}
                            className="btn-primary text-xs py-2 px-4 shadow-glow"
                            disabled={loading}
                        >
                            {loading ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                            REFRESH DATA
                        </button>
                    </div>
                </div>

                {/* DESKTOP TABLE View */}
                <div className="hidden lg:block overflow-x-auto rounded-xl border border-white/5 bg-slate-900/40">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-white/5 text-slate-400 uppercase tracking-wider text-xs font-bold">
                            <tr>
                                <th className="p-4">Lead Persona</th>
                                <th className="p-4">Direct Contact</th>
                                <th className="p-4">Clarity Score</th>
                                <th className="p-4">Oracle Signal</th>
                                <th className="p-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {results.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="p-16 text-center text-slate-500">
                                        {loading ? 'Decrypting Intelligence...' : 'The Vault is empty. Launch a Mission in Mission Control.'}
                                    </td>
                                </tr>
                            ) : (
                                results.map((r) => (
                                    <tr key={r.id} className="hover:bg-white/5 transition-colors group">
                                        <td className="p-4">
                                            <div className="flex items-center gap-4">
                                                <div className="relative">
                                                    {r.data_payload?.avatar_url ? (
                                                        <img src={r.data_payload.avatar_url} alt="" className="w-10 h-10 rounded-lg object-cover ring-1 ring-white/10" />
                                                    ) : (
                                                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center font-black text-pearl ring-1 ring-white/10">
                                                            {(r.data_payload?.name || "U")[0]}
                                                        </div>
                                                    )}
                                                </div>
                                                <div>
                                                    <div className="font-bold text-white group-hover:text-pearl transition-colors">
                                                        {r.data_payload?.name || 'Unknown Asset'}
                                                    </div>
                                                    <div className="text-xs text-slate-400 flex items-center gap-2">
                                                        {r.data_payload?.title || 'No Title'}
                                                    </div>
                                                    <div className="text-[0.65rem] uppercase tracking-wide text-slate-500 mt-1">
                                                        {r.data_payload?.company}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>

                                        <td className="p-4">
                                            <div className="flex flex-col gap-1.5">
                                                {/* Email */}
                                                {r.data_payload?.email || r.data_payload?.decision_maker_email ? (
                                                    <a href={`mailto:${r.data_payload.decision_maker_email || r.data_payload.email}`}
                                                        className="flex items-center gap-2 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors">
                                                        <Mail size={12} />
                                                        {r.data_payload.decision_maker_email || r.data_payload.email}
                                                    </a>
                                                ) : <span className="text-xs text-slate-600 italic">No Email</span>}

                                                {/* Phone */}
                                                {(r.data_payload?.phones?.[0] || r.data_payload?.phone) && (
                                                    <a href={`tel:${r.data_payload.phone || r.data_payload.phones[0]}`}
                                                        className="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors">
                                                        <Smartphone size={12} />
                                                        {r.data_payload.phone || r.data_payload.phones[0]}
                                                    </a>
                                                )}

                                                {/* Socials */}
                                                <div className="flex gap-2 mt-1">
                                                    {r.data_payload?.linkedin_url && (
                                                        <a href={r.data_payload.linkedin_url} target="_blank" className="text-blue-400 hover:text-blue-300">
                                                            <Linkedin size={12} />
                                                        </a>
                                                    )}
                                                    {r.data_payload?.website && (
                                                        <a href={r.data_payload.website} target="_blank" className="text-slate-400 hover:text-white">
                                                            <Globe size={12} />
                                                        </a>
                                                    )}
                                                </div>
                                            </div>
                                        </td>

                                        <td className="p-4">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-2">
                                                    <div className="h-1.5 w-16 bg-slate-800 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full ${r.clarity_score > 80 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]' : 'bg-amber-500'}`}
                                                            style={{ width: `${r.clarity_score || 0}%` }}
                                                        ></div>
                                                    </div>
                                                    <span className={`text-xs font-black ${r.clarity_score > 80 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                                        {r.clarity_score || 0}%
                                                    </span>
                                                </div>
                                                {r.verified && (
                                                    <span className="text-[0.6rem] font-bold text-emerald-500 flex items-center gap-1">
                                                        <CheckCircle size={8} /> VERIFIED
                                                    </span>
                                                )}
                                            </div>
                                        </td>

                                        <td className="p-4">
                                            {r.intent_score > 50 ? (
                                                <div className="badge badge-pearl flex items-center gap-1 w-fit">
                                                    <span className="animate-pulse">●</span> {r.intent_score}% INTENT
                                                </div>
                                            ) : (
                                                <span className="text-xs text-slate-600">Stable Baseline</span>
                                            )}
                                        </td>

                                        <td className="p-4 text-right">
                                            <div className="flex flex-col items-end gap-2">
                                                <button
                                                    onClick={() => handleOutreach(r)}
                                                    className="btn-primary py-1.5 px-3 text-[0.65rem] rounded-lg w-fit"
                                                >
                                                    INITIATE CONTACT
                                                </button>
                                                <button
                                                    onClick={async () => {
                                                        const { data: { session } } = await supabase.auth.getSession()
                                                        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                            method: 'POST',
                                                            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                            body: JSON.stringify({ vault_id: r.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                                        })
                                                        if (res.ok) alert("Log Entry Created in Database.")
                                                    }}
                                                    className="btn-ghost py-1 px-3 text-[0.65rem] rounded-lg w-fit border-white/5 hover:border-white/20"
                                                    title="Simulate CRM Sync"
                                                >
                                                    <Database size={10} className="mr-1" /> LOG TO DB
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* MOBILE CARD View (Visible on small screens) */}
                <div className="lg:hidden flex flex-col gap-4">
                    {results.length === 0 ? (
                        <div className="text-center p-8 text-slate-500 text-sm">No data available. Switch to Desktop for analytics.</div>
                    ) : (
                        results.map((r) => (
                            <div key={r.id} className="bg-slate-800/50 p-4 rounded-xl border border-white/5 space-y-4">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        {r.data_payload?.avatar_url ? (
                                            <img src={r.data_payload.avatar_url} className="w-12 h-12 rounded-lg object-cover" />
                                        ) : (
                                            <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center text-xl">👤</div>
                                        )}
                                        <div>
                                            <div className="font-bold text-white">{r.data_payload?.name}</div>
                                            <div className="text-xs text-slate-400">{r.data_payload?.company}</div>
                                        </div>
                                    </div>
                                    <div className={`text-lg font-black ${r.clarity_score > 80 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                        {r.clarity_score}%
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-2">
                                    <button
                                        onClick={() => handleOutreach(r)}
                                        className="btn-primary py-2 text-xs"
                                    >
                                        CONTACT
                                    </button>
                                    <button
                                        onClick={() => alert("Simulated DB Sync.")}
                                        className="btn-ghost py-2 text-xs border border-white/10"
                                    >
                                        LOG DB
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
