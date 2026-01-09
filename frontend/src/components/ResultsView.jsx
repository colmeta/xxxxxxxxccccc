import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import AnalyticsDashboard from './AnalyticsDashboard'

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
                jobs ( target_query )
            `)
            .order('created_at', { ascending: false })
            .limit(50)

        if (!error && data) {
            setResults(data)
        }
        setLoading(false)
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
                }
            })

            const data = await response.json()
            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Outreach failed')
            }

            alert(`Outreach ${data.status === 'sent' ? 'Sent' : 'Queued'}. Provider: ${data.provider}`)
            fetchResults() // Refresh to show status update
        } catch (error) {
            console.error('Outreach error:', error)
            alert(error.message || 'Failed to initiate outreach.')
        }
    }

    return (
        <div style={{ marginTop: '2rem' }}>
            <AnalyticsDashboard />

            <div className="supreme-glass" style={{ padding: '2.5rem', marginTop: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 800 }}>
                        <span style={{ color: 'hsl(var(--pearl-primary))' }}>💎</span> SALES INTELLIGENCE VAULT
                    </h2>
                    <button
                        onClick={fetchResults}
                        className="btn-primary"
                        disabled={loading}
                        style={{
                            padding: '0.6rem 1.2rem',
                            fontSize: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.6rem',
                            borderRadius: '12px'
                        }}
                    >
                        {loading ? <div className="spinner" style={{ width: '12px', height: '12px' }}></div> : 'REFRESH DATA'}
                    </button>
                </div>

                <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-xl)', border: '1px solid var(--glass-border)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                        <thead>
                            <tr style={{ background: 'rgba(2, 6, 23, 0.8)', color: 'var(--text-muted)', borderBottom: '1px solid var(--glass-border)' }}>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>SOURCE & QUERY</th>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>PAYLOAD</th>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>AI TRUTH SCORE</th>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>ORACLE SIGNAL</th>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>STATUS</th>
                                <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results.length === 0 ? (
                                <tr>
                                    <td colSpan="5" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                        {loading ? (
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                                                <div className="spinner"></div> ARCHIVING GLOBAL SENSORY FEED...
                                            </div>
                                        ) : (
                                            'The Vault is empty. Launch a Scout to begin.'
                                        )}
                                    </td>
                                </tr>
                            ) : (
                                results.map((r, i) => (
                                    <tr key={r.id} className="animate-slide-up" style={{
                                        borderBottom: '1px solid var(--glass-border)',
                                        animationDelay: `${i * 0.05}s`,
                                        background: i % 2 === 0 ? 'rgba(255,255,255,0.01)' : 'transparent'
                                    }}>
                                        <td style={{ padding: '1.25rem 1rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                <div style={{
                                                    padding: '4px 8px',
                                                    background: 'rgba(255,255,255,0.05)',
                                                    borderRadius: '6px',
                                                    fontSize: '0.65rem',
                                                    fontWeight: 800,
                                                    color: 'hsl(var(--pearl-primary))'
                                                }}>
                                                    {r.jobs?.target_platform?.toUpperCase() || 'WEB'}
                                                </div>
                                                <span style={{ fontWeight: 600 }}>{r.jobs?.target_query || 'Direct Scrape'}</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '1.25rem 1rem' }}>
                                            <div style={{
                                                display: 'flex',
                                                flexDirection: 'column',
                                                gap: '0.35rem'
                                            }}>
                                                <div style={{ fontWeight: 700, color: '#fff', fontSize: '1rem' }}>
                                                    {r.data_payload?.name || r.data_payload?.title || 'Unknown Asset'}
                                                </div>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    {r.data_payload?.company || r.data_payload?.author || 'No Attribution'}
                                                    {r.is_high_intent && (
                                                        <span style={{
                                                            fontSize: '0.65rem',
                                                            color: 'hsl(var(--pearl-warning))',
                                                            fontWeight: 900,
                                                            background: 'rgba(245, 158, 11, 0.1)',
                                                            padding: '2px 6px',
                                                            borderRadius: '4px',
                                                            border: '1px solid hsla(var(--pearl-warning), 0.3)'
                                                        }}>
                                                            🔥 HIGH INTENT
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ padding: '1.25rem 1rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <div style={{
                                                        flex: 1,
                                                        height: '6px',
                                                        background: 'rgba(255,255,255,0.05)',
                                                        borderRadius: '3px',
                                                        overflow: 'hidden',
                                                        minWidth: '100px'
                                                    }}>
                                                        <div style={{
                                                            width: `${r.truth_score || r.clarity_score || 0}%`,
                                                            height: '100%',
                                                            background: (r.truth_score || r.clarity_score || 0) > 80
                                                                ? 'linear-gradient(90deg, hsl(var(--pearl-primary)), hsl(var(--pearl-success)))'
                                                                : 'linear-gradient(90deg, var(--secondary), var(--primary))',
                                                            boxShadow: '0 0 10px rgba(6, 182, 212, 0.3)'
                                                        }}></div>
                                                    </div>
                                                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: (r.truth_score || r.clarity_score || 0) > 80 ? 'var(--success)' : '#fff' }}>
                                                        {r.truth_score || r.clarity_score || 0}%
                                                    </span>
                                                </div>
                                                {r.verdict && (
                                                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontStyle: 'italic', maxWidth: '200px' }}>
                                                        "{r.verdict}"
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td style={{ padding: '1.25rem 1rem' }}>
                                            {r.oracle_signal && r.oracle_signal !== 'Baseline' ? (
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                                    <span style={{
                                                        fontSize: '0.7rem',
                                                        fontWeight: 900,
                                                        color: r.intent_score > 70 ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                                                        letterSpacing: '0.5px'
                                                    }}>
                                                        🔮 {r.oracle_signal.toUpperCase()}
                                                    </span>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                        <div style={{ width: '40px', height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                                                            <div style={{ width: `${r.intent_score}%`, height: '100%', background: 'hsl(var(--pearl-primary))' }}></div>
                                                        </div>
                                                        <span style={{ fontSize: '0.6rem', opacity: 0.5 }}>{r.intent_score}% INTENT</span>
                                                    </div>
                                                </div>
                                            ) : (
                                                <span style={{ fontSize: '0.7rem', opacity: 0.2 }}>STABLE</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                                                {r.verified ? (
                                                    <span className="status-badge status-completed" style={{ fontSize: '0.6rem' }}>VERIFIED</span>
                                                ) : (
                                                    <span className="status-badge status-running" style={{ fontSize: '0.6rem' }}>PENDING</span>
                                                )}

                                                {r.outreach_status && r.outreach_status !== 'none' && (
                                                    <span style={{
                                                        fontSize: '0.6rem',
                                                        fontWeight: 900,
                                                        padding: '2px 6px',
                                                        borderRadius: '4px',
                                                        background: r.outreach_status === 'sent' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                                        color: r.outreach_status === 'sent' ? '#22c55e' : '#ef4444',
                                                        border: `1px solid ${r.outreach_status === 'sent' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                                                        textAlign: 'center'
                                                    }}>
                                                        PROMO: {r.outreach_status.toUpperCase()}
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td style={{ padding: '1rem' }}>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="btn-primary"
                                                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem' }}
                                                    onClick={() => handleOutreach(r)}
                                                >
                                                    OUTREACH
                                                </button>
                                                <button
                                                    className="btn-ghost"
                                                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                                                    onClick={async () => {
                                                        const { data: { session: currentSession } } = await supabase.auth.getSession()
                                                        const token = currentSession?.access_token
                                                        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/outreach/ghostwrite/${r.id}/`, {
                                                            method: 'POST',
                                                            headers: { 'Authorization': `Bearer ${token}` }
                                                        })
                                                        const data = await res.json()
                                                        alert(`THE GHOSTWRITER DRAFT:\n\n${data.draft}`)
                                                    }}
                                                >
                                                    ✍️ GHOSTWRITE
                                                </button>
                                                <button
                                                    className="btn-ghost"
                                                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                                                    onClick={() => {
                                                        const url = `${import.meta.env.VITE_BACKEND_URL || ''}/api/results/export/${r.job_id}/`
                                                        window.open(url, '_blank')
                                                    }}
                                                >
                                                    📁 FORGE
                                                </button>
                                                <button
                                                    className="btn-ghost"
                                                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem', color: 'hsl(var(--pearl-primary))', background: 'rgba(6, 182, 212, 0.05)', border: '1px solid rgba(6, 182, 212, 0.1)' }}
                                                    onClick={async () => {
                                                        const { data: { session } } = await supabase.auth.getSession()
                                                        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                            method: 'POST',
                                                            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                            body: JSON.stringify({ vault_id: r.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                                        })
                                                        if (res.ok) alert("Injection Successful: Intelligence synced to CRM.")
                                                    }}
                                                >
                                                    🎯 CRM
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
