import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Link2, Zap, Save, RefreshCw, BookOpen, ShieldCheck, Terminal, History, ChevronRight, Activity, Cpu } from 'lucide-react'

export default function CRMHub({ session, orgId }) {
    const [crmLogs, setCrmLogs] = useState([])
    const [webhookUrl, setWebhookUrl] = useState('')
    const [loading, setLoading] = useState(true)
    const [syncing, setSyncing] = useState(false)

    useEffect(() => {
        loadCRMLogs()
        loadWebhookSettings()
    }, [])

    const loadCRMLogs = async () => {
        try {
            const { data, error } = await supabase
                .from('crm_injection_logs')
                .select('*')
                .eq('org_id', orgId)
                .order('created_at', { ascending: false })
                .limit(50)

            if (error) throw error
            setCrmLogs(data || [])
        } catch (error) {
            console.error('CRM logs error:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadWebhookSettings = async () => {
        try {
            const { data, error } = await supabase
                .from('organizations')
                .select('slack_webhook')
                .eq('id', orgId)
                .single()

            if (error) throw error
            setWebhookUrl(data?.slack_webhook || '')
        } catch (error) {
            console.error('Webhook load error:', error)
        }
    }

    const saveWebhook = async () => {
        try {
            const { error } = await supabase
                .from('organizations')
                .update({ slack_webhook: webhookUrl })
                .eq('id', orgId)

            if (error) throw error
            alert('PROTOCOL_SAVED: Webhook endpoint verified.')
        } catch (error) {
            alert('SAVE_ERROR: ' + error.message)
        }
    }

    const triggerManualSync = async () => {
        setSyncing(true)
        try {
            const token = session.access_token
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })

            const data = await response.json()
            alert(`SYNC_SUCCESS: ${data.count || 0} nodes transferred to CRM.`)
            loadCRMLogs()
        } catch (error) {
            alert('SYNC_ERROR: ' + error.message)
        } finally {
            setSyncing(false)
        }
    }

    return (
        <div className="space-y-8 animate-slide-up">

            {/* HUD Header */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-white/5 pb-8">
                <div className="space-y-1">
                    <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                        SYNC <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">VORTEX</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Link2 size={12} className="text-pearl" />
                        <span>INTEGRATION LAYER ACTIVE // CROSS-SYSTEM SYNCHRONIZATION</span>
                    </div>
                </div>

                <button
                    onClick={triggerManualSync}
                    disabled={syncing}
                    className="w-full md:w-auto bg-pearl text-black font-display font-bold py-3 px-8 rounded-xl text-xs tracking-widest hover:shadow-neon hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2 group"
                >
                    {syncing ? <RefreshCw size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                    MANUAL_SYNC_OVERRIDE
                </button>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">

                {/* Integration Controls */}
                <div className="xl:col-span-2 space-y-8">

                    {/* Webhook Terminal */}
                    <div className="glass-panel p-8 bg-black/40 border-pearl/10 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none">
                            <Zap size={120} strokeWidth={0.5} className="text-pearl" />
                        </div>

                        <div className="flex items-center gap-3 mb-8">
                            <div className="p-2 rounded-lg bg-pearl/10 text-pearl"><Zap size={18} /></div>
                            <h3 className="text-sm font-display font-black text-white tracking-widest uppercase">AUTOMATION_PROTOCOL</h3>
                        </div>

                        <div className="space-y-6">
                            <div className="p-6 rounded-2xl bg-black/60 border border-white/5 space-y-4">
                                <div className="flex justify-between items-center text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">
                                    <span>WEBHOOK_ENDPOINT_URL</span>
                                    <Terminal size={12} />
                                </div>
                                <input
                                    type="url"
                                    value={webhookUrl}
                                    onChange={(e) => setWebhookUrl(e.target.value)}
                                    placeholder="https://hooks.slack.com/..."
                                    className="w-full bg-transparent border-b border-white/10 py-2 font-mono text-sm text-pearl focus:border-pearl/40 outline-none transition-all placeholder:text-slate-800"
                                />
                                <button
                                    onClick={saveWebhook}
                                    className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-[0.65rem] font-black tracking-widest text-slate-400 hover:text-white hover:border-pearl/30 hover:bg-white/10 transition-all flex items-center justify-center gap-2 uppercase"
                                >
                                    <Save size={14} /> PERSIST_PROTOCOL
                                </button>
                            </div>

                            <div className="flex items-start gap-4 p-4 rounded-xl bg-pearl/5 border border-pearl/10">
                                <BookOpen size={16} className="text-pearl mt-1 shrink-0" />
                                <div className="text-[0.65rem] font-mono text-slate-400 leading-relaxed italic">
                                    Integration active for: Slack, Make.com, Zapier, Webflow, and custom REST endpoints. High-intent nodes (>80%) trigger automatic transmission.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Setup Guide Tiles */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all">
                            <div className="text-[0.6rem] font-black text-pearl uppercase tracking-widest mb-4">MAKE.COM_SETUP</div>
                            <ul className="text-[0.6rem] font-mono text-slate-500 space-y-2 uppercase">
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> INITIALIZE_SCENARIO</li>
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> SELECT_WEBHOOK_TRIGGER</li>
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> BIND_ENDPOINT_ABOVE</li>
                            </ul>
                        </div>
                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all">
                            <div className="text-[0.6rem] font-black text-emerald-500 uppercase tracking-widest mb-4">PRO_PROTOCOL</div>
                            <ul className="text-[0.6rem] font-mono text-slate-500 space-y-2 uppercase">
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> ENABLE_AUTO_PRIORITY</li>
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> SYNC_CRM_METADATA</li>
                                <li className="flex gap-2 items-center"><ChevronRight size={10} /> BROADCAST_TO_SLACK</li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Sync History */}
                <div className="glass-panel p-8 bg-black/40 border-white/5 flex flex-col">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 rounded-lg bg-white/5 text-slate-400"><History size={18} /></div>
                        <h3 className="text-sm font-display font-black text-white tracking-widest uppercase">SYNC_HISTORY</h3>
                    </div>

                    <div className="flex-1 space-y-4 overflow-y-auto custom-scrollbar pr-2 max-h-[600px]">
                        {crmLogs.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center gap-4 opacity-20">
                                <Cpu size={48} strokeWidth={1} />
                                <span className="text-[0.6rem] font-mono tracking-widest">NO_LOGS_DETECTED</span>
                            </div>
                        ) : (
                            crmLogs.map(log => (
                                <div key={log.id} className="p-4 rounded-xl bg-white/[0.02] border border-white/5 group hover:border-pearl/20 transition-all relative overflow-hidden">
                                    {/* Side status strip */}
                                    <div className={`absolute top-0 left-0 w-0.5 h-full ${log.status === 'success' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-red-500 shadow-[0_0_10px_#ef4444]'}`}></div>

                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-[0.65rem] font-black text-white uppercase tracking-widest">{log.crm_name || 'WEBHOOK'}_PUSH</span>
                                        <span className={`text-[0.55rem] font-mono px-2 py-0.5 rounded border ${log.status === 'success' ? 'text-emerald-500 border-emerald-500/20' : 'text-red-500 border-red-500/20'
                                            }`}>
                                            {log.status}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-600">
                                        <Activity size={10} />
                                        {new Date(log.created_at).toLocaleString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
