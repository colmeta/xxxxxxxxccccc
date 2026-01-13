import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import AnalyticsDashboard from './AnalyticsDashboard'

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

    const toggleRow = (id) => {
        const newExpanded = new Set(expandedRows)
        if (newExpanded.has(id)) {
            newExpanded.delete(id)
        } else {
            newExpanded.add(id)
        }
        setExpandedRows(newExpanded)
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
                    draft_id: 'default', // Force default template on backend
                    custom_message: "Hi there, I noticed your profile and wanted to connect." // Fallback message
                })
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
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
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

                {/* Desktop View */}
                <div style={{ display: 'none' }} className="desktop-table">
                    <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-xl)', border: '1px solid var(--glass-border)' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                            <thead>
                                <tr style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'rgba(255,255,255,0.9)', borderBottom: '1px solid var(--glass-border)' }}>
                                    <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>LEAD INFORMATION</th>
                                    <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>CONTACT</th>
                                    <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>AI SCORE</th>
                                    <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>ORACLE</th>
                                    <th style={{ padding: '1.25rem 1rem', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '1px' }}>ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" style={{ padding: '4rem', textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                                            {loading ? (
                                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                                                    <div className="spinner"></div> LOADING INTELLIGENCE...
                                                </div>
                                            ) : (
                                                'The Vault is empty. Launch a Mission in the SOVEREIGN tab to begin.'
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
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                                    <div style={{ fontWeight: 800, color: '#fff', fontSize: '1.05rem' }}>
                                                        {r.data_payload?.name || r.data_payload?.full_name || 'Unknown'}
                                                    </div>
                                                    <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.85rem' }}>
                                                        {r.data_payload?.title || 'No Title'}
                                                    </div>
                                                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem' }}>
                                                        {r.data_payload?.company || 'No Company'}
                                                    </div>
                                                    {r.is_high_intent && (
                                                        <span style={{
                                                            fontSize: '0.65rem',
                                                            color: 'hsl(var(--pearl-warning))',
                                                            fontWeight: 900,
                                                            background: 'rgba(245, 158, 11, 0.2)',
                                                            padding: '4px 8px',
                                                            borderRadius: '6px',
                                                            border: '1px solid hsla(var(--pearl-warning), 0.4)',
                                                            width: 'fit-content'
                                                        }}>
                                                            🔥 HIGH INTENT
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            <td style={{ padding: '1.25rem 1rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                                                    {r.data_payload?.email && (
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem' }}>
                                                            <span style={{ opacity: 0.6 }}>📧</span>
                                                            <a href={`mailto:${r.data_payload.email}`} style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none' }}>
                                                                {r.data_payload.email}
                                                            </a>
                                                        </div>
                                                    )}
                                                    {r.data_payload?.phone && (
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem' }}>
                                                            <span style={{ opacity: 0.6 }}>📞</span>
                                                            <a href={`tel:${r.data_payload.phone}`} style={{ color: 'rgba(255,255,255,0.9)', textDecoration: 'none' }}>
                                                                {r.data_payload.phone}
                                                            </a>
                                                        </div>
                                                    )}
                                                    {r.data_payload?.linkedin_url && (
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem' }}>
                                                            <span style={{ opacity: 0.6 }}>💼</span>
                                                            <a href={r.data_payload.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none' }}>
                                                                LinkedIn Profile
                                                            </a>
                                                        </div>
                                                    )}
                                                    {!r.data_payload?.email && !r.data_payload?.phone && !r.data_payload?.linkedin_url && (
                                                        <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: '0.75rem', fontStyle: 'italic' }}>
                                                            No contact info available
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                            <td style={{ padding: '1.25rem 1rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                        <div style={{
                                                            flex: 1,
                                                            height: '8px',
                                                            background: 'rgba(255,255,255,0.05)',
                                                            borderRadius: '4px',
                                                            overflow: 'hidden',
                                                            minWidth: '80px'
                                                        }}>
                                                            <div style={{
                                                                width: `${r.clarity_score || 0}%`,
                                                                height: '100%',
                                                                background: (r.clarity_score || 0) > 80
                                                                    ? 'linear-gradient(90deg, hsl(var(--pearl-success)), hsl(var(--pearl-primary)))'
                                                                    : 'linear-gradient(90deg, hsl(var(--pearl-warning)), hsl(var(--pearl-primary)))',
                                                                boxShadow: '0 0 10px rgba(6, 182, 212, 0.4)'
                                                            }}></div>
                                                        </div>
                                                        <span style={{ fontSize: '0.9rem', fontWeight: 800, color: (r.clarity_score || 0) > 80 ? 'var(--success)' : '#fff', minWidth: '45px' }}>
                                                            {r.clarity_score || 0}%
                                                        </span>
                                                    </div>
                                                    {r.verified && (
                                                        <span style={{ fontSize: '0.65rem', color: 'hsl(var(--pearl-success))', fontWeight: 700 }}>
                                                            ✓ VERIFIED
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            <td style={{ padding: '1.25rem 1rem' }}>
                                                {r.oracle_signal && r.oracle_signal !== 'Baseline' ? (
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                                        <span style={{
                                                            fontSize: '0.7rem',
                                                            fontWeight: 900,
                                                            color: r.intent_score > 70 ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.6)',
                                                            letterSpacing: '0.5px'
                                                        }}>
                                                            🔮 {r.oracle_signal.toUpperCase()}
                                                        </span>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                            <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.5)' }}>{r.intent_score}% INTENT</span>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)' }}>STABLE</span>
                                                )}
                                            </td>
                                            <td style={{ padding: '1rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                                    <button
                                                        className="btn-primary"
                                                        style={{ padding: '0.4rem 0.9rem', fontSize: '0.7rem', fontWeight: 800 }}
                                                        onClick={() => handleOutreach(r)}
                                                    >
                                                        📧 OUTREACH
                                                    </button>
                                                    <button
                                                        className="btn-ghost"
                                                        style={{ padding: '0.4rem 0.9rem', fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                                                        onClick={async () => {
                                                            const { data: { session } } = await supabase.auth.getSession()
                                                            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                                method: 'POST',
                                                                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                                body: JSON.stringify({ vault_id: r.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                                            })
                                                            if (res.ok) alert("Intelligence synced to CRM!")
                                                        }}
                                                    >
                                                        🎯 PUSH TO CRM
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

                {/* Mobile Card View */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }} className="mobile-cards">
                    {results.length === 0 ? (
                        <div style={{ padding: '4rem 1rem', textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                            {loading ? 'LOADING...' : 'No results yet. Create a mission to begin!'}
                        </div>
                    ) : (
                        results.map((r, i) => (
                            <div key={r.id} className="glass-panel" style={{
                                padding: '1.5rem',
                                border: '1px solid rgba(255,255,255,0.08)',
                                borderRadius: '16px',
                                animation: `fadeIn 0.3s ease-out ${i * 0.05}s both`
                            }}>
                                {/* Lead Name & Company */}
                                <div style={{ marginBottom: '1rem' }}>
                                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff', marginBottom: '0.4rem' }}>
                                        {r.data_payload?.name || r.data_payload?.full_name || 'Unknown'}
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.3rem' }}>
                                        {r.data_payload?.title || 'No Title'}
                                    </div>
                                    <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)' }}>
                                        {r.data_payload?.company || 'No Company'}
                                    </div>
                                </div>

                                {/* Contact Info */}
                                <div style={{ marginBottom: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.5)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                                        Contact Information
                                    </div>
                                    {r.data_payload?.email && (
                                        <div style={{ marginBottom: '0.5rem' }}>
                                            <a href={`mailto:${r.data_payload.email}`} style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none', fontSize: '0.9rem' }}>
                                                📧 {r.data_payload.email}
                                            </a>
                                        </div>
                                    )}
                                    {r.data_payload?.phone && (
                                        <div style={{ marginBottom: '0.5rem' }}>
                                            <a href={`tel:${r.data_payload.phone}`} style={{ color: 'rgba(255,255,255,0.9)', textDecoration: 'none', fontSize: '0.9rem' }}>
                                                📞 {r.data_payload.phone}
                                            </a>
                                        </div>
                                    )}
                                    {r.data_payload?.linkedin_url && (
                                        <div>
                                            <a href={r.data_payload.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none', fontSize: '0.9rem' }}>
                                                💼 View LinkedIn
                                            </a>
                                        </div>
                                    )}
                                </div>

                                {/* Scores */}
                                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.3rem' }}>AI SCORE</div>
                                        <div style={{ fontSize: '1.2rem', fontWeight: 800, color: (r.clarity_score || 0) > 80 ? 'var(--success)' : '#fff' }}>
                                            {r.clarity_score || 0}%
                                        </div>
                                    </div>
                                    {r.intent_score > 0 && (
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.3rem' }}>INTENT</div>
                                            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'hsl(var(--pearl-primary))' }}>
                                                {r.intent_score}%
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                    <button
                                        className="btn-primary"
                                        style={{ flex: 1, padding: '0.7rem', fontSize: '0.75rem', fontWeight: 800, minWidth: '120px' }}
                                        onClick={() => handleOutreach(r)}
                                    >
                                        📧 OUTREACH
                                    </button>
                                    <button
                                        className="btn-ghost"
                                        style={{ flex: 1, padding: '0.7rem', fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', minWidth: '120px' }}
                                        onClick={async () => {
                                            const { data: { session } } = await supabase.auth.getSession()
                                            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session?.access_token}` },
                                                body: JSON.stringify({ vault_id: r.id, crm_type: 'hubspot', api_key: 'DEMO' })
                                            })
                                            if (res.ok) alert("Synced to CRM!")
                                        }}
                                    >
                                        🎯 CRM
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <style>{`
                @media (min-width: 1024px) {
                    .desktop-table { display: block !important; }
                    .mobile-cards { display: none !important; }
                }
                @media (max-width: 1023px) {
                    .desktop-table { display: none !important; }
                    .mobile-cards { display: flex !important; }
                }
            `}</style>
        </div>
    )
}
