import React, { useState } from 'react'
import { Zap, Copy, Check, Plus, BookOpen, ShieldAlert, Terminal, FileCode, Search, Share2 } from 'lucide-react'

export default function DisplacementLibrary() {
    const [selectedScript, setSelectedScript] = useState(null)
    const [copySuccess, setCopySuccess] = useState('')

    // Mock data for displacement scripts
    const scripts = [
        {
            id: 1,
            title: 'TROJAN_HORSE_ENTRY',
            category: 'INFILTRATION',
            content: "Hi {{firstName}},\n\nI noticed you're using {{competitor}} for your data needs. Just wanted to share a quick report we ran on your site showing 3 missed opportunities...\n\nWould you be open to seeing the full data set?",
            effectiveness: '94%',
            risk: 'Low'
        },
        {
            id: 2,
            title: 'NEURAL_VALUE_ADD',
            category: 'NURTURE',
            content: "Hey {{firstName}},\n\nThinking about our chat regarding {{painPoint}}. I found this case study relevant to your situation with {{company}}...\n\nLet me know if this resonates.",
            effectiveness: '88%',
            risk: 'None'
        },
        {
            id: 3,
            title: 'TERMINATION_PROTOCOL',
            category: 'RE_ENGAGEMENT',
            content: "Hi {{firstName}},\n\nI haven't heard back, so I assume you're all set with {{currentSolution}} or busy scaling {{company}}.\n\nI'll close your file for now, but feel free to reach out if priorities change.",
            effectiveness: '76%',
            risk: 'Medium'
        }
    ]

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text)
        setCopySuccess('Copied!')
        setTimeout(() => setCopySuccess(''), 2000)
    }

    return (
        <div className="space-y-6 animate-slide-up">

            {/* Header Controls */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-white/5 pb-6">
                <div className="space-y-1">
                    <h2 className="text-2xl font-display font-black text-white tracking-widest flex items-center gap-3">
                        <Zap className="text-pearl animate-pulse" size={24} />
                        DISPLACEMENT <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">ARCHIVE</span>
                    </h2>
                    <div className="flex items-center gap-2 text-[0.55rem] font-mono text-slate-500 uppercase tracking-widest">
                        <Terminal size={12} className="text-pearl" />
                        <span>TACTICAL OUTREACH SCRIPTS // {scripts.length} DEPLOYABLE ASSETS</span>
                    </div>
                </div>

                <div className="flex gap-4">
                    <button className="bg-pearl text-black font-display font-bold py-2 px-6 rounded-lg text-xs tracking-widest hover:shadow-neon transition-all flex items-center gap-2">
                        <Plus size={14} /> NEW_PROTOCOL
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[500px]">

                {/* Sidebar Protocol List */}
                <div className="lg:col-span-1 space-y-3 overflow-y-auto custom-scrollbar pr-2">
                    <div className="relative mb-4">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600" />
                        <input
                            type="text"
                            placeholder="SEARCH_PROTOCOLS..."
                            className="w-full bg-black/40 border border-white/5 rounded-lg py-2 pl-10 pr-4 text-[0.6rem] font-mono text-slate-400 focus:border-pearl/40 outline-none transition-all"
                        />
                    </div>
                    {scripts.map(script => (
                        <div
                            key={script.id}
                            onClick={() => setSelectedScript(script)}
                            className={`p-4 rounded-xl border cursor-pointer group relative overflow-hidden transition-all duration-300 ${selectedScript?.id === script.id
                                    ? 'bg-pearl/10 border-pearl/40 shadow-[0_0_20px_rgba(255,255,255,0.05)]'
                                    : 'bg-white/[0.02] border-white/5 hover:border-white/10 hover:bg-white/[0.04]'
                                }`}
                        >
                            <div className={`font-display font-black text-xs tracking-widest mb-2 ${selectedScript?.id === script.id ? 'text-white' : 'text-slate-400'
                                }`}>
                                {script.title}
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-[0.55rem] font-mono font-bold text-slate-600 uppercase">
                                    {script.category}
                                </span>
                                <span className="text-emerald-500 text-[0.6rem] font-black group-hover:scale-110 transition-transform">
                                    {script.effectiveness}
                                </span>
                            </div>

                            {/* Scanning Indicator for active selection */}
                            {selectedScript?.id === script.id && (
                                <div className="absolute top-0 left-0 w-full h-[1px] bg-pearl/30 animate-scan"></div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Content Viewer / CRT Editor */}
                <div className="lg:col-span-3 glass-panel p-0 flex flex-col bg-black/40 border-pearl/10 overflow-hidden relative group">
                    {selectedScript ? (
                        <>
                            {/* Terminal Top Bar */}
                            <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                                <div className="flex items-center gap-4">
                                    <div className="flex gap-1.5">
                                        <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
                                        <div className="w-2 h-2 rounded-full bg-amber-500/50"></div>
                                        <div className="w-2 h-2 rounded-full bg-emerald-500/50"></div>
                                    </div>
                                    <div className="text-[0.6rem] font-mono text-slate-500 tracking-widest uppercase">
                                        FILE_PATH: ROOT/DISPLACEMENT/{selectedScript.title}.PROTO
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => copyToClipboard(selectedScript.content)}
                                        className="bg-white/5 border border-white/10 hover:border-pearl/30 px-4 py-1.5 rounded-lg text-[0.6rem] font-black tracking-widest text-slate-400 hover:text-white transition-all flex items-center gap-2"
                                    >
                                        {copySuccess ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                                        {copySuccess || 'CLONE_BUFFER'}
                                    </button>
                                    <button className="bg-white/5 border border-white/10 hover:border-emerald-500/30 px-3 py-1.5 rounded-lg text-slate-500 hover:text-emerald-400 transition-all">
                                        <Share2 size={12} />
                                    </button>
                                </div>
                            </div>

                            {/* CRT Editor Area */}
                            <div className="flex-1 p-8 relative overflow-hidden">
                                {/* Grid/Scanline Overlay */}
                                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none"></div>
                                <div className="absolute inset-0 bg-scanline pointer-events-none opacity-20"></div>

                                <div className="h-full bg-black/60 rounded-2xl border border-white/5 p-8 relative z-10 shadow-inner group-hover:border-pearl/5 transition-colors">
                                    <div className="flex items-center gap-3 mb-6 text-pearl/50">
                                        <FileCode size={16} />
                                        <div className="h-[1px] flex-1 bg-gradient-to-r from-pearl/20 to-transparent"></div>
                                    </div>

                                    <textarea
                                        readOnly
                                        value={selectedScript.content}
                                        className="w-full h-[200px] bg-transparent outline-none font-mono text-sm text-emerald-500/80 leading-relaxed resize-none cursor-default"
                                    />

                                    <div className="mt-8 flex gap-6">
                                        <div className="flex flex-col gap-1">
                                            <span className="text-[0.5rem] font-mono text-slate-600 uppercase tracking-widest">SUCCESS_RATE</span>
                                            <span className="text-base font-display font-black text-emerald-500 tracking-widest">{selectedScript.effectiveness}</span>
                                        </div>
                                        <div className="flex flex-col gap-1">
                                            <span className="text-[0.5rem] font-mono text-slate-600 uppercase tracking-widest">RISK_LEVEL</span>
                                            <span className={`text-base font-display font-black tracking-widest ${selectedScript.risk === 'Low' ? 'text-emerald-500' : selectedScript.risk === 'Medium' ? 'text-amber-500' : 'text-red-500'
                                                }`}>{selectedScript.risk}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* TIP BAR */}
                            <div className="px-6 py-3 border-t border-white/5 bg-white/[0.01] flex items-center gap-3">
                                <ShieldAlert size={12} className="text-pearl animate-pulse" />
                                <span className="text-[0.55rem] font-mono text-slate-600 uppercase tracking-widest">
                                    INFUSION ENGINE: Variables {'{{brackets}}'} auto-populating from node data.
                                </span>
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-6 opacity-30 animate-pulse">
                            <Zap size={64} strokeWidth={1} className="text-slate-800" />
                            <p className="font-display font-black text-slate-800 tracking-[0.5em] uppercase text-sm">Awaiting Protocol Selection</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
