import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Settings, CreditCard, Key, Shield, Wifi, RefreshCw, Lock } from 'lucide-react'

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
        if (!error) alert('Invisible Hand (Slack) Activated.')
        setSaving(false)
    }

    const generateKey = async () => {
        const newKey = `nx_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
        const confirm = window.confirm("Generate a new Clarity Pearl API Key? This will replace your existing one.")
        if (!confirm) return

        setSaving(true)
        alert(`CLARITY PEARL API KEY GENERATED:\n\n${newKey}\n\nCOPY THIS NOW. It will not be shown again.`)
        setSaving(false)
    }

    if (loading) return (
        <div className="text-center p-12 animate-pulse text-slate-500 font-mono tracking-widest text-xs">
            SYNCHRONIZING ENTERPRISE SETTINGS...
        </div>
    )

    return (
        <div className="space-y-8 animate-slide-up">
            <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-slate-800 rounded-xl border border-white/5">
                    <Settings className="text-white" size={24} />
                </div>
                <h2 className="text-2xl font-black text-white tracking-tight">
                    COMMAND CENTER
                </h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Organization Details */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                        <CreditCard size={14} /> Credit Status
                    </div>
                    <div className="glass-panel p-6 bg-white/5">
                        <div className="text-4xl font-black text-pearl">
                            {org?.credits_monthly - org?.credits_used}
                        </div>
                        <div className="text-xs text-slate-400 mt-2 font-medium">
                            Credits remaining for <span className="text-white">{org?.name}</span> ({org?.plan_tier?.toUpperCase()})
                        </div>
                        <div className="mt-6 h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-pearl shadow-[0_0_10px_rgba(6,182,212,0.5)] transition-all duration-1000"
                                style={{ width: `${(org?.credits_used / org?.credits_monthly) * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* API & Integrity */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                        <Key size={14} /> White-Label API
                    </div>
                    <div className="glass-panel p-6 bg-white/5 flex flex-col justify-between h-full">
                        <div className="flex gap-4">
                            <input
                                readOnly
                                value={apiKey}
                                className="input-cyber text-center font-mono opacity-50"
                                placeholder="NO API KEY GENERATED"
                            />
                            <button onClick={generateKey} className="btn-primary py-2 px-4 text-xs whitespace-nowrap">
                                <RefreshCw size={14} /> ROTATE
                            </button>
                        </div>
                        <p className="text-xs text-slate-500 mt-4 leading-relaxed">
                            Use this key to integrate the Intelligence Vault into your 3rd party applications.
                            <span className="text-red-400 block mt-1">Warning: Rotating invalidates old keys immediately.</span>
                        </p>
                    </div>
                </div>
            </div>

            <hr className="border-white/5 my-8" />

            {/* DIVINE SWARM orchestration */}
            <div className="space-y-6">
                <div className="flex justify-between items-end">
                    <div>
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Wifi className="text-emerald-500" size={20} /> DIVINE SWARM
                        </h3>
                        <p className="text-sm text-slate-500 mt-1">Active residential nodes and proxy health.</p>
                    </div>
                    <span className="badge bg-emerald-500/10 text-emerald-500 border-emerald-500/20">GLOBAL SYNC ACTIVE</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {workers.length === 0 ? (
                        <div className="col-span-full p-12 text-center bg-white/5 rounded-2xl border border-white/5 text-slate-600">
                            No active nodes detected. Ensure your local worker is running.
                        </div>
                    ) : (
                        workers.map(w => (
                            <div key={w.worker_id} className="glass-panel p-5 relative overflow-hidden">
                                <div className="flex justify-between mb-4">
                                    <div className="font-bold text-sm text-white font-mono">{w.worker_id}</div>
                                    <div className={`w-2 h-2 rounded-full ${new Date() - new Date(w.last_pulse) < 60000 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]' : 'bg-red-500'}`}></div>
                                </div>
                                <div className="space-y-2 text-xs">
                                    <div className="flex justify-between text-slate-400">
                                        <span>LOCATION</span>
                                        <span className="text-white font-mono">{w.geo_city || 'Unknown'}, {w.geo_country || 'Earth'}</span>
                                    </div>
                                    <div className="flex justify-between text-slate-400">
                                        <span>IP ADDR</span>
                                        <span className="text-white font-mono">{w.public_ip || 'Masked'}</span>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-white/5">
                                        <div className="flex justify-between mb-1">
                                            <span className="text-[0.6rem] font-bold text-slate-500">STEALTH HEALTH</span>
                                            <span className={`text-xs font-bold ${w.stealth_health > 90 ? 'text-emerald-500' : 'text-amber-500'}`}>{w.stealth_health}%</span>
                                        </div>
                                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div className={`h-full ${w.stealth_health > 90 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${w.stealth_health}%` }}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <hr className="border-white/5 my-8" />

            {/* The Invisible Hand */}
            <div className="max-w-3xl">
                <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-2">
                    <Shield className="text-purple-500" size={20} /> THE INVISIBLE HAND
                </h3>
                <p className="text-sm text-slate-500 mb-6">Receive real-time Oracle signals (80%+ intent) directly in your Slack workspace.</p>

                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="https://hooks.slack.com/services/..."
                        value={slackUrl}
                        onChange={(e) => setSlackUrl(e.target.value)}
                        className="input-cyber flex-1"
                    />
                    <button onClick={saveSlack} disabled={saving} className="btn-primary min-w-[150px]">
                        {saving ? 'SAVING...' : 'ACTIVATE RELAY'}
                    </button>
                </div>
            </div>
        </div>
    )
}
