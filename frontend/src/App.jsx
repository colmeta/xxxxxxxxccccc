import React, { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { supabase } from './lib/supabase'
import Layout from './components/Layout'
import Login from './components/Login'
import OnboardingWizard from './components/OnboardingWizard'

// Core Pillars (Views)
import OracleControl from './components/OracleControl'
import SovereignHub from './components/SovereignHub'
import LiveFeed from './components/LiveFeed'
import ResultsView from './components/ResultsView'
import JobSeparatedResults from './components/JobSeparatedResults'
import IntelligenceView from './components/IntelligenceView'
import GlobalMapView from './components/GlobalMapView'
import SettingsView from './components/SettingsView'
import Loader from './components/Loader' // Optional, inline for now

// Secondary Components (Lazy or direct import)
import CompliancePortal from './pages/CompliancePortal'
// import JobCreator from './components/JobCreator' // Now part of Oracle Advanced?
// import AnalyticsLab from './components/AnalyticsLab' // Now in Vault?

function App() {
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)
    const [orgSetupDone, setOrgSetupDone] = useState(false)
    const [showOnboarding, setShowOnboarding] = useState(false)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setLoading(false)
            if (session) checkAndSetupOrganization(session)
        })

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            if (session) checkAndSetupOrganization(session)
        })

        return () => subscription.unsubscribe()
    }, [])

    useEffect(() => {
        if (session && orgSetupDone) {
            const onboardingCompleted = localStorage.getItem('onboarding_completed')
            if (onboardingCompleted !== 'true') {
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
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
            })
            if (response.ok) setOrgSetupDone(true)
        } catch (error) {
            console.error('Org setup error:', error)
        }
    }

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-background text-pearl animate-pulse font-mono tracking-widest text-xs">
                INITIALIZING NEURAL INTERFACE...
            </div>
        )
    }

    if (!session) {
        return <Login />
    }

    return (
        <Layout session={session}>
            <Routes>
                {/* PILLAR 1: MISSION CONTROL (HOME) */}
                <Route path="/" element={
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <div className="lg:col-span-3 flex flex-col gap-8">
                            {/* Oracle Section */}
                            <section>
                                <div className="section-header">
                                    <h2 className="section-title text-pearl">
                                        <span>🔮</span> THE ORACLE
                                    </h2>
                                    <span className="badge badge-pearl">DATAFORGE AGENT ACTIVE</span>
                                </div>
                                <OracleControl />
                            </section>

                            {/* Sovereign Data Hub */}
                            <SovereignHub />
                        </div>

                        {/* Sidebar */}
                        <div className="lg:col-span-1">
                            <LiveFeed />
                        </div>
                    </div>
                } />

                {/* PILLAR 2: THE VAULT */}
                <Route path="/vault" element={<JobSeparatedResults />} />

                {/* PILLAR 3: INTELLIGENCE */}
                <Route path="/intelligence" element={<IntelligenceView session={session} />} />

                {/* PILLAR 4: GLOBAL MAP */}
                <Route path="/map" element={<GlobalMapView session={session} />} />

                {/* PILLAR 5: SETTINGS */}
                <Route path="/settings" element={<SettingsView session={session} />} />

                {/* UTILITY */}
                <Route path="/compliance" element={<CompliancePortal />} />

                {/* FALLBACK */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>

            {showOnboarding && (
                <OnboardingWizard
                    session={session}
                    onComplete={() => setShowOnboarding(false)}
                />
            )}
        </Layout>
    )
}

export default App
