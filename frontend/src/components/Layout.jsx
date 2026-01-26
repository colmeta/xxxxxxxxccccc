import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { LayoutDashboard, Database, Brain, Globe, Settings, LogOut, Disc, Activity, Radio, Cpu } from 'lucide-react'

export default function Layout({ children, session }) {
    const navigate = useNavigate()
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)

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
        <div className="flex h-screen bg-background text-white overflow-hidden relative font-sans selection:bg-pearl selection:text-black">

            {/* AMBIENT BACKGROUND FX */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[50vw] h-[50vw] bg-pearl/5 rounded-full blur-[120px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-accent-purple/5 rounded-full blur-[120px] animate-pulse-slow animation-delay-2000"></div>
                {/* GRID OVERLAY */}
                <div className="absolute inset-0 bg-[#00F0FF]/[0.02] bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
            </div>

            {/* SIDEBAR - GLASS PANEL */}
            <aside
                className={`relative z-50 flex flex-col h-full bg-black/40 backdrop-blur-md border-r border-white/5 transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)] ${isSidebarOpen ? 'w-64' : 'w-20'} hidden md:flex group`}
                onMouseEnter={() => setIsSidebarOpen(true)}
                onMouseLeave={() => setIsSidebarOpen(false)}
            >
                {/* LOGO */}
                <div className="p-5 flex items-center justify-center border-b border-white/5 h-20">
                    <div className="relative flex items-center justify-center w-10 h-10 group-hover:scale-110 transition-transform duration-300">
                        {/* Logo Icon Placeholder */}
                        <div className="absolute inset-0 bg-pearl/20 blur-md rounded-full"></div>
                        <Disc className={`w-8 h-8 text-pearl ${isSidebarOpen ? 'animate-spin-slow' : ''}`} strokeWidth={1.5} />
                    </div>
                </div>

                {/* NAV ITEMS */}
                <nav className="flex-1 flex flex-col gap-2 p-3 mt-4">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `
                                relative flex items-center px-3 py-3 rounded-lg overflow-hidden transition-all duration-300 group/item
                                ${isActive ? 'bg-pearl/10 text-pearl' : 'text-slate-400 hover:text-white hover:bg-white/5'}
                            `}
                        >
                            {/* ACTIVE INDICATOR */}
                            {({ isActive }) => (
                                <>
                                    {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-pearl shadow-[0_0_10px_#00F0FF]"></div>}

                                    <div className="flex items-center gap-4 z-10 w-full justify-center lg:justify-start">
                                        <item.icon size={20} strokeWidth={isActive ? 2 : 1.5} className="min-w-[20px]" />

                                        <span className={`text-xs font-bold tracking-[0.15em] whitespace-nowrap overflow-hidden transition-all duration-300 ${isSidebarOpen ? 'opacity-100 max-w-[150px]' : 'opacity-0 max-w-0'}`}>
                                            {item.label}
                                        </span>
                                    </div>

                                    {/* HOVER GLOW */}
                                    <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-0 group-hover/item:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                {/* USER PROFILE - BOTTOM */}
                <div className="p-4 border-t border-white/5">
                    <button onClick={handleLogout} className="flex items-center gap-3 w-full p-2 text-slate-500 hover:text-red-400 transition-colors group/logout">
                        <LogOut size={20} />
                        <span className={`text-xs font-mono tracking-wider whitespace-nowrap overflow-hidden transition-all duration-300 ${isSidebarOpen ? 'opacity-100 max-w-[100px]' : 'opacity-0 max-w-0'}`}>
                            DISCONNECT
                        </span>
                    </button>
                    <div className={`mt-2 text-[10px] text-center text-slate-700 font-mono transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
                        V 2.6.0 [STABLE]
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT SHELL */}
            <main className="flex-1 flex flex-col relative z-10 min-w-0">

                {/* HUD HEADER */}
                <header className="h-16 border-b border-white/5 bg-black/20 backdrop-blur-sm flex items-center justify-between px-6 z-20">

                    {/* LEFT HUD - BREADCRUMB / STATUS */}
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-xs font-mono text-pearl/50">
                            <Activity size={14} className="animate-pulse" />
                            <span>SYSTEM ONLINE</span>
                        </div>
                        <div className="h-4 w-[1px] bg-white/10"></div>
                        <div className="text-xs text-slate-400 font-mono">
                            {session?.user?.email}
                        </div>
                    </div>

                    {/* RIGHT HUD - METRICS */}
                    <div className="flex items-center gap-6">

                        {/* FAKE SYSTEM METRICS FOR VIBE */}
                        <div className="hidden md:flex items-center gap-4 text-[10px] font-mono text-slate-500 tracking-wider">
                            <div className="flex items-center gap-1">
                                <Cpu size={12} />
                                <span>CORE: 34%</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <Radio size={12} />
                                <span>NET: SECURE</span>
                            </div>
                        </div>

                        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-pearl to-accent-purple p-[1px] relative cursor-pointer hover:shadow-neon transition-shadow">
                            <div className="bg-black w-full h-full rounded-full flex items-center justify-center">
                                <span className="text-xs font-bold text-white">OP</span>
                            </div>
                            <div className="absolute top-0 right-0 w-2 h-2 bg-accent-success rounded-full border-2 border-black"></div>
                        </div>
                    </div>
                </header>

                {/* SCROLLABLE VIEWPORT */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-8 scroll-smooth relative">
                    {/* BENTO GRID DECORATIONS CAN GO HERE */}
                    {children}
                </div>

                {/* MOBILE NAV (Bottom Bar) */}
                <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-black/90 backdrop-blur-xl border-t border-white/10 z-50 flex justify-evenly p-4 pb-6">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `
                                flex flex-col items-center gap-1 transition-all
                                ${isActive ? 'text-pearl drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]' : 'text-slate-600'}
                            `}
                        >
                            <item.icon size={22} strokeWidth={2} />
                        </NavLink>
                    ))}
                </nav>

            </main>
        </div>
    )
}
