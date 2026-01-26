import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Globe, ShieldCheck, Zap, Activity, Cpu, Server, Signal, HardDrive } from 'lucide-react'

export default function SwarmObservatory() {
    const [workers, setWorkers] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadWorkers()
        const interval = setInterval(loadWorkers, 10000)
        return () => clearInterval(interval)
    }, [])

    const loadWorkers = async () => {
        try {
            const { data, error } = await supabase
                .from('worker_status')
                .select('*')
                .order('last_pulse', { ascending: false })

            if (error) throw error
            setWorkers(data || [])
        } catch (error) {
            console.error('Swarm load error:', error)
        } finally {
            setLoading(false)
        }
    }

    const isOnline = (lastPulse) => {
        const pulseTime = new Date(lastPulse)
        const now = new Date()
        return (now - pulseTime) / 1000 / 60 < 2
    }

    const onlineNodes = workers.filter(w => isOnline(w.last_pulse)).length
    const avgHealth = workers.reduce((sum, w) => sum + (w.stealth_health || 0), 0) / (workers.length || 1)

    return (
        <div className="space-y-8 animate-slide-up">

            {/* HUD Header */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-white/5 pb-8">
                <div className="space-y-1">
                    <h2 className="text-3xl font-display font-black text-white tracking-widest flex items-center gap-4">
                        SWARM <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">OBSERVATORY</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Globe size={12} className="text-pearl animate-spin-slow" />
                        <span>GLOBAL RESIDENTIAL MESH // ACTIVE_TELEMETRY_STREAM</span>
                    </div>
                </div>

                <div className="flex gap-4 bg-black/40 p-1.5 rounded-xl border border-white/5">
                    <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-3">
                        <Signal size={14} className="text-emerald-500 animate-pulse" />
                        <span className="text-[0.65rem] font-black text-emerald-500 tracking-widest uppercase">{onlineNodes} NODES_ONLINE</span>
                    </div>
                </div>
            </div>

            {/* Global Stealth HUD */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatMetric icon={Globe} label="TOTAL_WORKERS" value={workers.length} color="text-pearl" />
                <StatMetric icon={ShieldCheck} label="MEAN_STEALTH" value={`${avgHealth.toFixed(1)}%`} color="text-emerald-400" />
                <StatMetric icon={Cpu} label="ACTIVE_TASKS" value={workers.reduce((s, w) => s + (w.active_missions || 0), 0)} color="text-amber-400" />
            </div>

            {/* Node List Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {workers.map(worker => (
                    <NodeSlab key={worker.worker_id} worker={worker} online={isOnline(worker.last_pulse)} />
                ))}
            </div>
        </div>
    )
}

function StatMetric({ icon: Icon, label, value, color }) {
    return (
        <div className="glass-panel p-6 bg-white/[0.02] border border-white/5 flex flex-col items-center justify-center text-center group hover:border-pearl/20 transition-all">
            <div className={`p-2 rounded-lg bg-white/5 ${color} mb-3 group-hover:scale-110 transition-transform`}>
                <Icon size={18} />
            </div>
            <div className={`text-2xl font-display font-black text-white tracking-widest mb-1`}>{value}</div>
            <div className="text-[0.55rem] font-mono font-bold text-slate-600 uppercase tracking-widest">{label}</div>
        </div>
    )
}

function NodeSlab({ worker, online }) {
    const health = worker.stealth_health || 0
    const healthColor = health >= 90 ? 'text-emerald-500' : health >= 70 ? 'text-amber-500' : 'text-red-500'
    const healthBg = health >= 90 ? 'bg-emerald-500' : health >= 70 ? 'bg-amber-500' : 'bg-red-500'

    return (
        <div className={`p-6 rounded-2xl bg-black/40 border transition-all duration-300 group relative overflow-hidden flex flex-col sm:flex-row items-center gap-6 ${online ? 'border-white/5 hover:border-pearl/40' : 'border-red-500/20 opacity-60 grayscale'
            }`}>
            {/* Background Texture */}
            <div className="absolute inset-0 bg-scanline opacity-[0.03] pointer-events-none"></div>

            {/* Status Pulse */}
            <div className="relative flex-shrink-0">
                <div className={`w-12 h-12 rounded-full border border-white/5 flex items-center justify-center bg-white/[0.02] relative z-10`}>
                    <Server size={20} className={online ? 'text-pearl' : 'text-slate-600'} />
                </div>
                {online && (
                    <>
                        <div className="absolute inset-0 rounded-full border border-pearl/20 animate-ping"></div>
                        <div className="absolute top-0 right-0 w-3 h-3 rounded-full bg-emerald-500 shadow-neon-sm border-2 border-black"></div>
                    </>
                )}
            </div>

            <div className="flex-1 space-y-3 relative z-10 w-full sm:w-auto">
                <div className="flex justify-between items-start">
                    <div>
                        <div className="text-xs font-display font-black text-white tracking-widest uppercase mb-1">{worker.worker_id}</div>
                        <div className="flex items-center gap-3 text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">
                            <span className="flex items-center gap-1"><Globe size={10} /> {worker.geo_city}, {worker.geo_country}</span>
                            <span className="flex items-center gap-1"><HardDrive size={10} /> {worker.node_type || 'RESIDENTIAL'}</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className={`text-lg font-display font-black ${healthColor} tracking-tighter`}>{health.toFixed(1)}%</div>
                        <div className={`text-[0.5rem] font-mono font-bold ${healthColor} uppercase opacity-60 tracking-widest`}>STEALTH_INDEX</div>
                    </div>
                </div>

                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div className={`h-full ${healthBg} shadow-glow transition-all duration-1000`} style={{ width: `${health}%` }}></div>
                </div>

                <div className="flex justify-between items-center text-[0.5rem] font-mono text-slate-700 uppercase tracking-widest">
                    <span>Active_Missions: {worker.active_missions || 0}</span>
                    <span>Last_Pulse: {online ? 'LIVE' : new Date(worker.last_pulse).toLocaleTimeString()}</span>
                </div>
            </div>
        </div>
    )
}
