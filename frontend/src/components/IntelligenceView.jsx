import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import '../styles/design-tokens.css'

export default function IntelligenceView({ session }) {
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // 'all', 'high-intent', 'verified'

    useEffect(() => {
        loadIntelligence()
    }, [filter])

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

        const headers = ["Name", "Title", "Company", "Email", "Intent Score", "Oracle Signal", "Clarity Score", "Velocity"]
        const csvRows = [headers.join(",")]

        results.forEach(res => {
            const data = res.data_payload || {}
            const velocity = res.velocity_data || {}
            const row = [
                `"${(data.name || "").replace(/"/g, '""')}"`,
                `"${(data.title || "").replace(/"/g, '""')}"`,
                `"${(data.company || "").replace(/"/g, '""')}"`,
                `"${data.email || ""}"`,
                res.intent_score || 0,
                `"${(res.oracle_signal || "").replace(/"/g, '""')}"`,
                res.clarity_score || 0,
                `"${velocity.scaling_signal || "Steady"}"`
            ]
            csvRows.push(row.join(","))
        })

        const csvContent = csvRows.join("\n")
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.setAttribute("href", url)
        link.setAttribute("download", `clarity_pearl_intelligence_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const getIntentColor = (score) => {
        if (score >= 85) return 'var(--success)'
        if (score >= 60) return 'var(--warning)'
        return 'var(--text-muted)'
    }

    const getIntentLabel = (score) => {
        if (score >= 85) return '🔥 HOT LEAD'
        if (score >= 60) return '⚡ WARM'
        return '❄️ COLD'
    }

    return (
        <div style={{
            background: 'rgba(0,0,0,0.3)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.05)'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 900, color: 'hsl(var(--pearl-primary))' }}>
                    🧠 INTELLIGENCE VIEW
                </h2>
                <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
                    <button
                        onClick={downloadIntelligenceAsCSV}
                        className="btn-secondary"
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            color: 'rgba(255,255,255,0.5)',
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,255,255,0.1)',
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        EXPORT CSV
                    </button>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {['all', 'high-intent', 'verified'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                style={{
                                    background: filter === f ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.05)',
                                    color: filter === f ? '#000' : 'rgba(255,255,255,0.5)',
                                    padding: '0.5rem 1rem',
                                    borderRadius: '8px',
                                    border: 'none',
                                    fontSize: '0.7rem',
                                    fontWeight: 700,
                                    textTransform: 'uppercase',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {f.replace('-', ' ')}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {loading ? (
                <SkeletonLoader type="result-card" count={3} />
            ) : results.length === 0 ? (
                <EmptyStates
                    type={filter === 'high-intent' ? 'no-results' : 'no-data'}
                    title={filter === 'high-intent' ? 'No High-Intent Leads Yet' : null}
                    description={filter === 'high-intent' ? 'High-intent leads will appear here as they are discovered.' : null}
                />
            ) : (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {results.map(result => {
                        const data = result.data_payload || {}
                        const velocity = result.velocity_data || {}
                        const displacement = result.displacement_data || {}

                        return (
                            <div key={result.id} style={{
                                background: 'rgba(0,0,0,0.3)',
                                borderRadius: '12px',
                                padding: '1.5rem',
                                border: `1px solid ${result.intent_score >= 80 ? 'var(--success)' : 'var(--border-subtle)'}`,
                                transition: 'all 0.3s',
                                cursor: 'pointer'
                            }}>
                                {/* Header with Intent */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
                                        <div style={{ position: 'relative' }}>
                                            {data.avatar_url ? (
                                                <img
                                                    src={data.avatar_url}
                                                    alt={data.name}
                                                    style={{ width: '44px', height: '44px', borderRadius: '12px', objectFit: 'cover', border: '1px solid var(--glass-border)' }}
                                                />
                                            ) : (
                                                <div style={{
                                                    width: '44px',
                                                    height: '44px',
                                                    borderRadius: '12px',
                                                    background: 'linear-gradient(135deg, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '0.9rem',
                                                    fontWeight: 900,
                                                    color: '#000'
                                                }}>
                                                    {(data.name || data.company || "U")[0].toUpperCase()}
                                                </div>
                                            )}
                                            {data.logo_url && (
                                                <img
                                                    src={data.logo_url}
                                                    alt="Company Logo"
                                                    style={{
                                                        position: 'absolute',
                                                        bottom: '-4px',
                                                        right: '-4px',
                                                        width: '18px',
                                                        height: '18px',
                                                        borderRadius: '4px',
                                                        background: '#fff',
                                                        border: '1px solid var(--glass-border)',
                                                        padding: '1.5px'
                                                    }}
                                                />
                                            )}
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff', marginBottom: '0.25rem', margin: 0 }}>
                                                {data.name || data.company || 'Unknown Contact'}
                                            </h3>
                                            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>
                                                {data.title} {data.company ? `@ ${data.company}` : ''}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{
                                        background: getIntentColor(result.intent_score) + '15',
                                        border: `1px solid ${getIntentColor(result.intent_score)}`,
                                        borderRadius: '8px',
                                        padding: '0.5rem 1rem',
                                        textAlign: 'center'
                                    }}>
                                        <div style={{ fontSize: '1.5rem', fontWeight: 900, color: getIntentColor(result.intent_score) }}>
                                            {result.intent_score || 0}
                                        </div>
                                        <div style={{ fontSize: '0.6rem', color: getIntentColor(result.intent_score), fontWeight: 700 }}>
                                            {getIntentLabel(result.intent_score)}
                                        </div>
                                    </div>
                                </div>

                                {/* Metrics Grid */}
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                                    {result.verified && (
                                        <div style={{ background: 'rgba(0,255,100,0.05)', borderRadius: '8px', padding: '0.75rem' }}>
                                            <div style={{ fontSize: '0.6rem', color: 'rgba(0,255,100,0.6)', marginBottom: '0.25rem' }}>VERIFICATION</div>
                                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'rgba(0,255,100,1)' }}>✅ VERIFIED</div>
                                        </div>
                                    )}
                                    {result.clarity_score > 0 && (
                                        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '0.75rem' }}>
                                            <div style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.25rem' }}>CLARITY SCORE</div>
                                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'hsl(var(--pearl-primary))' }}>{result.clarity_score}/100</div>
                                        </div>
                                    )}
                                    {velocity.growth_rate_pct > 0 && (
                                        <div style={{ background: 'rgba(255,200,0,0.05)', borderRadius: '8px', padding: '0.75rem' }}>
                                            <div style={{ fontSize: '0.6rem', color: 'rgba(255,200,0,0.6)', marginBottom: '0.25rem' }}>VELOCITY</div>
                                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'rgba(255,200,0,1)' }}>
                                                📈 +{velocity.growth_rate_pct}%
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Oracle Signal */}
                                {result.oracle_signal && result.oracle_signal !== 'Baseline' && (
                                    <div style={{
                                        background: 'rgba(147,51,234,0.1)',
                                        border: '1px solid rgba(147,51,234,0.3)',
                                        borderRadius: '8px',
                                        padding: '0.75rem',
                                        marginBottom: '1rem'
                                    }}>
                                        <div style={{ fontSize: '0.6rem', color: 'rgba(147,51,234,0.8)', fontWeight: 700, marginBottom: '0.25rem' }}>
                                            🔮 ORACLE SIGNAL
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'rgba(147,51,234,1)', fontWeight: 600 }}>
                                            {result.oracle_signal}
                                        </div>
                                    </div>
                                )}

                                {/* Displacement Script */}
                                {displacement.sovereign_script && (
                                    <details style={{ marginBottom: '1rem' }}>
                                        <summary style={{
                                            fontSize: '0.75rem',
                                            fontWeight: 700,
                                            color: 'hsl(var(--pearl-primary))',
                                            cursor: 'pointer',
                                            padding: '0.5rem',
                                            background: 'rgba(255,255,255,0.02)',
                                            borderRadius: '6px'
                                        }}>
                                            ⚔️ DISPLACEMENT SCRIPT (Click to expand)
                                        </summary>
                                        <div style={{
                                            marginTop: '0.5rem',
                                            padding: '1rem',
                                            background: 'rgba(0,0,0,0.4)',
                                            borderRadius: '8px',
                                            fontSize: '0.75rem',
                                            lineHeight: '1.6',
                                            color: 'rgba(255,255,255,0.8)',
                                            fontFamily: 'monospace',
                                            whiteSpace: 'pre-wrap'
                                        }}>
                                            {displacement.sovereign_script}
                                        </div>
                                    </details>
                                )}

                                {/* Contact Info */}
                                {data.email && (
                                    <div style={{
                                        fontSize: '0.75rem',
                                        color: 'rgba(255,255,255,0.6)',
                                        display: 'flex',
                                        gap: '1rem',
                                        flexWrap: 'wrap'
                                    }}>
                                        <span>📧 {data.email}</span>
                                        {data.source_url && <a href={data.source_url} target="_blank" style={{ color: 'hsl(var(--pearl-primary))' }}>🔗 View Profile</a>}
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
