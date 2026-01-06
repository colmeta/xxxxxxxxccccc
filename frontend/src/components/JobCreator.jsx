import React, { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function JobCreator({ session }) {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [platform, setPlatform] = useState('linkedin')
    const [boostMode, setBoostMode] = useState(false)
    const [strategy, setStrategy] = useState('A')
    const [oneClickMode, setOneClickMode] = useState(false)

    const platforms = [
        { id: 'linkedin', label: 'LinkedIn', icon: '👔' },
        { id: 'google_news', label: 'News Pulse', icon: '📡' },
        { id: 'amazon', label: 'E-Commerce', icon: '🛒' },
        { id: 'real_estate', label: 'Real Estate', icon: '🏠' },
        { id: 'job_scout', label: 'Job Scout', icon: '💼' },
        { id: 'reddit', label: 'Reddit', icon: '🗨️' },
        { id: 'tiktok', label: 'TikTok', icon: '🎵' },
        { id: 'facebook', label: 'Facebook', icon: '👥' },
        { id: 'google_maps', label: 'G-Maps', icon: '📍' }
    ]

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!query.trim()) return

        setLoading(true)
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/jobs/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: query,
                    platform: platform,
                    compliance_mode: boostMode ? 'strict' : 'standard',
                    priority: boostMode ? 10 : 1,
                    ab_test_group: strategy,
                    search_metadata: {
                        one_click_agency: oneClickMode
                    }
                })
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Network error' }))
                throw new Error(errorData.detail || 'Failed to create job')
            }

            setQuery('')
        } catch (error) {
            console.error('Error creating job:', error)
            alert(error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="supreme-glass" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>
                    <span style={{ color: 'hsl(var(--nexus-primary))' }}>⚡</span> INITIALIZE SCOUT
                </h2>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    {platforms.map(p => (
                        <button
                            key={p.id}
                            onClick={() => setPlatform(p.id)}
                            style={{
                                padding: '0.5rem 1rem',
                                borderRadius: '12px',
                                background: platform === p.id ? 'hsl(var(--nexus-primary))' : 'rgba(255,255,255,0.05)',
                                color: platform === p.id ? '#000' : '#fff',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '0.75rem',
                                fontWeight: 800,
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                boxShadow: platform === p.id ? '0 0 15px rgba(59, 130, 246, 0.5)' : 'none'
                            }}
                        >
                            <span>{p.icon}</span> {p.label}
                        </button>
                    ))}

                    <div style={{ width: '1px', height: '24px', background: 'rgba(255,255,255,0.1)', margin: '0 0.5rem' }}></div>

                    <button
                        onClick={() => setBoostMode(!boostMode)}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '12px',
                            background: boostMode ? 'hsl(var(--nexus-warning))' : 'rgba(255,255,255,0.05)',
                            color: boostMode ? '#000' : 'rgba(255,255,255,0.4)',
                            border: '1px solid ' + (boostMode ? 'hsl(var(--nexus-warning))' : 'rgba(255,255,255,0.1)'),
                            cursor: 'pointer',
                            fontSize: '0.7rem',
                            fontWeight: 900,
                            letterSpacing: '1px',
                            transition: 'all 0.3s'
                        }}
                    >
                        🚀 BOOST {boostMode ? 'ON' : 'OFF'}
                    </button>

                    <select
                        value={strategy}
                        onChange={(e) => setStrategy(e.target.value)}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '12px',
                            background: 'rgba(255,255,255,0.05)',
                            color: '#fff',
                            border: '1px solid rgba(255,255,255,0.1)',
                            fontSize: '0.7rem',
                            fontWeight: 800,
                            cursor: 'pointer'
                        }}
                    >
                        <option value="A">STRATEGY A (STEALTH)</option>
                        <option value="B">STRATEGY B (SPEED)</option>
                        <option value="C">STRATEGY C (MOBILE SWARM)</option>
                    </select>

                    <button
                        onClick={() => setOneClickMode(!oneClickMode)}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '12px',
                            background: oneClickMode ? 'hsl(var(--nexus-primary))' : 'rgba(255,255,255,0.05)',
                            color: oneClickMode ? '#000' : '#fff',
                            border: '1px solid rgba(255,255,255,0.1)',
                            fontSize: '0.7rem',
                            fontWeight: 900,
                            cursor: 'pointer'
                        }}
                    >
                        🤖 ONE-CLICK AGENCY: {oneClickMode ? 'ACTIVE' : 'OFF'}
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <input
                        className="input-cyber"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder={`Who are we scouting on ${platform.toUpperCase()} today?`}
                        style={{
                            padding: '1.25rem 1.5rem',
                            paddingLeft: '3.5rem',
                            borderRadius: '20px',
                            background: 'rgba(0,0,0,0.3)',
                            fontSize: '1rem',
                            border: '1px solid rgba(255,255,255,0.05)',
                            transition: 'all 0.3s'
                        }}
                    />
                    <span style={{ position: 'absolute', left: '1.5rem', top: '50%', transform: 'translateY(-50%)', opacity: 0.3, fontSize: '1.25rem' }}>🔍</span>
                </div>
                <button
                    className="btn-primary"
                    type="submit"
                    disabled={loading}
                    style={{
                        minWidth: '200px',
                        borderRadius: '20px',
                        fontSize: '0.9rem',
                        fontWeight: 900,
                        letterSpacing: '1px',
                        background: boostMode ? 'linear-gradient(135deg, hsl(var(--nexus-primary)), hsl(var(--nexus-accent)))' : 'var(--nexus-primary)'
                    }}
                >
                    {loading ? <div className="spinner"></div> : 'LAUNCH MISSION'}
                </button>
            </form>

            <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', gap: '2rem', alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                    <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 800, color: '#fff', marginBottom: '0.5rem' }}>
                        🕵️ REALITY CHECK: DATA AUDIT
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)' }}>
                        Confirm the accuracy of your Apollo or ZoomInfo lists. We re-verify every lead.
                    </p>
                </div>
                <input
                    id="audit-upload"
                    type="file"
                    accept=".csv"
                    style={{ display: 'none' }}
                    onChange={async (e) => {
                        const file = e.target.files[0]
                        if (!file) return

                        setLoading(true)
                        try {
                            const formData = new FormData()
                            formData.append('file', file)

                            const { data: { session: currentSession } } = await supabase.auth.getSession()
                            const token = currentSession?.access_token

                            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/bulk/audit`, {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${token}` },
                                body: formData
                            })

                            if (!res.ok) throw new Error('Audit upload failed')
                            alert('Reality Check Initialized. Results will appear in your feed.')
                        } catch (err) {
                            alert(err.message)
                        } finally {
                            setLoading(false)
                        }
                    }}
                />
                <button
                    onClick={() => document.getElementById('audit-upload').click()}
                    style={{
                        padding: '0.75rem 1.5rem',
                        borderRadius: '15px',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px dashed rgba(255,255,255,0.2)',
                        color: '#fff',
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                    }}
                >
                    📁 UPLOAD CSV FOR AUDIT
                </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0.5rem 0' }}>
                <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.3)', letterSpacing: '1.5px', textTransform: 'uppercase' }}>
                    Shield: Stealth v2.4 (Residential)
                </div>
                <div style={{ fontSize: '0.65rem', color: boostMode ? 'hsl(var(--nexus-warning))' : 'rgba(255,255,255,0.3)', fontWeight: 700 }}>
                    {boostMode ? '⚠️ BOOST MODE: OVERNIGHT PRIORITY HARVESTING ACTIVE' : 'STANDARD PRIORITY'}
                </div>
            </div>
        </div>
    )
}
