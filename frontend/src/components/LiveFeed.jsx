import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { Radio, Wifi } from 'lucide-react'

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

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'text-emerald-400 bg-emerald-500/10'
            case 'running': return 'text-amber-400 bg-amber-500/10'
            case 'failed': return 'text-red-400 bg-red-500/10'
            default: return 'text-slate-500 bg-white/5'
        }
    }

    return (
        <div className="glass-panel p-6 h-[calc(100vh-200px)] overflow-y-auto custom-scrollbar">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-black text-white flex items-center gap-2">
                    <Radio className="text-pearl" size={20} /> MISSION LOG
                </h2>
                <div className="flex items-center gap-2 text-[0.6rem] font-bold text-emerald-400">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    LIVE
                </div>
            </div>

            {jobs.length === 0 ? (
                <div className="p-8 text-center text-slate-500 border border-dashed border-white/10 rounded-xl bg-white/5">
                    <Wifi size={24} className="mx-auto mb-3 opacity-30" />
                    <p className="text-xs uppercase tracking-widest font-bold">Awaiting Signals...</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {jobs.map((job) => (
                        <div key={job.id} className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-all group animate-slide-up">
                            <div className="flex justify-between items-start mb-2">
                                <div className="text-sm font-bold text-white line-clamp-2 leading-tight">
                                    {job.target_query}
                                </div>
                                <div className={`text-[0.6rem] font-black px-2 py-0.5 rounded uppercase tracking-wider ${getStatusColor(job.status)}`}>
                                    {job.status}
                                </div>
                            </div>
                            <div className="flex justify-between items-center text-[0.6rem] text-slate-500">
                                <span className="font-mono uppercase">TARGET: {job.target_platform}</span>
                                <span className="opacity-50 group-hover:opacity-100 transition-opacity">
                                    {new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
