import React, { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function JobCreator({ session }) {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!query.trim()) return

        setLoading(true)
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/jobs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: query,
                    platform: 'linkedin',
                    compliance_mode: 'standard'
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to create job')
            }

            setQuery('')
        } catch (error) {
            console.error('Error creating job:', error)
            alert(error.message || 'Failed to initialize job sequence.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
            <h2 className="text-gradient" style={{ marginTop: 0, fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="animate-pulse-slow">⚡</span> INITIALIZE NEW HUNT
            </h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <input
                        className="input-cyber"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter Target Parameters (e.g. 'SaaS CEOs in Austin')"
                        style={{ paddingLeft: '2.5rem' }}
                    />
                    <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }}>🔍</span>
                </div>
                <button className="btn-primary" type="submit" disabled={loading} style={{ minWidth: '140px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
                    {loading ? <div className="spinner"></div> : 'EXECUTE'}
                </button>
            </form>
        </div>
    )
}
