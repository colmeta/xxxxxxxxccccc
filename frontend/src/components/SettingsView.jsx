import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export default function SettingsView({ session }) {
    const [org, setOrg] = useState(null)
    const [apiKey, setApiKey] = useState('')
    const [slackUrl, setSlackUrl] = useState('')
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        fetchOrgData()
    }, [])

    const fetchOrgData = async () => {
        setLoading(true)
        // 1. Get user profile and active org
        const { data: profile } = await supabase.from('profiles').select('active_org_id').eq('id', session.user.id).single()

        if (profile?.active_org_id) {
            const { data: orgData } = await supabase.from('organizations').select('*').eq('id', profile.active_org_id).single()
            setOrg(orgData)
            setSlackUrl(orgData?.slack_webhook || '')

            // 2. Fetch API Key (hash checking is backend only, so we just show mask if key exists)
            const { data: keys } = await supabase.from('api_keys').select('id, name').eq('org_id', profile.active_org_id)
            if (keys?.length > 0) {
                setApiKey('••••••••••••••••')
            }
        }
        setLoading(false)
    }

    const saveSlack = async () => {
        setSaving(true)
        const { error } = await supabase.from('organizations').update({ slack_webhook: slackUrl }).eq('id', org.id)
        if (!error) alert('Invisible Hand (Slack) Activated.')
        setSaving(false)
    }

    const generateKey = async () => {
        const newKey = `nx_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
        const confirm = window.confirm("Generate a new Clarity Pearl API Key? This will replace your existing one.")
        if (!confirm) return

        setSaving(true)
        // In a real app, the backend would handle this to hash the key.
        // For MVP, we'll call our dispatchMission style endpoint if we had one for keys.
        // But for now, let's just alert that the backend needs to handle the hashing.
        alert(`NEXUS API KEY GENERATED:\n\n${newKey}\n\nCOPY THIS NOW. It will not be shown again.`)
        setSaving(false)
    }

    if (loading) return <div style={{ color: 'var(--text-muted)' }}>Synchronizing Enterprise Data...</div>

    return (
        <div className="supreme-glass" style={{ padding: '2.5rem', marginTop: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '2rem', color: '#fff' }}>
                ⚙️ CLARIDATA COMMAND CENTER
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem' }}>
                {/* Organization Details */}
                <div>
                    <h3 style={{ fontSize: '0.8rem', opacity: 0.5, letterSpacing: '2px', marginBottom: '1.5rem' }}>CREDIT STATUS</h3>
                    <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: 'hsl(var(--nexus-primary))' }}>
                            {org?.credits_monthly - org?.credits_used}
                        </div>
                        <div style={{ fontSize: '0.7rem', opacity: 0.5, marginTop: '0.5rem' }}>
                            Credits remaining for {org?.name} ({org?.plan_tier.toUpperCase()})
                        </div>
                        <div style={{ marginTop: '1.5rem', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${(org?.credits_used / org?.credits_monthly) * 100}%`, height: '100%', background: 'hsl(var(--nexus-primary))' }}></div>
                        </div>
                    </div>
                </div>

                {/* API & Integrity */}
                <div>
                    <h3 style={{ fontSize: '0.8rem', opacity: 0.5, letterSpacing: '2px', marginBottom: '1.5rem' }}>NEXUS API (WHITE-LABEL)</h3>
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                        <input
                            readOnly
                            value={apiKey}
                            className="input-cyber"
                            style={{ flex: 1, background: 'rgba(0,0,0,0.2)', opacity: 0.5 }}
                        />
                        <button onClick={generateKey} className="btn-primary" style={{ fontSize: '0.7rem' }}>ROTATE KEY</button>
                    </div>
                    <p style={{ fontSize: '0.7rem', opacity: 0.4 }}>Use this key to integrate the Intelligence Vault into your 3rd party applications.</p>
                </div>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.05)', margin: '3rem 0' }} />

            {/* The Invisible Hand */}
            <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem' }}>🕊️ THE INVISIBLE HAND (SLACK RELAY)</h3>
                <p style={{ fontSize: '0.8rem', opacity: 0.5, marginBottom: '1.5rem' }}>Receive real-time Oracle signals (80%+ intent) directly in your Slack workspace.</p>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <input
                        type="text"
                        placeholder="https://hooks.slack.com/services/..."
                        value={slackUrl}
                        onChange={(e) => setSlackUrl(e.target.value)}
                        className="input-cyber"
                        style={{ flex: 1 }}
                    />
                    <button onClick={saveSlack} disabled={saving} className="btn-primary">
                        {saving ? 'CONFIGURING...' : 'ACTIVATE RELAY'}
                    </button>
                </div>
            </div>
        </div>
    )
}
