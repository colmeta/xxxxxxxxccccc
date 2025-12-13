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
                jobs ( query )
            `)
            .order('created_at', { ascending: false })
            .limit(50)

        if (!error && data) {
            setResults(data)
        }
        setLoading(false)
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem', marginTop: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--primary)' }}>
                    <span style={{ marginRight: '0.5rem' }}>💎</span> ACQUIRED INTEL
                </h2>
                <button
                    onClick={fetchResults}
                    className="btn-primary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.75rem', background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)' }}
                >
                    REFRESH
                </button>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                        <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                            <th style={{ padding: '1rem' }}>SOURCE QUERY</th>
                            <th style={{ padding: '1rem' }}>DATA</th>
                            <th style={{ padding: '1rem' }}>VERIFIED</th>
                            <th style={{ padding: '1rem' }}>CAPTURED</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results.length === 0 ? (
                            <tr>
                                <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    {loading ? 'Scanning database...' : 'No intelligence gathered yet.'}
                                </td>
                            </tr>
                        ) : (
                            results.map((r) => (
                                <tr key={r.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                                    <td style={{ padding: '1rem', color: 'var(--secondary)' }}>{r.jobs?.query || 'Unknown'}</td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ whiteSpace: 'pre-wrap', maxHeight: '100px', overflowY: 'auto', fontSize: '0.75rem' }}>
                                            {JSON.stringify(r.data, null, 2)}
                                        </div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        {r.verified ? (
                                            <span style={{ color: 'var(--success)', background: 'rgba(16, 185, 129, 0.1)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>VERIFIED</span>
                                        ) : (
                                            <span style={{ color: 'var(--warning)', background: 'rgba(245, 158, 11, 0.1)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>PENDING</span>
                                        )}
                                    </td>
                                    <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                                        {new Date(r.created_at).toLocaleString()}
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
