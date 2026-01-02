import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

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

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/outreach/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    target_emails: [lead.data_payload?.email],
                    subject: `Strategic Inquiry: ${lead.data_payload?.company || 'Your Organization'}`,
                    body_template: `Hello ${lead.data_payload?.name || 'there'},\n\nI noticed your work at ${lead.data_payload?.company || 'your company'} and wanted to reach out regarding a strategic opportunity.\n\nBest regards,\n[Clarity Intel Agent]`,
                    sender_identity: "agent@claritypearl.com",
                    service_provider: "smtp",
                    api_key: "REAL_KEY_FROM_ENV" // Backend should handle this
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Outreach failed')
            }

            alert('Outreach sequence initiated.')
        } catch (error) {
            console.error('Outreach error:', error)
            alert(error.message || 'Failed to initiate outreach.')
        }
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 className="text-gradient" style={{ margin: 0, fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>💎</span> ACQUIRED INTEL
                </h2>
                <button
                    onClick={fetchResults}
                    className="btn-primary"
                    disabled={loading}
                    style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.75rem',
                        background: 'transparent',
                        border: '1px solid var(--primary)',
                        color: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}
                >
                    {loading ? <div className="spinner" style={{ width: '10px', height: '10px' }}></div> : 'REFRESH'}
                </button>
            </div>

            <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                        <tr style={{ background: 'rgba(2, 6, 23, 0.5)', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                            <th style={{ padding: '1rem', fontWeight: 600 }}>SOURCE QUERY</th>
                            <th style={{ padding: '1rem', fontWeight: 600 }}>PAYLOAD</th>
                            <th style={{ padding: '1rem', fontWeight: 600 }}>CLARITY SCORE</th>
                            <th style={{ padding: '1rem', fontWeight: 600 }}>STATUS</th>
                            <th style={{ padding: '1rem', fontWeight: 600 }}>ACTION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results.length === 0 ? (
                            <tr>
                                <td colSpan="4" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    {loading ? (
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                                            <div className="spinner"></div> Scanning DataVault...
                                        </div>
                                    ) : (
                                        'No intelligence gathered yet.'
                                    )}
                                </td>
                            </tr>
                        ) : (
                            results.map((r, i) => (
                                <tr key={r.id} className="animate-slide-up" style={{
                                    borderBottom: '1px solid var(--border-subtle)',
                                    animationDelay: `${i * 0.05}s`,
                                    background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'
                                }}>
                                    <td style={{ padding: '1rem', color: 'var(--secondary)', fontWeight: 500 }}>
                                        {r.jobs?.target_query || 'Unknown'}
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{
                                            background: '#0f172a',
                                            padding: '0.5rem',
                                            borderRadius: '4px',
                                            fontFamily: 'monospace',
                                            fontSize: '0.75rem',
                                            whiteSpace: 'pre-wrap',
                                            maxHeight: '100px',
                                            overflowY: 'auto',
                                            border: '1px solid var(--border-subtle)'
                                        }}>
                                            {JSON.stringify(r.data, null, 2)}
                                        </div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <div style={{
                                                width: '40px',
                                                height: '4px',
                                                background: 'rgba(255,255,255,0.1)',
                                                borderRadius: '2px',
                                                overflow: 'hidden'
                                            }}>
                                                <div style={{
                                                    width: `${r.clarity_score || 0}%`,
                                                    height: '100%',
                                                    background: (r.clarity_score || 0) > 70 ? 'var(--primary)' : 'var(--secondary)'
                                                }}></div>
                                            </div>
                                            <span style={{ fontSize: '0.75rem', fontWeight: 'bold' }}>{r.clarity_score || 0}%</span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        {r.verified ? (
                                            <span className="status-badge status-completed">VERIFIED</span>
                                        ) : (
                                            <span className="status-badge status-running">PENDING</span>
                                        )}
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <button
                                            className="btn-primary"
                                            style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem' }}
                                            onClick={() => handleOutreach(r)}
                                        >
                                            OUTREACH
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
