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
            const { error } = await supabase
                .from('jobs')
                .insert([
                    {
                        query: query,
                        status: 'queued',
                        user_id: session.user.id // Ensure RLS allows this
                    }
                ])

            if (error) throw error
            setQuery('')
        } catch (error) {
            console.error('Error creating job:', error)
            alert('Failed to initialize job sequence.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
            <h2 style={{ marginTop: 0, fontSize: '1.25rem', color: 'var(--primary)', marginBottom: '1.5rem' }}>
                <span style={{ marginRight: '0.5rem' }}>⚡</span> INITIALIZE NEW HUNT
            </h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <input
                    className="input-cyber"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter Target Parameters (e.g. 'SaaS CEOs in Austin')"
                    style={{ flex: 1, minWidth: '300px' }}
                />
                <button className="btn-primary" type="submit" disabled={loading} style={{ minWidth: '120px' }}>
                    {loading ? 'Processing...' : 'EXECUTE'}
                </button>
            </form>
        </div>
    )
}
