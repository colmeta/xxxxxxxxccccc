import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Radio, Wifi, Database, Search, Target, ShieldCheck } from 'lucide-react'

export default function LiveFeed() {
    const [jobs, setJobs] = useState([])

    useEffect(() => {
        fetchJobs()
        const channel = supabase
            .channel('public:jobs')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'jobs' }, (payload) => {
                fetchJobs()
            })
            .subscribe()

        return () => {
            supabase.removeChannel(channel)
        }
    }, [])

    const fetchJobs = async () => {
        const { data, error } = await supabase
            .from('jobs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(10)

        if (!error && data) {
            setJobs(data)
        }
    }

    const getStatusStyles = (status) => {
        switch (status) {
            case 'completed': return 'bg-accent-success/10 text-accent-success border-accent-success/20'
            case 'running': return 'bg-accent-gold/10 text-accent-gold border-accent-gold/20 animate-pulse'
            case 'failed': return 'bg-accent-alert/10 text-accent-alert border-accent-alert/20'
            default: return 'bg-white/5 text-slate-500 border-white/5'
        }
    }

    return (
        <div className="glass-panel p-6 h-[calc(100vh-140px)] flex flex-col border-pearl/10 shadow-[inner_0_0_20px_rgba(0,0,0,0.5)]">
            <div className="flex justify-between items-center mb-8 border-b border-white/5 pb-4">
                <h2 className="text-sm font-display font-black text-white flex items-center gap-2 tracking-[0.2em] uppercase">
                    <Radio className="text-pearl animate-pulse" size={16} /> MISSION LOG
                </h2>
                <div className="flex items-center gap-2 text-[0.6rem] font-bold text-emerald-500 font-mono tracking-widest">
                    <span className="relative flex h-1.5 w-1.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                    </span>
                    LIVE_FEED
                </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4">
                {jobs.length === 0 ? (
                    <div className="py-20 text-center text-slate-600 border border-dashed border-white/5 rounded-xl bg-black/20 flex flex-col items-center gap-3">
                        <Wifi size={32} strokeWidth={1} className="opacity-20 translate-y-2" />
                        <p className="text-[10px] uppercase tracking-[0.3em] font-mono">Awaiting Signals...</p>
                    </div>
                ) : (
                    jobs.map((job) => (
                        <div key={job.id} className="p-4 bg-white/[0.02] rounded-xl border border-white/5 hover:border-pearl/20 transition-all group animate-slide-up relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-[1px] h-full bg-gradient-to-b from-transparent via-pearl/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

                            <div className="flex justify-between items-start mb-3">
                                <div className="text-xs font-bold text-slate-200 line-clamp-2 leading-relaxed font-mono">
                                    <span className="text-pearl/50 mr-1">&gt;</span>{job.target_query}
                                </div>
                                <div className={`text-[0.6rem] font-black px-2 py-0.5 rounded border uppercase tracking-widest ${getStatusStyles(job.status)}`}>
                                    {job.status}
                                </div>
                            </div>

                            <div className="flex justify-between items-center text-[0.6rem] font-mono tracking-tighter">
                                <div className="flex items-center gap-3 text-slate-500">
                                    <span className="flex items-center gap-1 uppercase">
                                        <Target size={10} /> {job.target_platform}
                                    </span>
                                    <span className="flex items-center gap-1 uppercase">
                                        <Database size={10} /> VAULT_SYNC
                                    </span>
                                </div>
                                <span className="text-slate-600 group-hover:text-pearl/50 transition-colors">
                                    {new Date(job.created_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-center gap-2">
                <ShieldCheck size={12} className="text-slate-700" />
                <span className="text-[0.5rem] font-mono text-slate-700 uppercase tracking-widest">End of encrypted stream</span>
            </div>
        </div>
    )
}
