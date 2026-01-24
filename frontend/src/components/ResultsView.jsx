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
                    <div style={{ display: 'flex', gap: '0.8rem' }}>
                        <button
                            onClick={downloadResultsAsCSV}
                            className="btn-secondary"
                            style={{
                                padding: '0.6rem 1.2rem',
                                fontSize: '0.75rem',
                                borderRadius: '12px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                color: 'rgba(255,255,255,0.6)',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                                fontWeight: 600
                            }}
                        >
                            DOWNLOAD CSV
                        </button>
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
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                    <div style={{ position: 'relative' }}>
                                                        {r.data_payload?.avatar_url ? (
                                                            <img
                                                                src={r.data_payload.avatar_url}
                                                                alt={r.data_payload.name}
                                                                style={{ width: '36px', height: '36px', borderRadius: '8px', objectFit: 'cover', border: '1px solid var(--glass-border)' }}
                                                            />
                                                        ) : (
                                                            <div style={{
                                                                width: '36px',
                                                                height: '36px',
                                                                borderRadius: '8px',
                                                                background: 'linear-gradient(135deg, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))',
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                fontSize: '0.75rem',
                                                                fontWeight: 900,
                                                                color: '#000'
                                                            }}>
                                                                {(r.data_payload?.name || "U")[0].toUpperCase()}
                                                            </div>
                                                        )}
                                                        {r.data_payload?.logo_url && (
                                                            <img
                                                                src={r.data_payload.logo_url}
                                                                alt="Company"
                                                                style={{
                                                                    position: 'absolute',
                                                                    bottom: '-3px',
                                                                    right: '-3px',
                                                                    width: '14px',
                                                                    height: '14px',
                                                                    borderRadius: '3px',
                                                                    background: '#fff',
                                                                    border: '1px solid var(--glass-border)',
                                                                    padding: '1px'
                                                                }}
                                                            />
                                                        )}
                                                    </div>
                                                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                        <div style={{ fontWeight: 800, color: '#fff', fontSize: '1rem' }}>
                                                            {r.data_payload?.name || r.data_payload?.full_name || 'Unknown'}
                                                        </div>
                                                        <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                                            {r.data_payload?.title || 'No Title'}
                                                            {r.data_payload?.location && <span style={{ opacity: 0.6 }}>• 📍 {r.data_payload.location}</span>}
                                                            {r.data_payload?.industry && <span style={{ opacity: 0.6 }}>• 🏭 {r.data_payload.industry}</span>}
                                                        </div>
                                                    </div>
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
                                            </td>
                                            <td style={{ padding: '1.25rem 1rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                                                    {/* Decision Maker Email */}
                                                    {r.data_payload?.decision_maker_email && (
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                                                            <span style={{ opacity: 0.6 }}>👤</span>
                                                            <a href={`mailto:${r.data_payload.decision_maker_email}`} style={{ color: 'hsl(var(--pearl-success))', fontWeight: 'bold', textDecoration: 'none' }}>
                                                                {r.data_payload.decision_maker_email}
                                                            </a>
                                                        </div>
                                                    )}

                                                    {/* Generic Emails */}
                                                    {(r.data_payload?.emails || (r.data_payload?.email ? [r.data_payload.email] : [])).slice(0, 3).map((email, i) => (
                                                        email !== r.data_payload?.decision_maker_email && (
                                                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                                                                <span style={{ opacity: 0.6 }}>📧</span>
                                                                <a href={`mailto:${email}`} style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none' }}>
                                                                    {email}
                                                                </a>
                                                            </div>
                                                        )
                                                    ))}

                                                    {/* Phones */}
                                                    {(r.data_payload?.phones || (r.data_payload?.phone ? [r.data_payload.phone] : [])).slice(0, 2).map((phone, i) => (
                                                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                                                            <span style={{ opacity: 0.6 }}>📞</span>
                                                            <a href={`tel:${phone}`} style={{ color: 'rgba(255,255,255,0.8)', textDecoration: 'none' }}>
                                                                {phone}
                                                            </a>
                                                        </div>
                                                    ))}

                                                    {/* Unique Socials */}
                                                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
                                                        {r.data_payload?.linkedin_url && (
                                                            <a href={r.data_payload.linkedin_url} target="_blank" rel="noopener noreferrer" title="LinkedIn" style={{ color: '#0077b5', opacity: 0.9 }}>
                                                                <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" /></svg>
                                                            </a>
                                                        )}
                                                        {r.data_payload?.decision_maker_linkedin && r.data_payload.decision_maker_linkedin !== r.data_payload.linkedin_url && (
                                                            <a href={r.data_payload.decision_maker_linkedin} target="_blank" rel="noopener noreferrer" title="Decision Maker LinkedIn" style={{ color: '#0077b5', opacity: 0.9 }}>
                                                                <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" /></svg>
                                                            </a>
                                                        )}
                                                        {Object.entries(r.data_payload?.socials || {}).map(([network, link], i) => (
                                                            link && <a key={i} href={link} target="_blank" rel="noopener noreferrer" title={network} style={{ textDecoration: 'none', fontSize: '0.8rem' }}>
                                                                {network.includes('facebook') ? '📘' : network.includes('twitter') ? '🐦' : network.includes('instagram') ? '📸' : '🔗'}
                                                            </a>
                                                        ))}
                                                    </div>

                                                    {!r.data_payload?.email && !r.data_payload?.emails?.length && !r.data_payload?.phone && !r.data_payload?.phones?.length && !r.data_payload?.linkedin_url && (
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
                                    <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                        <span>🏢 {r.data_payload?.company || 'No Company'}</span>
                                        {r.data_payload?.location && <span style={{ color: 'hsl(var(--pearl-primary))' }}>📍 {r.data_payload.location}</span>}
                                        {r.data_payload?.industry && <span style={{ color: '#a855f7' }}>🏭 {r.data_payload.industry}</span>}
                                    </div>
                                </div>

                                {/* Contact Info */}
                                <div style={{ marginBottom: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.5)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                                        Contact Information
                                    </div>

                                    {/* DM Email */}
                                    {r.data_payload?.decision_maker_email && (
                                        <div style={{ marginBottom: '0.5rem' }}>
                                            <a href={`mailto:${r.data_payload.decision_maker_email}`} style={{ color: 'hsl(var(--pearl-success))', textDecoration: 'none', fontSize: '0.95rem', fontWeight: 'bold' }}>
                                                👤 {r.data_payload.decision_maker_email} <span style={{ fontSize: '0.7rem', opacity: 0.7 }}>(DM)</span>
                                            </a>
                                        </div>
                                    )}

                                    {/* All Emails */}
                                    {(r.data_payload?.emails || (r.data_payload?.email ? [r.data_payload.email] : [])).slice(0, 3).map((email, i) => (
                                        email !== r.data_payload?.decision_maker_email && (
                                            <div key={i} style={{ marginBottom: '0.3rem' }}>
                                                <a href={`mailto:${email}`} style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none', fontSize: '0.9rem' }}>
                                                    📧 {email}
                                                </a>
                                            </div>
                                        )
                                    ))}

                                    {/* All Phones */}
                                    {(r.data_payload?.phones || (r.data_payload?.phone ? [r.data_payload.phone] : [])).slice(0, 2).map((phone, i) => (
                                        <div key={i} style={{ marginBottom: '0.3rem' }}>
                                            <a href={`tel:${phone}`} style={{ color: 'rgba(255,255,255,0.9)', textDecoration: 'none', fontSize: '0.9rem' }}>
                                                📞 {phone}
                                            </a>
                                        </div>
                                    ))}

                                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.8rem' }}>
                                        {r.data_payload?.linkedin_url && (
                                            <div>
                                                <a href={r.data_payload.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none', fontSize: '0.85rem' }}>
                                                    💼 Company LinkedIn
                                                </a>
                                            </div>
                                        )}
                                        {r.data_payload?.decision_maker_linkedin && (
                                            <div>
                                                <a href={r.data_payload.decision_maker_linkedin} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--pearl-primary))', textDecoration: 'none', fontSize: '0.85rem' }}>
                                                    👤 DM Profile
                                                </a>
                                            </div>
                                        )}
                                    </div>

                                    {/* Socials */}
                                    {r.data_payload?.socials && Object.keys(r.data_payload.socials).length > 0 && (
                                        <div style={{ display: 'flex', gap: '0.8rem', marginTop: '0.5rem' }}>
                                            {Object.entries(r.data_payload.socials).map(([net, link], i) => (
                                                <a key={i} href={link} target="_blank" rel="noopener noreferrer" style={{ fontSize: '1.2rem', textDecoration: 'none' }}>
                                                    {net.includes('facebook') ? '📘' : net.includes('twitter') ? '🐦' : net.includes('instagram') ? '📸' : '🔗'}
                                                </a>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Scores */}
                                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                                            <div style={{ position: 'relative' }}>
                                                {r.data_payload?.avatar_url ? (
                                                    <img
                                                        src={r.data_payload.avatar_url}
                                                        alt={r.data_payload.name}
                                                        style={{ width: '40px', height: '40px', borderRadius: '10px', objectFit: 'cover', border: '1px solid var(--glass-border)' }}
                                                    />
                                                ) : (
                                                    <div style={{
                                                        width: '40px',
                                                        height: '40px',
                                                        borderRadius: '10px',
                                                        background: 'linear-gradient(135deg, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        fontSize: '0.8rem',
                                                        fontWeight: 900,
                                                        color: '#000'
                                                    }}>
                                                        {(r.data_payload?.name || "U")[0].toUpperCase()}
                                                    </div>
                                                )}
                                                {r.data_payload?.logo_url && (
                                                    <img
                                                        src={r.data_payload.logo_url}
                                                        alt="Company Logo"
                                                        style={{
                                                            position: 'absolute',
                                                            bottom: '-5px',
                                                            right: '-5px',
                                                            width: '18px',
                                                            height: '18px',
                                                            borderRadius: '4px',
                                                            background: '#fff',
                                                            border: '1px solid var(--glass-border)',
                                                            padding: '1px'
                                                        }}
                                                    />
                                                )}
                                            </div>
                                            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-bright)' }}>{r.data_payload?.name || 'Unknown Lead'}</div>
                                        </div>
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
