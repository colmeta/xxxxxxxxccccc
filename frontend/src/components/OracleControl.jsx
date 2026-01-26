import React, { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'
import { Send, Upload, Command, Terminal, Sliders, Cpu, Activity, Zap } from 'lucide-react'
import JobCreator from './JobCreator'

export default function OracleControl() {
    const [prompt, setPrompt] = useState('')
    const [loading, setLoading] = useState(false)
    const [history, setHistory] = useState([])
    const [showAdvanced, setShowAdvanced] = useState(false)
    const scrollRef = useRef(null)

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [history])

    const dispatchMission = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || loading) return

        const userMsg = { role: 'user', content: prompt }
        setHistory(prev => [...prev, userMsg])
        setPrompt('')
        setLoading(true)

        try {
            const { data: { session } } = await supabase.auth.getSession()
            const token = session?.access_token

            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/oracle/dispatch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ prompt: prompt })
            })

            if (!res.ok) throw new Error('The Oracle is silent. (Mission failed)')

            const data = await res.json()
            const oracleMsg = {
                role: 'oracle',
                content: `Mission Deployed: ${data.steps_deployed} steps identified.`,
                details: data.interpretation
            }
            setHistory(prev => [...prev, oracleMsg])

        } catch (err) {
            setHistory(prev => [...prev, { role: 'oracle', content: `Error: ${err.message}`, isError: true }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="glass-panel min-h-[500px] flex flex-col relative overflow-hidden group border-pearl/20 shadow-[0_0_50px_rgba(0,240,255,0.05)]">
            {/* Holographic Grid Background */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
            <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none animate-pulse-slow">
                <Command size={200} />
            </div>

            {/* HEADER HUD */}
            <div className="flex items-center gap-3 p-6 border-b border-white/5 relative z-10 bg-black/20 backdrop-blur-sm">
                <div className="p-2 bg-pearl/10 rounded-lg border border-pearl/20 shadow-[0_0_15px_rgba(0,240,255,0.2)]">
                    <Terminal size={20} className="text-pearl animate-pulse" />
                </div>
                <div>
                    <h2 className="text-lg font-display font-black tracking-widest text-white flex gap-2 items-center">
                        ORACLE <span className="text-pearl">NEXUS</span>
                    </h2>
                    <div className="text-[0.55rem] text-pearl/50 font-mono uppercase tracking-[0.3em]">
                        Neural Interface V9.0 // READY
                    </div>
                </div>

                <div className="flex-1"></div>

                <div className="flex gap-2">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-white/5 border border-white/5 text-[0.6rem] font-mono text-emerald-400">
                        <Activity size={10} /> 98% STABLE
                    </div>
                    <button
                        onClick={() => setShowAdvanced(true)}
                        className="btn-ghost text-[0.65rem] py-1.5 px-3 border border-white/10 hover:bg-white/10 text-slate-400 hover:text-white hover:border-pearl/50 transition-all font-mono tracking-widest"
                    >
                        <Sliders size={12} className="mr-1" /> MANUAL_OVERRIDE
                    </button>
                </div>
            </div>

            {/* TERMINAL VIEWPORT */}
            <div
                ref={scrollRef}
                className="flex-1 p-6 font-mono text-sm overflow-y-auto custom-scrollbar relative z-10"
            >
                {history.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-6">
                        <div className="relative">
                            <div className="absolute -inset-4 bg-pearl/20 blur-xl rounded-full animate-pulse-slow"></div>
                            <Cpu size={64} className="text-pearl/50 relative z-10" strokeWidth={1} />
                        </div>
                        <div className="text-center space-y-2">
                            <p className="text-lg tracking-widest font-display text-white/50">AWAITING INSTRUCTION</p>
                            <p className="text-xs opacity-40 font-mono text-pearl">System initialized. Type a command to assume direct control.</p>
                        </div>
                    </div>
                )}

                {history.map((h, i) => (
                    <div key={i} className="mb-6 animate-slide-up group/msg">
                        <div className="flex items-start gap-3 mb-2">
                            <span className={`mt-1 text-[0.6rem] px-1.5 py-0.5 rounded font-bold tracking-wider ${h.role === 'user' ? 'bg-slate-800 text-slate-400' : 'bg-pearl/10 text-pearl border border-pearl/20'}`}>
                                {h.role === 'user' ? 'CMD' : 'SYS'}
                            </span>
                            <span className="text-xs text-slate-500 font-mono mt-1">
                                {new Date().toLocaleTimeString([], { hour12: false })}
                            </span>
                        </div>

                        <div className={`ml-2 pl-4 border-l-2 ${h.role === 'user' ? 'border-slate-700 text-slate-300' : 'border-pearl text-white'}`}>
                            <div className="leading-relaxed whitespace-pre-wrap">{h.content}</div>
                        </div>

                        {h.details && (
                            <div className="ml-6 mt-3 grid grid-cols-1 gap-2">
                                {h.details.map((d, index) => (
                                    <div key={index} className="flex justify-between items-center text-xs bg-white/5 p-3 rounded-r border-l-2 border-l-accent-purple hover:bg-white/10 transition-colors">
                                        <div className="flex items-center gap-2">
                                            <span className="text-accent-purple font-bold font-mono">STEP {index + 1}</span>
                                            <span className="text-slate-300">{d.query}</span>
                                        </div>
                                        <span className="px-2 py-0.5 bg-black/50 rounded text-[0.6rem] uppercase text-pearl tracking-wider border border-white/5">
                                            {d.platform}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex items-center gap-3 ml-2 text-pearl text-xs tracking-widest font-mono animate-pulse">
                        <Zap size={14} className="fill-pearl" />
                        PROCESSING NEURAL REQUEST...
                    </div>
                )}
            </div>

            {/* COMMAND PROMPT AREA */}
            <form onSubmit={dispatchMission} className="p-4 bg-black/40 backdrop-blur-xl border-t border-white/5 relative z-20 flex gap-4 items-end">
                {/* Decorative scanning line */}
                <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-pearl/50 to-transparent"></div>

                <input
                    type="file"
                    id="bulk-upload"
                    className="hidden"
                    accept=".csv"
                    onChange={async (e) => {
                        const file = e.target.files[0]
                        if (!file) return
                        setLoading(true)
                        setHistory(prev => [...prev, { role: 'user', content: `Initiating Bulk Upload: ${file.name}` }])
                        setTimeout(() => {
                            setLoading(false)
                            setHistory(prev => [...prev, { role: 'oracle', content: `Bulk Mission Queued: 50 targets identified.` }])
                        }, 1000)
                    }}
                />

                <button
                    type="button"
                    onClick={() => document.getElementById('bulk-upload').click()}
                    className="p-3 rounded-xl border border-white/10 hover:bg-white/5 text-slate-500 hover:text-white transition-all hover:border-pearl/30 hover:shadow-neon"
                    title="Upload CSV Mission"
                >
                    <Upload size={20} strokeWidth={1.5} />
                </button>

                <div className="flex-1">
                    <div className="relative group/input">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-pearl/20 to-accent-purple/20 rounded-xl blur opacity-0 group-hover/input:opacity-100 transition duration-500"></div>
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="INITIALIZE MISSION PARAMETERS..."
                            className="relative w-full bg-black border border-white/10 rounded-xl py-4 px-5 text-white placeholder-slate-600 focus:outline-none focus:border-pearl/50 focus:shadow-[0_0_30px_rgba(0,240,255,0.1)] transition-all font-mono text-sm tracking-wide"
                            disabled={loading}
                            autoFocus
                        />
                        <div className="absolute right-4 top-1/2 -translate-y-1/2">
                            <span className="text-[0.6rem] bg-white/5 border border-white/10 px-2 py-1 rounded text-slate-500 font-mono hidden md:block">
                                ↵ ENTER
                            </span>
                        </div>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="h-[54px] px-6 bg-pearl text-black font-bold font-display tracking-wider rounded-xl hover:shadow-[0_0_20px_rgba(0,240,255,0.4)] hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    <span className="hidden md:inline">DISPATCH</span>
                    <Send size={18} strokeWidth={2.5} className="md:hidden" />
                </button>
            </form>

            {/* Advanced Modal */}
            {showAdvanced && (
                <JobCreator
                    onClose={() => setShowAdvanced(false)}
                />
            )}
        </div>
    )
}
