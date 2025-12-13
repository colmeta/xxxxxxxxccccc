import React, { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'
import Layout from './components/Layout'
import Login from './components/Login'
import JobCreator from './components/JobCreator'
import LiveFeed from './components/LiveFeed'
import ResultsView from './components/ResultsView'

function App() {
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

    return (
        <Layout session={session}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
                <div className="main-content">
                    <JobCreator session={session} />
                    <ResultsView />
                </div>

                <div className="sidebar">
                    <LiveFeed />
                </div>
            </div>
        </Layout>
    )
}

export default App
