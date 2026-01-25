import React, { useState, useEffect, useRef } from 'react'
import { supabase } from '../lib/supabase'
import { Send, Upload, Command, Terminal } from 'lucide-react'

export default function OracleControl() {
    const [prompt, setPrompt] = useState('')
    const [loading, setLoading] = useState(false)
    const [history, setHistory] = useState([])
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
        <div className="glass-panel p-6 min-h-[500px] flex flex-col relative overflow-hidden group">
            {/* Background Decor */}
            <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                <Command size={120} />
            </div>

            <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="p-2 bg-pearl/10 rounded-lg">
                    <Terminal size={20} className="text-pearl" />
                </div>
                <div>
                    <h2 className="text-lg font-black tracking-tight text-white flex gap-2 items-center">
                        CLARITY MISSION CONTROL
                    </h2>
                    <div className="text-[0.6rem] text-pearl font-mono uppercase tracking-widest">
                        Neural Interface V9.0
                    </div>
                </div>
            </div>

            {/* Terminal Window */}
            <div
                ref={scrollRef}
                className="flex-1 mb-4 p-4 rounded-xl bg-black/80 border border-white/10 font-mono text-sm overflow-y-auto shadow-inner custom-scrollbar"
            >
                {history.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-4">
                        <Terminal size={48} className="opacity-20" />
                        <div className="text-center">
                            <p>Ready for command.</p>
                            <p className="text-xs opacity-50 mt-2">Example: "Scout real estate in Miami"</p>
                        </div>
                    </div>
                )}
                {history.map((h, i) => (
                    <div key={i} className="mb-4 animate-slide-up">
                        <div className="flex items-start gap-2 mb-1">
                            <span className={h.role === 'user' ? 'text-slate-400' : 'text-pearl'}>
                                {h.role === 'user' ? '>' : '>>'}
                            </span>
                            <span className={`font-bold ${h.isError ? 'text-red-400' : 'text-slate-200'}`}>
                                {h.role === 'user' ? 'USER' : 'ORACLE'}
                            </span>
                        </div>

                        <div className={`ml-5 p-2 rounded ${h.role === 'user' ? 'text-slate-300' : 'text-emerald-400 bg-emerald-500/5 border border-emerald-500/10'}`}>
                            {h.content}
                        </div>

                        {h.details && (
                            <div className="ml-5 mt-2 space-y-2">
                                {h.details.map((d, index) => (
                                    <div key={index} className="flex justify-between items-center text-xs bg-white/5 p-2 rounded border border-white/5">
                                        <span className="text-pearl font-bold">[{index + 1}] {d.query}</span>
                                        <span className="px-2 py-0.5 bg-slate-800 rounded text-[0.6rem] uppercase text-slate-400">
                                            {d.platform}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="text-pearl animate-pulse ml-5 text-xs tracking-widest">
                        PROCESSING NEURAL REQUEST...
                    </div>
                )}
            </div>

            {/* Input Area */}
            <form onSubmit={dispatchMission} className="flex gap-3 relative z-10">
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
                        // Bulk upload logic (placeholder)
                        setTimeout(() => {
                            setLoading(false)
                            setHistory(prev => [...prev, { role: 'oracle', content: `Bulk Mission Queued: 50 targets identified.` }])
                        }, 1000)
                    }}
                />

                <button
                    type="button"
                    onClick={() => document.getElementById('bulk-upload').click()}
                    className="btn-ghost p-3 rounded-xl border-white/10 hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                    title="Upload CSV Mission"
                >
                    <Upload size={18} />
                </button>

                <div className="flex-1 relative">
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Enter mission parameters..."
                        className="w-full bg-slate-900/80 border border-pearl/30 rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none focus:border-pearl focus:ring-1 focus:ring-pearl/50 transition-all font-mono"
                        disabled={loading}
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-1">
                        <span className="text-[0.6rem] bg-white/10 px-1.5 rounded text-slate-500 font-mono hidden md:block">ENTER</span>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary"
                >
                    <span className="hidden md:inline">DISPATCH</span>
                    <Send size={16} className="md:hidden" />
                </button>
            </form>
        </div>
    )
}
