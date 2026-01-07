import React, { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'

export default function OracleControl() {
    const [prompt, setPrompt] = useState('')
    const [loading, setLoading] = useState(false)
    const [history, setHistory] = useState([])
    const scrollRef = useRef(null)

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [history])

    const dispatchMission = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || loading) return

        const userMsg = { role: 'user', content: prompt }
        setHistory(prev => [...prev, userMsg])
        setPrompt('')
        setLoading(true)

        try {
            const { data: { session } } = await supabase.auth.getSession()
            const token = session?.access_token

            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/oracle/dispatch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ prompt: prompt })
            })

            if (!res.ok) throw new Error('The Oracle is silent. (Mission failed)')

            const data = await res.json()
            const oracleMsg = {
                role: 'oracle',
                content: `Mission Deployed: ${data.steps_deployed} steps identified.`,
                details: data.interpretation
            }
            setHistory(prev => [...prev, oracleMsg])

        } catch (err) {
            setHistory(prev => [...prev, { role: 'oracle', content: `Error: ${err.message}`, isError: true }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="supreme-glass" style={{ padding: '1.5rem', marginTop: '2rem', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 900, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ color: 'hsl(var(--pearl-primary))' }}>🔮</span> CLARITY PEARL MISSION CONTROL
            </h2>

            <div
                ref={scrollRef}
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    marginBottom: '1rem',
                    padding: '1rem',
                    background: 'rgba(0,0,0,0.2)',
                    borderRadius: '12px',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: '0.8rem'
                }}
            >
                {history.length === 0 && (
                    <div style={{ color: 'rgba(255,255,255,0.2)', textAlign: 'center', marginTop: '4rem' }}>
                        Ready for command. Example: "Scout real estate in Miami and ghostwrite to owners."
                    </div>
                )}
                {history.map((h, i) => (
                    <div key={i} style={{ marginBottom: '1rem', animation: 'fadeIn 0.3s ease-out' }}>
                        {h.role === 'user' ? '> USER:' : '>> ORACLE:'}
                        <div style={{ color: h.isError ? 'hsl(var(--pearl-danger))' : '#fff', marginTop: '0.25rem', whiteSpace: 'pre-wrap' }}>
                            {h.content}
                        </div>
                        {h.details && (
                            <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                {h.details.map((d, index) => (
                                    <div key={index} className="mission-log-entry" style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                    }}>
                                        <span>
                                            <span style={{ color: 'hsl(var(--pearl-primary))', marginRight: '0.5rem' }}>[{index + 1}]</span>
                                            {d.query}
                                        </span>
                                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                            <span style={{
                                                fontSize: '0.6rem',
                                                background: 'rgba(255,255,255,0.1)',
                                                padding: '2px 6px',
                                                borderRadius: '4px'
                                            }}>
                                                {d.platform.toUpperCase()}
                                            </span>
                                            {d.reasoning && (
                                                <span style={{
                                                    fontSize: '0.6rem',
                                                    color: 'rgba(255,255,255,0.4)',
                                                    fontStyle: 'italic',
                                                    maxWidth: '200px',
                                                    whiteSpace: 'nowrap',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis'
                                                }}>
                                                    // {d.reasoning}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div style={{ color: 'hsl(var(--pearl-primary))', animation: 'pulse 1s infinite' }}>
                        {">> ORACLE IS INTERPRETING..."}
                    </div>
                )}
            </div>

            <form onSubmit={dispatchMission} style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter mission command..."
                    className="input-cyber"
                    style={{
                        flex: 1,
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px'
                    }}
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary"
                    style={{ padding: '0 1.5rem', borderRadius: '8px', fontWeight: 900 }}
                >
                    DISPATCH
                </button>
            </form>
        </div>
    )
}
