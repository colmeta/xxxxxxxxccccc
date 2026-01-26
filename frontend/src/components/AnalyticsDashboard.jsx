import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Activity, Target, ShieldCheck, Zap, BarChart3, TrendingUp, Cpu, Globe } from 'lucide-react'

export default function AnalyticsDashboard() {
    const [stats, setStats] = useState({
        total_leads: 0,
        verified_leads: 0,
        success_rate: 0,
        avg_clarity: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStats()
        const interval = setInterval(fetchStats, 30000)
        return () => clearInterval(interval)
    }, [])

    const fetchStats = async () => {
        try {
            const { data: { session: currentSession } } = await supabase.auth.getSession()
            const token = currentSession?.access_token

            if (!token) {
                setLoading(false)
                return
            }

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/results/stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setStats(data)
            }
        } catch (e) {
            console.error("Stats fetch error:", e)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-end gap-4 border-b border-pearl/10 pb-6">
                <div className="space-y-1">
                    <h2 className="text-2xl font-display font-black text-white tracking-widest flex items-center gap-3">
                        <BarChart3 className="text-pearl" size={24} />
                        SENSORY <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">TELEMETRY</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Activity size={12} className="text-emerald-500 animate-pulse" />
                        <span>LIVE INTELLIGENCE STREAM // CALIBRATED_TO_SOURCE</span>
                    </div>
                </div>

                <div className="flex gap-2">
                    <EngineStatus name="LinkedIn" status="operational" />
                    <EngineStatus name="Maps" status="active" />
                    <EngineStatus name="News" status="standby" />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatSlab
                    label="NODES_ACQUIRED"
                    value={stats.total_leads}
                    icon={Target}
                    trend="+12%_DELTA"
                    color="text-pearl"
                    glow="shadow-pearl/20"
                />
                <StatSlab
                    label="VERIFIED_INTEL"
                    value={stats.verified_leads}
                    icon={ShieldCheck}
                    trend={`${stats.success_rate}%_CONFIDENCE`}
                    color="text-emerald-400"
                    glow="shadow-emerald-500/10"
                />
                <StatSlab
                    label="MEAN_CLARITY"
                    value={`${stats.avg_clarity}%`}
                    icon={Zap}
                    trend="HIGH_FIDELITY"
                    color="text-pearl"
                    glow="shadow-pearl/20"
                />
                <StatSlab
                    label="ACTIVE_HYDRA"
                    value="04"
                    icon={Cpu}
                    trend="MAX_YIELD"
                    color="text-amber-400"
                    glow="shadow-amber-500/10"
                />
            </div>
        </div>
    )
}

function StatSlab({ label, value, icon: Icon, trend, color, glow }) {
    return (
        <div className={`glass-panel p-6 border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-pearl/20 transition-all duration-300 group overflow-hidden relative`}>
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                <Icon size={48} />
            </div>

            <div className="flex justify-between items-start mb-4">
                <span className="text-[0.6rem] font-black text-slate-500 uppercase tracking-widest">{label}</span>
                <div className={`p-1.5 rounded-lg bg-white/5 ${color} group-hover:shadow-glow transition-all`}>
                    <Icon size={14} />
                </div>
            </div>

            <div className={`text-3xl font-display font-black text-white tracking-widest mb-1`}>
                {value}
            </div>

            <div className="flex items-center gap-1.5 mt-2">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-[0.55rem] font-mono font-bold text-slate-400 uppercase tracking-widest">
                    {trend}
                </span>
            </div>
        </div>
    )
}

function EngineStatus({ name, status }) {
    const isOperational = status === 'operational'
    const isActive = status === 'active'

    return (
        <div className="px-3 py-1.5 rounded-lg bg-black/40 border border-white/5 flex items-center gap-2 group hover:border-pearl/20 transition-colors">
            <div className={`w-1.5 h-1.5 rounded-full ${isOperational ? 'bg-emerald-500 shadow-glow' :
                    isActive ? 'bg-pearl shadow-glow' :
                        'bg-slate-700'
                }`}></div>
            <span className="text-[0.55rem] font-black text-slate-500 group-hover:text-white transition-colors uppercase tracking-widest">
                {name}
            </span>
        </div>
    )
}

