import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { LayoutDashboard, Database, Brain, Globe, Settings, LogOut, User } from 'lucide-react'

export default function Layout({ children, session }) {
    const navigate = useNavigate()

    const handleLogout = async () => {
        await supabase.auth.signOut()
        navigate('/login')
    }

    const navItems = [
        { path: '/', label: 'MISSION CONTROL', icon: LayoutDashboard },
        { path: '/vault', label: 'THE VAULT', icon: Database },
        { path: '/intelligence', label: 'INTELLIGENCE', icon: Brain },
        { path: '/map', label: 'GLOBAL MAP', icon: Globe },
        { path: '/settings', label: 'SETTINGS', icon: Settings },
    ]

    return (
        <div className="min-h-screen flex flex-col max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <header className="glass-panel p-6 flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                {/* BRANDING */}
                <div className="flex items-center gap-4">
                    <div className="relative group cursor-pointer" onClick={() => navigate('/')}>
                        <div className="absolute -inset-1 bg-gradient-to-r from-pearl to-secondary rounded-full blur opacity-40 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                        <img
                            src="/logo-cp.png"
                            alt="Clarity Pearl"
                            className="relative w-12 h-12 object-contain filter drop-shadow-lg transform transition group-hover:scale-105"
                        />
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-2xl font-black tracking-tighter text-white">
                            CLARITY<span className="font-light text-pearl">PEARL</span>
                        </h1>
                        <span className="text-[0.6rem] tracking-[0.2em] text-slate-400 font-bold uppercase">
                            Sovereign Intelligence
                        </span>
                    </div>
                </div>

                {/* NAVIGATION - DESKTOP */}
                <nav className="hidden md:flex items-center gap-1 bg-slate-800/50 p-1.5 rounded-xl border border-white/5">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `
                                px-4 py-2 rounded-lg text-xs font-bold tracking-wider flex items-center gap-2 transition-all
                                ${isActive
                                    ? 'bg-pearl text-black shadow-glow'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'}
                            `}
                        >
                            <item.icon size={16} strokeWidth={3} />
                            {item.label}
                        </NavLink>
                    ))}
                </nav>

                {/* USER PROFILE */}
                <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                        <div className="text-sm font-bold text-white">{session?.user?.email?.split('@')[0]}</div>
                        <div className="text-[0.6rem] font-black text-emerald-400 tracking-wider">VERIFIED AGENT</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="btn-ghost p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10"
                        title="Secure Logout"
                    >
                        <LogOut size={18} />
                    </button>
                </div>
            </header>

            {/* MOBILE NAV (Bottom Bar) */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-slate-900/90 backdrop-blur-xl border-t border-white/10 z-50 flex justify-around p-4 pb-6">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `
                            flex flex-col items-center gap-1
                            ${isActive ? 'text-pearl' : 'text-slate-500'}
                        `}
                    >
                        <item.icon size={20} className={isActive ? 'drop-shadow-[0_0_8px_rgba(6,182,212,0.6)]' : ''} />
                        <span className="text-[0.5rem] font-bold tracking-wider">{item.label.split(' ')[0]}</span>
                    </NavLink>
                ))}
            </nav>

            <main className="flex-1 relative z-0">
                {children}
            </main>

            <footer className="mt-12 py-6 border-t border-white/5 text-center text-slate-500 text-xs tracking-widest uppercase mb-16 md:mb-0">
                © 2026 Clarity Pearl Systems | Sovereign Data Architecture
            </footer>
        </div>
    )
}
