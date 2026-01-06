import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export default function LiveFeed() {
    const [jobs, setJobs] = useState([])

    useEffect(() => {
        // Initial Fetch
        fetchJobs()

        // Realtime Subscription
        const channel = supabase
            .channel('public:jobs')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'jobs' }, (payload) => {
                console.log('Change received!', payload)
                fetchJobs() // Re-fetch to keep it simple and consistent
            })
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [])

    const fetchJobs = async () => {
        const { data, error } = await supabase
            .from('jobs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(10)

        if (!error && data) {
            setJobs(data)
        }
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'var(--success)'
            case 'running': return 'var(--warning)'
            case 'failed': return 'var(--danger)'
            default: return 'var(--text-muted)'
        }
    }

    return (
    return (
        <div className="supreme-glass" style={{ padding: '2rem', height: 'calc(100vh - 200px)', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ color: 'hsl(var(--nexus-primary))' }}>📡</span> MISSION LOG
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', fontSize: '0.6rem', fontWeight: 700 }}>
                    <div className="worker-active-pulse" style={{ width: '8px', height: '8px' }}></div>
                    LIVE
                </div>
            </div>

            {jobs.length === 0 ? (
                <div style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-xl)', border: '1px dashed var(--glass-border)' }}>
                    <div style={{ marginBottom: '1rem', fontSize: '1.5rem', opacity: 0.3 }}>📶</div>
                    <p style={{ margin: 0, fontSize: '0.75rem', letterSpacing: '1px' }}>AWAITING SENSORY SIGNALS...</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {jobs.map((job) => (
                        <div key={job.id} className="animate-slide-up" style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem',
                            padding: '1.25rem',
                            background: 'rgba(0,0,0,0.25)',
                            borderRadius: '16px',
                            border: '1px solid var(--glass-border)',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', maxWidth: '180px', lineHeight: '1.4' }}>
                                    {job.target_query}
                                </div>
                                <div style={{
                                    fontSize: '0.65rem',
                                    fontWeight: 900,
                                    padding: '2px 8px',
                                    borderRadius: '6px',
                                    background: job.status === 'completed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(251, 146, 60, 0.15)',
                                    color: getStatusColor(job.status)
                                }}>
                                    {job.status?.toUpperCase()}
                                </div>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontFamily: 'monospace', letterSpacing: '1px' }}>
                                    TARGET: {job.target_platform?.toUpperCase()}
                                </div>
                                <div style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.2)' }}>
                                    {new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
