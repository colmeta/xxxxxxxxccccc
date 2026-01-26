import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Settings, CreditCard, Key, Shield, Wifi, RefreshCw, Lock, Activity, Cpu, Globe, Link2, Save } from 'lucide-react'

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
        const { data: profile } = await supabase.from('profiles').select('active_org_id').eq('id', session.user.id).single()

        if (profile?.active_org_id) {
            const { data: orgData } = await supabase.from('organizations').select('*').eq('id', profile.active_org_id).single()
            setOrg(orgData)
            setSlackUrl(orgData?.slack_webhook || '')

            const { data: keys } = await supabase.from('api_keys').select('id, name').eq('org_id', profile.active_org_id)
            if (keys?.length > 0) {
                setApiKey('••••••••••••••••')
            }

            const { data: workerData } = await supabase.from('worker_status').select('*').order('last_pulse', { ascending: false })
            if (workerData) setWorkers(workerData)
        }
        setLoading(false)
    }

    const saveSlack = async () => {
        setSaving(true)
        const { error } = await supabase.from('organizations').update({ slack_webhook: slackUrl }).eq('id', org.id)
        if (!error) alert('PROTOCOL_SAVED: Stealth Relay (Slack) Enabled.')
        setSaving(false)
    }

    const generateKey = async () => {
        const newKey = `nx_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
        const confirm = window.confirm("Generate a new Tactical API Key? This will replace your existing one.")
        if (!confirm) return

        setSaving(true)
        alert(`API_KEY_GENERATED:\n\n${newKey}\n\nCOPY THIS NOW. It will not be shown again.`)
        setSaving(false)
    }

    if (loading) return (
        <div className="h-[400px] flex items-center justify-center">
            <div className="text-pearl font-mono text-xs tracking-[0.5em] animate-pulse">SYNCHRONIZING_COMMAND_LATICE...</div>
        </div>
    )

    return (
        <div className="space-y-12 animate-slide-up">

            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-white/5 pb-8">
                <div className="space-y-1">
                    <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                        COMMAND <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">CENTER</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Cpu size={12} className="text-pearl" />
                        <span>ENTREPRISE_NODE_CONFIG // ORG_ID: {org?.id?.slice(0, 8)}</span>
                    </div>
                </div>

                <div className="flex gap-4">
                    <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-[0.6rem] font-black text-slate-400 uppercase tracking-widest">
                        PLAN_TIER: <span className="text-pearl">{org?.plan_tier || 'PRO_ELITE'}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Credit Slab */}
                <div className="glass-panel p-8 border-pearl/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
                        <CreditCard size={120} strokeWidth={0.5} className="text-pearl" />
                    </div>

                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 rounded-lg bg-pearl/10 text-pearl"><CreditCard size={18} /></div>
                        <h3 className="text-sm font-display font-black text-white tracking-widest uppercase">NODE_CREDITS</h3>
                    </div>

                    <div className="space-y-6">
                        <div className="flex items-end gap-4">
                            <div className="text-6xl font-display font-black text-white tracking-tighter">
                                {org?.credits_monthly - org?.credits_used}
                            </div>
                            <div className="text-[0.6rem] font-mono font-bold text-slate-500 uppercase tracking-widest mb-2 pb-1">Remaining_Calculated</div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-[0.55rem] font-mono text-slate-500 uppercase">
                                <span>Utilization</span>
                                <span>{((org?.credits_used / org?.credits_monthly) * 100).toFixed(1)}%</span>
                            </div>
                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                                <div
                                    className="h-full bg-gradient-to-r from-pearl to-white shadow-glow transition-all duration-1000"
                                    style={{ width: `${(org?.credits_used / org?.credits_monthly) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* API Key Slab */}
                <div className="glass-panel p-8 border-white/5 bg-white/[0.02] relative overflow-hidden group">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 rounded-lg bg-white/5 text-slate-400"><Key size={18} /></div>
                        <h3 className="text-sm font-display font-black text-white tracking-widest uppercase">TACTICAL_ACCESS_KEYS</h3>
                    </div>

                    <div className="space-y-6">
                        <div className="flex gap-4">
                            <input
                                readOnly
                                value={apiKey}
                                className="flex-1 bg-black/40 border border-white/5 rounded-xl px-4 py-3 font-mono text-xs text-pearl outline-none focus:border-pearl/40 transition-all text-center"
                                placeholder="NO_KEY_DETECTED"
                            />
                            <button onClick={generateKey} className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-[0.6rem] font-black tracking-widest text-slate-400 hover:text-white hover:border-pearl/30 hover:bg-white/10 transition-all uppercase flex items-center gap-2">
                                <RefreshCw size={14} /> ROTATE
                            </button>
                        </div>
                        <p className="text-[0.6rem] font-mono text-slate-600 uppercase leading-relaxed tracking-widest italic">
                            Integration active for white-label intelligence vault exposure.
                            <span className="text-red-500 block mt-1 underline underline-offset-4">ROTATION_INVALIDATES_ALL_ACTIVE_SESSIONS.</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* The Invisible Hand (Slack Relay) */}
            <div className="glass-panel p-8 border-purple-500/10 bg-purple-500/[0.02] relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
                    <Shield size={120} strokeWidth={0.5} className="text-purple-500" />
                </div>

                <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 rounded-lg bg-purple-500/10 text-purple-500 group-hover:shadow-[0_0_15px_rgba(168,85,247,0.4)] transition-all"><Shield size={18} /></div>
                    <h3 className="text-sm font-display font-black text-white tracking-widest uppercase">STEALTH_RELAY_PROTOCOL</h3>
                </div>

                <div className="max-w-3xl space-y-6">
                    <p className="text-[0.65rem] font-mono text-slate-400 leading-relaxed uppercase tracking-wider">
                        Configure high-intent Oracle signals (&gt;80% score) to broadcast directly to your secure communications layer.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1 bg-black/60 border border-white/5 rounded-2xl p-4 flex items-center gap-4 group/input focus-within:border-purple-500/40 transition-all">
                            <Link2 size={16} className="text-slate-700 group-focus-within/input:text-purple-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="https://hooks.slack.com/services/..."
                                value={slackUrl}
                                onChange={(e) => setSlackUrl(e.target.value)}
                                className="flex-1 bg-transparent border-none outline-none font-mono text-xs text-purple-400 placeholder:text-slate-800"
                            />
                        </div>
                        <button
                            onClick={saveSlack}
                            disabled={saving}
                            className="bg-purple-600 text-white font-display font-bold px-8 py-4 rounded-2xl text-[0.6rem] tracking-[0.3em] hover:shadow-[0_0_20px_rgba(168,85,247,0.5)] hover:scale-105 active:scale-95 transition-all uppercase flex items-center justify-center gap-2"
                        >
                            <Save size={14} /> {saving ? 'SYNCING...' : 'ACTIVATE_RELAY'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Footnote HUD */}
            <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4 text-[0.5rem] font-mono text-slate-700 uppercase tracking-[0.5em]">
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-neon-sm"></div>
                    SOUVEREIGN_SYSTEM_OPERATIONAL
                </div>
                <div>VER_V2.9.4_GOD_MODE_ACTIVE</div>
            </div>
        </div>
    )
}
