import React, { useState } from 'react'
import { Zap, Copy, Check, Plus, BookOpen } from 'lucide-react'

export default function DisplacementLibrary() {
    const [selectedScript, setSelectedScript] = useState(null)
    const [copySuccess, setCopySuccess] = useState('')

    // Mock data for displacement scripts
    const scripts = [
        {
            id: 1,
            title: 'The "Trojan Horse" Intro',
            category: 'Cold Outreach',
            content: "Hi {{firstName}},\n\nI noticed you're using {{competitor}} for your data needs. Just wanted to share a quick report we ran on your site showing 3 missed opportunities...\n\nWould you be open to seeing the full data set?",
            effectiveness: '94%'
        },
        {
            id: 2,
            title: 'Value-Add Follow Up',
            category: 'Nurture',
            content: "Hey {{firstName}},\n\nThinking about our chat regarding {{painPoint}}. I found this case study relevant to your situation with {{company}}...\n\nLet me know if this resonates.",
            effectiveness: '88%'
        },
        {
            id: 3,
            title: 'The "Break Up" Email',
            category: 'Re-engagement',
            content: "Hi {{firstName}},\n\nI haven't heard back, so I assume you're all set with {{currentSolution}} or busy scaling {{company}}.\n\nI'll close your file for now, but feel free to reach out if priorities change.",
            effectiveness: '76%'
        }
    ]

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text)
        setCopySuccess('Copied!')
        setTimeout(() => setCopySuccess(''), 2000)
    }

    return (
        <div className="animate-slide-up space-y-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-black flex items-center gap-3 text-white">
                    <Zap className="text-pearl" size={24} />
                    DISPLACEMENT LIBRARY
                </h2>
                <button className="btn-primary text-xs py-2 px-3">
                    <Plus size={14} /> NEW SCRIPT
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Sidebar List */}
                <div className="space-y-3">
                    {scripts.map(script => (
                        <div
                            key={script.id}
                            onClick={() => setSelectedScript(script)}
                            className={`glass-panel p-4 cursor-pointer border transition-all duration-200 group relative overflow-hidden ${selectedScript?.id === script.id
                                    ? 'bg-pearl/10 border-pearl/40 shadow-glow'
                                    : 'bg-white/5 border-transparent hover:bg-white/10'
                                }`}
                        >
                            <div className="absolute top-0 left-0 w-1 h-full bg-pearl opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            <div className={`font-bold text-sm mb-2 ${selectedScript?.id === script.id ? 'text-white' : 'text-slate-300'}`}>
                                {script.title}
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="bg-white/10 text-slate-400 text-[0.6rem] uppercase font-bold px-2 py-0.5 rounded">
                                    {script.category}
                                </span>
                                <span className="text-emerald-400 text-xs font-bold">
                                    {script.effectiveness} Win
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Content Viewer */}
                <div className="lg:col-span-2 glass-panel p-0 min-h-[400px] flex flex-col bg-slate-900/50 overflow-hidden">
                    {selectedScript ? (
                        <>
                            <div className="p-6 border-b border-white/5 flex justify-between items-start bg-white/5">
                                <div>
                                    <h3 className="text-lg font-black text-white">{selectedScript.title}</h3>
                                    <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-bold">{selectedScript.category}</p>
                                </div>
                                <button
                                    onClick={() => copyToClipboard(selectedScript.content)}
                                    className="btn-ghost text-xs border border-white/10 hover:bg-white/10"
                                >
                                    {copySuccess ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                                    <span className="ml-2">{copySuccess || 'COPY'}</span>
                                </button>
                            </div>

                            <div className="flex-1 p-6 bg-black/20">
                                <div className="bg-slate-950 rounded-xl p-6 font-mono text-sm text-slate-300 leading-relaxed border border-white/5 shadow-inner">
                                    {selectedScript.content}
                                </div>
                            </div>

                            <div className="p-4 bg-white/5 border-t border-white/5 text-[0.65rem] text-slate-500 font-mono flex items-center gap-2">
                                <BookOpen size={12} />
                                Tip: Variables like {'{{firstName}}'} will be auto-replaced when using the Forge.
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-slate-600 gap-4">
                            <Zap size={48} className="opacity-20" />
                            <p className="text-sm font-bold opacity-50 uppercase tracking-widest">Select a script to view details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
