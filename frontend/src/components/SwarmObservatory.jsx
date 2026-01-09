import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import '../styles/design-tokens.css'

export default function SwarmObservatory() {
    const [workers, setWorkers] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadWorkers()
        const interval = setInterval(loadWorkers, 10000) // Refresh every 10s
        return () => clearInterval(interval)
    }, [])

    const loadWorkers = async () => {
        try {
            const { data, error } = await supabase
                .from('worker_status')
                .select('*')
                .order('last_pulse', { ascending: false })

            if (error) throw error
            setWorkers(data || [])
        } catch (error) {
            console.error('Swarm load error:', error)
        } finally {
            setLoading(false)
        }
    }

    const getHealthColor = (health) => {
        if (health >= 95) return 'rgba(0,255,100,1)'
        if (health >= 80) return 'rgba(255,200,0,1)'
        return 'rgba(255,100,100,1)'
    }

    const isOnline = (lastPulse) => {
        const pulseTime = new Date(lastPulse)
        const now = new Date()
        const diffMinutes = (now - pulseTime) / 1000 / 60
        return diffMinutes < 2 // Online if pulsed in last 2 minutes
    }

    const totalNodes = workers.length
    const onlineNodes = workers.filter(w => isOnline(w.last_pulse)).length
    const avgHealth = workers.reduce((sum, w) => sum + (w.stealth_health || 0), 0) / (totalNodes || 1)

    return (
        <div style={{
            background: 'rgba(0,0,0,0.3)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.05)'
        }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '1rem', color: 'hsl(var(--pearl-primary))' }}>
                🛰️ SWARM OBSERVATORY
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginBottom: '2rem' }}>
                Global residential node network monitoring
            </p>

            {/* Global Stats */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '1rem',
                marginBottom: '2rem'
            }}>
                <div style={{
                    background: 'rgba(0,255,100,0.05)',
                    border: '1px solid rgba(0,255,100,0.2)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'rgba(0,255,100,1)' }}>
                        {onlineNodes}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'rgba(0,255,100,0.7)', fontWeight: 700 }}>
                        ONLINE NODES
                    </div>
                </div>
                <div style={{
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.05)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'hsl(var(--pearl-primary))' }}>
                        {totalNodes}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', fontWeight: 700 }}>
                        TOTAL WORKERS
                    </div>
                </div>
                <div style={{
                    background: 'rgba(147,51,234,0.05)',
                    border: '1px solid rgba(147,51,234,0.2)',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'rgba(147,51,234,1)' }}>
                        {avgHealth.toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'rgba(147,51,234,0.7)', fontWeight: 700 }}>
                        AVG STEALTH
                    </div>
                </div>
            </div>

            {/* Worker Grid */}
            {loading ? (
                <SkeletonLoader type="list-item" count={3} />
            ) : workers.length === 0 ? (
                <EmptyStates type="no-workers" />
            ) : (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {workers.map(worker => {
                        const online = isOnline(worker.last_pulse)
                        const health = worker.stealth_health || 0

                        return (
                            <div key={worker.worker_id} style={{
                                background: online ? 'rgba(0,0,0,0.3)' : 'rgba(255,100,100,0.05)',
                                borderRadius: '12px',
                                padding: '1.5rem',
                                border: `1px solid ${online ? 'rgba(255,255,255,0.05)' : 'rgba(255,100,100,0.2)'}`,
                                display: 'grid',
                                gridTemplateColumns: 'auto 1fr auto',
                                gap: '1.5rem',
                                alignItems: 'center'
                            }}>
                                {/* Status Indicator */}
                                <div style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '50%',
                                    background: online ? getHealthColor(health) : 'rgba(255,100,100,1)',
                                    boxShadow: `0 0 12px ${online ? getHealthColor(health) : 'rgba(255,100,100,1)'}`,
                                    animation: online ? 'pulse 2s infinite' : 'none'
                                }} />

                                {/* Worker Info */}
                                <div>
                                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#fff', marginBottom: '0.25rem' }}>
                                        {worker.worker_id}
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                                        <span>🌍 {worker.geo_city}, {worker.geo_country}</span>
                                        <span>🔒 {worker.node_type || 'residential'}</span>
                                        <span>⚡ {worker.active_missions || 0} missions</span>
                                    </div>
                                </div>

                                {/* Health Badge */}
                                <div style={{
                                    background: getHealthColor(health) + '15',
                                    border: `1px solid ${getHealthColor(health)}`,
                                    borderRadius: '8px',
                                    padding: '0.5rem 1rem',
                                    textAlign: 'center',
                                    minWidth: '80px'
                                }}>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 900, color: getHealthColor(health) }}>
                                        {health.toFixed(1)}%
                                    </div>
                                    <div style={{ fontSize: '0.6rem', color: getHealthColor(health), fontWeight: 700 }}>
                                        STEALTH
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Pulse Animation CSS */}
            <style>{`
                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.2); opacity: 0.8; }
                }
            `}</style>
        </div>
    )
}
