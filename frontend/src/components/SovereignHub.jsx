import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export default function SovereignHub() {
    const [profiles, setProfiles] = useState([])
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState({ total_sovereign: 0, growth_leads: 0, displacements: 0 })

    useEffect(() => {
        fetchSovereignData()
    }, [])

    const fetchSovereignData = async () => {
        setLoading(true)
        const { data, error } = await supabase
            .from('data_vault')
            .select('*')
            .order('last_verified_at', { ascending: false })
            .limit(20)

        if (!error && data) {
            setProfiles(data)

            // Calculate stats
            const growth = data.filter(p => p.metadata?.velocity_data?.is_viral).length
            const displacements = data.filter(p => p.metadata?.displacement_data?.sovereign_script).length
            setStats({
                total_sovereign: data.length,
                growth_leads: growth,
                displacements: displacements
            })
        }
        setLoading(false)
    }

    return (
        <div className="sovereign-hub animate-fade-in" style={{ marginTop: '1rem' }}>
            {/* STATS HUD */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
                <div className="supreme-glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px' }}>Unified Identities</div>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'hsl(var(--pearl-primary))' }}>{stats.total_sovereign}</div>
                </div>
                <div className="supreme-glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px' }}>Velocity Alerts</div>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'hsl(var(--pearl-warning))' }}>{stats.growth_leads}</div>
                </div>
                <div className="supreme-glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '1px' }}>Ready for Displacement</div>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: 'hsl(var(--pearl-success))' }}>{stats.displacements}</div>
                </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#fff', letterSpacing: '-0.5px' }}>
                    🧠 THE <span style={{ color: 'hsl(var(--pearl-primary))' }}>SOVEREIGN</span> NETWORK
                </h2>
                <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', fontWeight: 600 }}>
                    AUTO-LINKING ACTIVE • MULTI-NODE SWARM SYNCED
                </div>
            </div>
            {/* Phase 12: Eternal Forge HUD */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
                <div className="supreme-glass animate-fade-in" style={{ padding: '1.5rem', borderLeft: '4px solid #3b82f6' }}>
                    <div style={{ fontSize: '0.7rem', opacity: 0.5, letterSpacing: '1px', marginBottom: '0.5rem' }}>AUTONOMOUS HEART</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 900 }}>PEARL-01 DEBATE</div>
                    <div style={{ fontSize: '0.75rem', color: '#22c55e', marginTop: '0.5rem' }}>● CRITIQUE SYSTEM ACTIVE</div>
                </div>
                <div className="supreme-glass animate-fade-in" style={{ padding: '1.5rem', borderLeft: '4px solid #22c55e' }}>
                    <div style={{ fontSize: '0.7rem', opacity: 0.5, letterSpacing: '1px', marginBottom: '0.5rem' }}>AUTO-WARMER</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 900 }}>ACTIVE SCOUTING</div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: '0.5rem' }}>Drafting Viral Leaks @ 300s</div>
                </div>
                <div className="supreme-glass animate-fade-in" style={{ padding: '1.5rem', borderLeft: '4px solid #f59e0b' }}>
                    <div style={{ fontSize: '0.7rem', opacity: 0.5, letterSpacing: '1px', marginBottom: '0.5rem' }}>MONETIZATION</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 900 }}>FLUTTERWAVE DRAFT</div>
                    <div style={{ fontSize: '0.75rem', color: '#f59e0b', marginTop: '0.5rem' }}>⚡ READY FOR ACTIVATION</div>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '5rem', color: 'var(--text-muted)' }}>
                    <div className="spinner" style={{ margin: '0 auto 1.5rem' }}></div>
                    SYNCING MEGA-PROFILES...
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '2rem' }}>
                    {profiles.map((p, i) => (
                        <div key={p.id} className="supreme-glass animate-slide-up" style={{ padding: '2rem', animationDelay: `${i * 0.1}s`, position: 'relative', overflow: 'hidden' }}>
                            {/* VELOCITY BADGE */}
                            {p.metadata?.velocity_data?.is_viral && (
                                <div style={{
                                    position: 'absolute', top: '10px', right: '-35px', background: 'hsl(var(--pearl-warning))',
                                    color: '#000', padding: '5px 40px', transform: 'rotate(45deg)', fontSize: '0.6rem', fontWeight: 900
                                }}>
                                    VIRAL GROWTH
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
                                {/* AVATAR PLACEHOLDER */}
                                <div style={{
                                    width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg, hsl(var(--pearl-primary)), hsl(var(--pearl-secondary)))',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 900, color: '#000'
                                }}>
                                    {p.full_name?.[0] || 'P'}
                                </div>

                                <div style={{ flex: 1 }}>
                                    <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800 }}>{p.full_name || 'Anonymous Asset'}</h3>
                                    <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.5)', marginBottom: '0.5rem' }}>{p.title} @ <span style={{ color: '#fff', fontWeight: 700 }}>{p.company}</span></div>

                                    {/* PLATFORM LINKS */}
                                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                                        {p.linkedin_url && <span title="LinkedIn Optimized" style={{ opacity: 0.6 }}>🔗</span>}
                                        {p.twitter_handle && <span title="Twitter Synced" style={{ opacity: 0.6 }}>🐦</span>}
                                        {p.tiktok_url && <span title="TikTok Active" style={{ opacity: 0.6 }}>🎵</span>}
                                        {p.ph_username && <span title="Product Hunt Maker" style={{ opacity: 0.6 }}>🐱</span>}
                                    </div>
                                </div>
                            </div>

                            {/* KINETIC VELOCITY HUD */}
                            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', fontWeight: 800, textTransform: 'uppercase', marginBottom: '0.5rem', color: 'rgba(255,255,255,0.4)' }}>
                                    <span>Growth Velocity</span>
                                    <span style={{ color: 'hsl(var(--pearl-warning))' }}>{p.metadata?.velocity_data?.scaling_signal || 'Steady'}</span>
                                </div>
                                <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: `${Math.min(p.metadata?.velocity_data?.growth_rate_pct || 10, 100)}%`,
                                        height: '100%',
                                        background: 'linear-gradient(90deg, hsl(var(--pearl-primary)), hsl(var(--pearl-warning)))',
                                        boxShadow: '0 0 10px rgba(245, 158, 11, 0.4)'
                                    }}></div>
                                </div>
                            </div>

                            {/* DISPLACEMENT INTELLIGENCE */}
                            {p.metadata?.displacement_data?.sovereign_script && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <div style={{ fontSize: '0.7rem', fontWeight: 800, marginBottom: '0.5rem', color: 'hsl(var(--pearl-success))' }}>🧠 DISPLACEMENT OPPORTUNITY: {p.metadata.displacement_data.displacement_target}</div>
                                    <div style={{
                                        fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', fontStyle: 'italic', padding: '1rem',
                                        borderLeft: '2px solid hsl(var(--pearl-success))', background: 'rgba(34, 197, 94, 0.05)'
                                    }}>
                                        "{p.metadata.displacement_data.sovereign_script.substring(0, 120)}..."
                                    </div>
                                    <button
                                        className="btn-primary"
                                        style={{ marginTop: '1rem', width: '100%', padding: '0.75rem', fontSize: '0.7rem' }}
                                        onClick={() => alert(`FULL DISPLACEMENT SCRIPT:\n\n${p.metadata.displacement_data.sovereign_script}`)}
                                    >
                                        DEPLOY SOVEREIGN SCRIPT
                                    </button>
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                                <button
                                    onClick={async () => {
                                        if (window.confirm(`Inject ${p.full_name} into your connected CRM?`)) {
                                            try {
                                                const { data: { session } } = await supabase.auth.getSession()
                                                const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync/lead`, {
                                                    method: 'POST',
                                                    headers: {
                                                        'Content-Type': 'application/json',
                                                        'Authorization': `Bearer ${session?.access_token}`
                                                    },
                                                    body: JSON.stringify({
                                                        vault_id: p.id,
                                                        crm_type: 'hubspot', // Default
                                                        api_key: 'DEMO_KEY'
                                                    })
                                                })
                                                if (res.ok) alert("Injection Successful: Intelligence synced to CRM.")
                                                else alert("CRM Sync Error: Check your settings.")
                                            } catch (e) { alert("Sync Failed.") }
                                        }
                                    }}
                                    style={{
                                        flex: 2, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff',
                                        padding: '0.5rem', fontSize: '0.65rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 700,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem'
                                    }}
                                >
                                    📥 SYNC TO CRM
                                </button>
                                <button style={{
                                    flex: 1, background: 'none', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.4)',
                                    padding: '0.5rem', fontSize: '0.65rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 700
                                }}>
                                    ID: {p.sovereign_id?.substring(0, 8)}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
