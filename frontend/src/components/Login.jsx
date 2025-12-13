import React, { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function Login() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [sent, setSent] = useState(false)

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        const { error } = await supabase.auth.signInWithOtp({ email })
        if (error) {
            alert(error.error_description || error.message)
        } else {
            setSent(true)
        }
        setLoading(false)
    }

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <div className="glass-panel" style={{ padding: '3rem', maxWidth: '400px', width: '100%', textAlign: 'center' }}>
                <div style={{ marginBottom: '2rem' }}>
                    <h1 className="text-gradient" style={{ margin: 0, fontSize: '2.5rem' }}>CLARITY</h1>
                    <p style={{ color: 'var(--text-muted)', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '0.8rem' }}>
                        Sensory Access Terminal
                    </p>
                </div>

                {sent ? (
                    <div style={{ color: 'var(--success)', padding: '1rem', border: '1px solid var(--success)', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.1)' }}>
                        <p><strong>Link Sent.</strong><br />Check your secure comms channel used for verification.</p>
                    </div>
                ) : (
                    <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div style={{ textAlign: 'left' }}>
                            <label style={{ display: 'block', color: 'var(--text-muted)', marginBottom: '0.5rem', fontSize: '0.875rem' }}>OPERATOR ID</label>
                            <input
                                className="input-cyber"
                                type="email"
                                placeholder="identity@clarity.ai"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <button className="btn-primary" disabled={loading}>
                            {loading ? 'Authenticating...' : 'Initialize Session'}
                        </button>
                    </form>
                )}

                <div style={{ marginTop: '2rem', fontSize: '0.75rem', color: '#475569' }}>
                    System Version 0.9.1-Alpha <br />
                    Secure Connection Established
                </div>
            </div>
        </div>
    )
}
