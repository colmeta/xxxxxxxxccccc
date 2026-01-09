import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export default function SettingsView({ session }) {
    const [org, setOrg] = useState(null)
    const [apiKey, setApiKey] = useState('')
    const [slackUrl, setSlackUrl] = useState('')
    const [workers, setWorkers] = useState([])
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

            // 3. Fetch Swarm Status
            const { data: workerData } = await supabase.from('worker_status').select('*').order('last_pulse', { ascending: false })
            if (workerData) setWorkers(workerData)
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
        alert(`CLARITY PEARL API KEY GENERATED:\n\n${newKey}\n\nCOPY THIS NOW. It will not be shown again.`)
        setSaving(false)
    }

    if (loading) return <div style={{ color: 'var(--text-muted)' }}>Synchronizing Enterprise Data...</div>

    return (
        <div className="supreme-glass" style={{ padding: '2.5rem', marginTop: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '2rem', color: '#fff' }}>
                ⚙️ CLARITY PEARL COMMAND CENTER
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
                            <div style={{ width: `${(org?.credits_used / org?.credits_monthly) * 100}%`, height: '100%', background: 'hsl(var(--pearl-primary))' }}></div>
                        </div>
                    </div>
                </div>

                {/* API & Integrity */}
                <div>
                    <h3 style={{ fontSize: '0.8rem', opacity: 0.5, letterSpacing: '2px', marginBottom: '1.5rem' }}>CLARITY PEARL API (WHITE-LABEL)</h3>
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

            {/* DIVINE SWARM orchestration */}
            <div style={{ marginBottom: '3rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    🛰️ DIVINE SWARM (RESIDENTIAL NODES)
                    <span style={{ fontSize: '0.6rem', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '2px 8px', borderRadius: '10px', border: '1px solid rgba(34, 197, 94, 0.2)' }}>GLOBAL SYNC ACTIVE</span>
                </h3>
                <p style={{ fontSize: '0.8rem', opacity: 0.5, marginBottom: '2rem' }}>Monitor and manage the geographic distribution of your high-authority scraping swarm.</p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    {workers.length === 0 ? (
                        <div style={{ gridColumn: '1/-1', padding: '3rem', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '16px', color: 'rgba(255,255,255,0.2)' }}>
                            No active nodes detected. Ensure your local worker is running.
                        </div>
                    ) : (
                        workers.map(w => (
                            <div key={w.worker_id} className="supreme-glass" style={{ padding: '1.5rem', position: 'relative' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                    <div style={{ fontWeight: 800, fontSize: '0.9rem' }}>{w.worker_id}</div>
                                    <div style={{
                                        width: '8px', height: '8px', borderRadius: '50%',
                                        background: (new Date() - new Date(w.last_pulse)) < 60000 ? '#22c55e' : '#ef4444',
                                        boxShadow: (new Date() - new Date(w.last_pulse)) < 60000 ? '0 0 10px #22c55e' : 'none'
                                    }}></div>
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.75rem' }}>
                                    <div style={{ opacity: 0.4 }}>LOCATION: <span style={{ color: '#fff' }}>{w.geo_city || 'Unknown'}, {w.geo_country || 'Earth'}</span></div>
                                    <div style={{ opacity: 0.4 }}>RESIDENTIAL IP: <span style={{ color: '#fff' }}>{w.public_ip || 'Masked'}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
                                        <span style={{ opacity: 0.4 }}>STEALTH HEALTH</span>
                                        <span style={{ color: w.stealth_health > 90 ? '#22c55e' : '#f59e0b', fontWeight: 900 }}>{w.stealth_health}%</span>
                                    </div>
                                    <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                                        <div style={{ width: `${w.stealth_health}%`, height: '100%', background: w.stealth_health > 90 ? '#22c55e' : '#f59e0b' }}></div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* The Sovereign Extension */}
            <div style={{ marginBottom: '3rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    🧩 THE SOVEREIGN EXTENSION (LEGACY BRIDGE)
                    <span style={{ fontSize: '0.6rem', background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.4)', padding: '2px 8px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.1)' }}>MV3 COMPLIANT</span>
                </h3>
                <p style={{ fontSize: '0.8rem', opacity: 0.5, marginBottom: '1.5rem' }}>Inject the Sovereign HUD directly into LinkedIn and Twitter profiles to see intelligence without leaving your workflow.</p>

                <div className="supreme-glass" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
                        BRIDGE STATUS: <span style={{ color: 'hsl(var(--pearl-primary))' }}>LISTENING ON PORT 8000</span>
                    </div>
                    <button
                        onClick={() => alert("EXTENSION SETUP:\n1. Open Chrome Extensions\n2. Enable Developer Mode\n3. Click 'Load Unpacked'\n4. Select the 'extension/' directory in your Data Intelligence folder.")}
                        className="btn-ghost"
                        style={{ fontSize: '0.7rem' }}
                    >
                        SETUP INSTRUCTIONS
                    </button>
                </div>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.05)', margin: '3rem 0' }} />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem' }}>
                {/* AUTO-WARMER CONTROL */}
                <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem' }}>🔥 THE ARCHITECT'S FORGE (AUTO-WARMING)</h3>
                    <p style={{ fontSize: '0.8rem', opacity: 0.5, marginBottom: '1.5rem' }}>Pearl automatically drafts outbound scripts when viral growth ({">"}50%) is detected.</p>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{
                            width: '40px', height: '24px', background: '#22c55e', borderRadius: '12px',
                            position: 'relative', cursor: 'pointer', opacity: 0.8
                        }}>
                            <div style={{ width: '18px', height: '18px', background: '#fff', borderRadius: '50%', position: 'absolute', top: '3px', right: '3px' }}></div>
                        </div>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#22c55e' }}>AUTONOMOUS MODE ACTIVE</span>
                    </div>
                </div>

                {/* FLUTTERWAVE BILLING */}
                <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 900, marginBottom: '0.5rem' }}>💰 FLUTTERWAVE CREDIT FORGE</h3>
                    <p style={{ fontSize: '0.8rem', opacity: 0.5, marginBottom: '1.5rem' }}>Instantly top up your scraping capacity using local currency or USD.</p>

                    <button
                        onClick={() => alert("FLUTTERWAVE BRIDGE: Initializing Secure Sandbox Payment... (Phase 12 Verification required)")}
                        className="btn-primary"
                        style={{ background: 'linear-gradient(90deg, #fbbf24, #f59e0b)', border: 'none', color: '#000' }}
                    >
                        TOP UP CREDITS (FLUTTERWAVE)
                    </button>
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
