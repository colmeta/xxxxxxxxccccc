import React, { useState } from 'react'
import { supabase } from '../lib/supabase'
import { Disc, ShieldAlert, Mail, User, Building, ArrowRight } from 'lucide-react'

export default function Login() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [fullName, setFullName] = useState('')
    const [companyName, setCompanyName] = useState('')
    const [sent, setSent] = useState(false)

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)

        const { error } = await supabase.auth.signInWithOtp({
            email,
            options: {
                data: {
                    full_name: fullName,
                    company_name: companyName
                }
            }
        })

        if (error) {
            alert(error.error_description || error.message)
        } else {
            setSent(true)
        }
        setLoading(false)
    }

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-background p-4">

            {/* Ambient Background FX */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[600px] h-[600px] bg-pearl/10 rounded-full blur-[120px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-accent-purple/10 rounded-full blur-[120px] animate-pulse-slow animation-delay-2000"></div>
                {/* Scanline Effect */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
            </div>

            <div className="glass-panel w-full max-w-md p-8 md:p-12 relative z-10 flex flex-col items-center">

                {/* Brand Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-black/50 border border-pearl/30 shadow-neon mb-6 relative group">
                        <div className="absolute inset-0 bg-pearl/20 blur-lg rounded-full animate-pulse"></div>
                        <Disc className="w-10 h-10 text-pearl animate-spin-slow relative z-10" strokeWidth={1.5} />
                    </div>

                    <h1 className="text-4xl font-display font-black tracking-tighter text-white mb-2 uppercase">
                        CLARITY <span className="font-light text-pearl">PEARL</span>
                    </h1>
                    <div className="text-[0.6rem] font-mono font-bold text-pearl/50 tracking-[0.4em] uppercase">
                        Sensory Access Terminal
                    </div>
                </div>

                {sent ? (
                    <div className="w-full space-y-6 animate-slide-up">
                        <div className="p-6 rounded-xl bg-accent-success/5 border border-accent-success/20 flex flex-col items-center text-center">
                            <ShieldAlert className="w-12 h-12 text-accent-success mb-4" />
                            <h2 className="text-lg font-bold text-accent-success uppercase tracking-widest mb-2">MAPPING INITIALIZED</h2>
                            <p className="text-sm text-slate-400 font-mono leading-relaxed">
                                A secure metabolic link has been dispatched to <span className="text-white">{email}</span>.
                                Confirm identity to enter the lattice.
                            </p>
                        </div>
                        <button
                            onClick={() => setSent(false)}
                            className="w-full py-3 text-xs font-mono text-slate-500 hover:text-pearl transition-colors uppercase tracking-[0.2em]"
                        >
                            Back to Access
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleLogin} className="w-full space-y-6">

                        {/* Email Input */}
                        <div className="space-y-2">
                            <label className="block text-[0.6rem] font-black text-slate-500 uppercase tracking-widest ml-1">
                                Operator ID (Email)
                            </label>
                            <div className="relative group/input">
                                <Mail size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within/input:text-pearl transition-colors" />
                                <input
                                    className="input-cyber pl-12"
                                    type="email"
                                    placeholder="identity@claritypearl.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {/* Name & Company Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-[0.6rem] font-black text-slate-500 uppercase tracking-widest ml-1">
                                    Full Name
                                </label>
                                <div className="relative group/input">
                                    <User size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within/input:text-pearl transition-colors" />
                                    <input
                                        className="input-cyber pl-12"
                                        type="text"
                                        placeholder="John Doe"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="block text-[0.6rem] font-black text-slate-500 uppercase tracking-widest ml-1">
                                    Company
                                </label>
                                <div className="relative group/input">
                                    <Building size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within/input:text-pearl transition-colors" />
                                    <input
                                        className="input-cyber pl-12"
                                        type="text"
                                        placeholder="Acme Inc"
                                        value={companyName}
                                        onChange={(e) => setCompanyName(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Submit Button */}
                        <div className="pt-2">
                            <button
                                className="btn-primary w-full group py-4 h-auto"
                                disabled={loading}
                            >
                                {loading ? (
                                    <div className="w-6 h-6 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
                                ) : (
                                    <>
                                        INITIALIZE SESSION
                                        <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                )}

                {/* Footer Info */}
                <div className="mt-12 text-center">
                    <div className="text-[0.6rem] font-mono text-slate-600 uppercase tracking-[0.2em] mb-1">
                        System Version 2.6.0 [STABLE]
                    </div>
                    <div className="text-[0.5rem] font-mono text-slate-700 uppercase tracking-widest">
                        Encrypted Connection (AES-512) Established
                    </div>
                </div>
            </div>

            {/* Scanning Line Decoration */}
            <div className="absolute top-0 left-0 right-0 h-[1px] bg-pearl/20 animate-pulse pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-pearl/20 animate-pulse pointer-events-none"></div>
        </div>
    )
}
