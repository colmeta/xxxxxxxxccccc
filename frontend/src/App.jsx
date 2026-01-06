import React, { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'
import Layout from './components/Layout'
import Login from './components/Login'
import JobCreator from './components/JobCreator'
import LiveFeed from './components/LiveFeed'
import ResultsView from './components/ResultsView'
import AnalyticsLab from './components/AnalyticsLab'
import OracleControl from './components/OracleControl'
import SettingsView from './components/SettingsView'
import CompliancePortal from './pages/CompliancePortal'
import './styles/supreme.css'

function App() {
    const [path, setPath] = useState(window.location.pathname)
    const [view, setView] = useState('vault') // 'vault' or 'settings'
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setLoading(false)
        })

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
        })

        return () => subscription.unsubscribe()
    }, [])

    if (loading) {
        return <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>INITIALIZING...</div>
    }

    if (!session) {
        return <Login />
    }

    if (path === '/compliance') {
        return <CompliancePortal />
    }

    return (
        <Layout session={session}>
            <div style={{ marginBottom: '2rem', display: 'flex', gap: '2rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <button
                    onClick={() => setView('vault')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'vault' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'vault' ? '2px solid hsl(var(--pearl-primary))' : 'none'
                    }}
                >
                    💎 THE VAULT
                </button>
                <button
                    onClick={() => setView('settings')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'settings' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'settings' ? '2px solid hsl(var(--pearl-primary))' : 'none'
                    }}
                >
                    ⚙️ COMMAND CENTER
                </button>
            </div>

            {view === 'vault' ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
                    <div className="main-content">
                        <JobCreator session={session} />
                        <OracleControl />
                        <AnalyticsLab />
                        <ResultsView />
                    </div>

                    <div className="sidebar">
                        <LiveFeed />
                    </div>
                </div>
            ) : (
                <SettingsView session={session} />
            )}
            <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <a href="/compliance" style={{ color: 'inherit', textDecoration: 'none' }}>COMPLIANCE & OPT-OUT</a>
            </div>
        </Layout>
    )
}

export default App
