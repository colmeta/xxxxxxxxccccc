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
import SovereignHub from './components/SovereignHub'
import BulkMissionControl from './components/BulkMissionControl'
import IntelligenceView from './components/IntelligenceView'
import SwarmObservatory from './components/SwarmObservatory'
import CRMHub from './components/CRMHub'
import OnboardingWizard from './components/OnboardingWizard'
import CompliancePortal from './pages/CompliancePortal'
import VelocityView from './components/VelocityView'
import DisplacementLibrary from './components/DisplacementLibrary'
import CommandCenter from './components/CommandCenter'
import './styles/supreme.css'

function App() {
    const [path, setPath] = useState(window.location.pathname)
    const [view, setView] = useState('sovereign') // 'sovereign', 'vault', 'intelligence', 'swarm', etc.
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)
    const [showAdvanced, setShowAdvanced] = useState(false)
    const [orgSetupDone, setOrgSetupDone] = useState(false)
    const [showOnboarding, setShowOnboarding] = useState(false)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setLoading(false)

            // Auto-setup organization if user has none
            if (session) {
                checkAndSetupOrganization(session)
            }
        })

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            if (session) {
                checkAndSetupOrganization(session)
            }
        })

        return () => subscription.unsubscribe()
    }, [])

    // Check if user needs onboarding (after org setup)
    useEffect(() => {
        if (session && orgSetupDone) {
            const onboardingCompleted = localStorage.getItem('onboarding_completed')
            if (onboardingCompleted !== 'true') {
                // Small delay to let the UI render first
                setTimeout(() => setShowOnboarding(true), 500)
            }
        }
    }, [session, orgSetupDone])

    const checkAndSetupOrganization = async (session) => {
        if (!session || orgSetupDone) return

        try {
            const token = session.access_token
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/organizations/auto-setup`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })

            if (response.ok) {
                const data = await response.json()
                console.log('Organization setup:', data.message)
                setOrgSetupDone(true)
            }
        } catch (error) {
            console.error('Organization setup error:', error)
        }
    }

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
            <div style={{ marginBottom: '2rem', display: 'flex', gap: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)', overflowX: 'auto', paddingBottom: '0.5rem' }} className="tab-navigation">
                <button
                    onClick={() => setView('sovereign')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'sovereign' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'sovereign' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    🛰️ SOVEREIGN
                </button>
                <button
                    onClick={() => setView('vault')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'vault' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'vault' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    💎 SALES VAULT
                </button>
                <button
                    onClick={() => setView('velocity')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'velocity' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'velocity' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    📈 VELOCITY
                </button>
                <button
                    onClick={() => setView('displacement')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'displacement' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'displacement' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    ⚡ SCRIPTS
                </button>
                <button
                    onClick={() => setView('intelligence')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'intelligence' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'intelligence' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    🧠 INTELLIGENCE
                </button>
                <button
                    onClick={() => setView('swarm')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'swarm' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'swarm' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    🛸 SWARM
                </button>
                <button
                    onClick={() => setView('crm')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'crm' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'crm' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    🔗 CRM
                </button>
                <button
                    onClick={() => setView('bulk')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'bulk' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'bulk' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    📁 BULK
                </button>
                <button
                    onClick={() => setView('command')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'command' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'command' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    🗼 COMMAND
                </button>
                <button
                    onClick={() => setView('settings')}
                    style={{
                        background: 'none', border: 'none', padding: '1rem 0', color: view === 'settings' ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.4)',
                        fontWeight: 900, cursor: 'pointer', borderBottom: view === 'settings' ? '2px solid hsl(var(--pearl-primary))' : 'none', whiteSpace: 'nowrap'
                    }}
                >
                    ⚙️ SETTINGS
                </button>
            </div>

            {view === 'sovereign' ? (
                <div style={{ display: 'grid', gap: '2rem' }} className="main-grid">
                    <div className="main-content">
                        {/* THE ORACLE - TOP LEVEL COMMAND */}
                        <div style={{ marginBottom: '2rem' }}>
                            <h1 style={{
                                fontSize: '1.2rem',
                                fontWeight: 900,
                                color: 'rgba(255,255,255,0.7)',
                                textTransform: 'uppercase',
                                letterSpacing: '2px',
                                marginBottom: '0.25rem'
                            }}>
                                🔮 THE ORACLE
                            </h1>
                            <p style={{ fontSize: '0.7rem', color: 'hsl(var(--pearl-primary))', fontWeight: 700, letterSpacing: '1px', marginBottom: '1.5rem' }}>
                                POWERED BY DATAFORGE™ AUTOMATION
                            </p>
                            <OracleControl />
                        </div>

                        <SovereignHub />
                    </div>
                    <div className="sidebar">
                        <LiveFeed />
                    </div>
                </div>
            ) : view === 'vault' ? (
                <div style={{ display: 'grid', gap: '2rem' }} className="main-grid">
                    <div className="main-content">
                        {/* ORACLE CONTROL - PRIMARY INTERFACE */}
                        <div style={{ marginBottom: '1rem' }}>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '0.5rem',
                                flexWrap: 'wrap',
                                gap: '0.5rem'
                            }}>
                                <h1 style={{
                                    fontSize: '1.1rem',
                                    fontWeight: 900,
                                    color: 'rgba(255,255,255,0.5)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '2px',
                                    margin: 0
                                }}>
                                    What do you need today?
                                </h1>
                                <button
                                    onClick={() => setShowAdvanced(!showAdvanced)}
                                    style={{
                                        background: 'none',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        color: 'rgba(255,255,255,0.4)',
                                        padding: '0.5rem 1rem',
                                        borderRadius: '8px',
                                        fontSize: '0.7rem',
                                        cursor: 'pointer',
                                        fontWeight: 600,
                                        transition: 'all 0.3s'
                                    }}
                                >
                                    {showAdvanced ? '← SIMPLE MODE' : 'ADVANCED OPTIONS →'}
                                </button>
                            </div>
                            <p style={{
                                fontSize: '0.75rem',
                                color: 'rgba(255,255,255,0.3)',
                                marginBottom: '1.5rem',
                                lineHeight: '1.6'
                            }}>
                                Just type your request naturally. Our AI determines the best platforms to search automatically.
                                <br />
                                <span style={{ color: 'hsl(var(--pearl-primary))', fontWeight: 600 }}>Examples:</span> "Find tech CEOs in Austin" • "Scout real estate investors in Miami" • "Hiring managers at Y Combinator startups"
                            </p>
                        </div>

                        <OracleControl />

                        {/* ADVANCED MODE - Hidden by default */}
                        {showAdvanced && (
                            <div style={{
                                marginTop: '2rem',
                                padding: '1.5rem',
                                borderTop: '1px solid rgba(255,255,255,0.05)',
                                animation: 'fadeIn 0.3s ease-out'
                            }}>
                                <h3 style={{
                                    fontSize: '0.9rem',
                                    fontWeight: 800,
                                    color: 'rgba(255,255,255,0.6)',
                                    marginBottom: '1rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '1.5px'
                                }}>
                                    ⚙️ Power User Controls
                                </h3>
                                <JobCreator session={session} />
                            </div>
                        )}

                        <div style={{ marginTop: '2rem' }}>
                            <AnalyticsLab />
                        </div>

                        <div style={{ marginTop: '2rem' }}>
                            <ResultsView />
                        </div>
                    </div>

                    <div className="sidebar">
                        <LiveFeed />
                    </div>
                </div>
            ) : view === 'velocity' ? (
                <VelocityView />
            ) : view === 'displacement' ? (
                <DisplacementLibrary />
            ) : view === 'intelligence' ? (
                <IntelligenceView session={session} />
            ) : view === 'swarm' ? (
                <SwarmObservatory />
            ) : view === 'crm' ? (
                <div style={{ display: 'grid', gap: '2rem' }}>
                    <CRMHub session={session} orgId={session.user.user_metadata?.active_org_id} />
                </div>
            ) : view === 'bulk' ? (
                <div style={{ display: 'grid', gap: '2rem' }}>
                    <BulkMissionControl session={session} />
                </div>
            ) : view === 'command' ? (
                <CommandCenter session={session} />
            ) : (
                <SettingsView session={session} />
            )}

            {/* Onboarding Wizard Overlay */}
            {showOnboarding && (
                <OnboardingWizard
                    session={session}
                    onComplete={() => setShowOnboarding(false)}
                />
            )}
            <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <a href="/compliance" style={{ color: 'inherit', textDecoration: 'none' }}>COMPLIANCE & OPT-OUT</a>
            </div>
        </Layout>
    )
}

export default App
