import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export default function AnalyticsDashboard() {
    const [stats, setStats] = useState({
        total_leads: 0,
        verified_leads: 0,
        success_rate: 0,
        avg_clarity: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStats()
        // Auto-refresh every 30s
        const interval = setInterval(fetchStats, 30000)
        return () => clearInterval(interval)
    }, [])

    const fetchStats = async () => {
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            if (!token) {
                // Mock for dev if no auth
                setLoading(false)
                return
            }

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/results/stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setStats(data)
            }
        } catch (e) {
            console.error("Stats fetch error:", e)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 className="text-gradient" style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>📊</span> LIVE INTELLIGENCE FEED
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <StatCard
                    label="TOTAL TARGETS ACQUIRED"
                    value={stats.total_leads}
                    icon="🎯"
                    trend="+12% this hour"
                    color="var(--primary)"
                />
                <StatCard
                    label="VERIFIED INTELLIGENCE"
                    value={stats.verified_leads}
                    icon="✅"
                    trend={`${stats.success_rate}% Success Rate`}
                    color="#10b981"
                />
                <StatCard
                    label="AVERAGE CLARITY SCORE"
                    value={`${stats.avg_clarity}%`}
                    icon="💎"
                    trend="High Fidelity"
                    color="#8b5cf6"
                />
                <StatCard
                    label="ACTIVE AGENTS"
                    value="4"
                    icon="🤖"
                    trend="Hydra Nodes Online"
                    color="#f59e0b"
                />
            </div>

            <div style={{ marginTop: '2rem' }}>
                <h3 style={{ fontSize: '1rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Active Engine Status</h3>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <EngineBadge name="LinkedIn" status="operational" />
                    <EngineBadge name="Google Maps" status="operational" />
                    <EngineBadge name="Twitter Radar" status="active" />
                    <EngineBadge name="Startup Watch" status="active" />
                    <EngineBadge name="Website Crawler" status="standby" />
                </div>
            </div>
        </div>
    )
}

function StatCard({ label, value, icon, trend, color }) {
    return (
        <div style={{
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 'var(--radius-md)',
            padding: '1.5rem',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
                <span style={{ fontSize: '1.5rem' }}>{icon}</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: color }}>
                {value}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <span style={{ color: color }}>↗</span> {trend}
            </div>
        </div>
    )
}

function EngineBadge({ name, status }) {
    const getColor = (s) => {
        if (s === 'operational') return '#10b981'
        if (s === 'active') return '#3b82f6'
        return '#f59e0b'
    }

    return (
        <div style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '1rem',
            background: 'rgba(255,255,255,0.05)',
            border: `1px solid ${getColor(status)}44`,
            fontSize: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
        }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: getColor(status) }}></div>
            {name}
        </div>
    )
}
