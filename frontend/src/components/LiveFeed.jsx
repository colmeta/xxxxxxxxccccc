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
        <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 style={{ marginTop: 0, fontSize: '1.25rem', color: 'var(--secondary)', marginBottom: '1.5rem' }}>
                <span style={{ marginRight: '0.5rem' }}>📡</span> LIVE FEED
            </h2>

            {jobs.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No active signals detected.</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {jobs.map((job) => (
                        <div key={job.id} style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '1rem',
                            background: 'rgba(15, 23, 42, 0.4)',
                            borderRadius: 'var(--radius-md)',
                            borderLeft: `3px solid ${getStatusColor(job.status)}`
                        }}>
                            <div>
                                <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{job.query}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                    ID: {job.id.slice(0, 8)}...
                                </div>
                            </div>
                            <div style={{
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                fontWeight: 'bold',
                                color: getStatusColor(job.status),
                                letterSpacing: '1px'
                            }}>
                                {job.status}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
