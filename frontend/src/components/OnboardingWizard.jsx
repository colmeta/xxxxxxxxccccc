import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { Globe, ShieldCheck, Target, Zap, Cpu, ArrowRight, UserPlus, Brain, Rocket, ChevronRight, Activity, Terminal } from 'lucide-react'

export default function OnboardingWizard({ session, onComplete }) {
    const [step, setStep] = useState(1)
    const [userGoal, setUserGoal] = useState(null)
    const [missionQuery, setMissionQuery] = useState('')
    const [platform, setPlatform] = useState('linkedin')
    const [creatingMission, setCreatingMission] = useState(false)
    const [missionId, setMissionId] = useState(null)

    useEffect(() => {
        const completed = localStorage.getItem('onboarding_completed')
        if (completed === 'true') {
            onComplete()
        }
    }, [])

    const goals = [
        { id: 'sales', label: 'B2B LEAD_GEN', icon: Globe, example: 'SaaS CEOs in Austin raising Series A' },
        { id: 'product', label: 'R&D_INTEL', icon: Brain, example: 'Top Shopify stores in fashion niche' },
        { id: 'competitor', label: 'MARKET_DISPLACEMENT', icon: Target, example: 'Companies using competitor XYZ' },
        { id: 'real-estate', label: 'ASSET_ACQUISITION', icon: Activity, example: 'Commercial properties in NYC' }
    ]

    const handleGoalSelect = (goal) => {
        setUserGoal(goal)
        setMissionQuery(goals.find(g => g.id === goal).example)
        setStep(3)
    }

    const handleCreateMission = async () => {
        setCreatingMission(true)
        try {
            const { data, error } = await supabase
                .from('jobs')
                .insert({
                    user_id: session.user.id,
                    org_id: session.user.user_metadata?.active_org_id,
                    target_query: missionQuery,
                    target_platform: platform,
                    priority: 5,
                    status: 'queued'
                })
                .select()
                .single()

            if (error) throw error
            setMissionId(data.id)
            setStep(4)
        } catch (error) {
            console.error('Mission creation error:', error)
            alert('Initialization Error. Please retry.')
        } finally {
            setCreatingMission(false)
        }
    }

    const handleComplete = () => {
        localStorage.setItem('onboarding_completed', 'true')
        onComplete()
    }

    const progress = (step / 5) * 100

    return (
        <div className="fixed inset-0 z-[10000] bg-[#020205] flex items-center justify-center p-6 overflow-hidden">

            {/* AMBIENT BACKGROUND FX */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
                <div className="h-full bg-pearl shadow-[0_0_15px_#fff] transition-all duration-700 ease-out" style={{ width: `${progress}%` }}></div>
            </div>

            {/* STARFIELD / GRID PARALLAX */}
            <div className="absolute inset-0 bg-hero-pattern opacity-40 animate-pulse-slow"></div>
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.03)_0%,transparent_70%)]"></div>

            {/* MAIN CONTAINER */}
            <div className="max-w-4xl w-full relative z-10 flex flex-col items-center">

                {/* STEP COUNTER HUD */}
                <div className="mb-12 flex items-center gap-4 text-[0.6rem] font-mono font-black text-slate-700 tracking-[0.5em] uppercase">
                    <span className={step >= 1 ? 'text-pearl' : ''}>01_INIT</span>
                    <div className="w-8 h-[1px] bg-white/10"></div>
                    <span className={step >= 2 ? 'text-pearl' : ''}>02_GOAL</span>
                    <div className="w-8 h-[1px] bg-white/10"></div>
                    <span className={step >= 3 ? 'text-pearl' : ''}>03_SWEEP</span>
                    <div className="w-8 h-[1px] bg-white/10"></div>
                    <span className={step >= 4 ? 'text-pearl' : ''}>04_PROTO</span>
                    <div className="w-8 h-[1px] bg-white/10"></div>
                    <span className={step >= 5 ? 'text-pearl' : ''}>05_DEPLOY</span>
                </div>

                <div className="w-full glass-panel p-12 lg:p-16 border-pearl/10 shadow-[inner_0_0_100px_rgba(0,0,0,0.8)] relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-pearl/20 to-transparent"></div>

                    {/* Step 1: Welcome Initiation */}
                    {step === 1 && (
                        <div className="text-center animate-slide-up">
                            <div className="mb-10 relative inline-block">
                                <div className="absolute -inset-8 bg-pearl/10 blur-3xl rounded-full animate-pulse-slow"></div>
                                <div className="p-6 rounded-[2rem] bg-black/40 border border-pearl/20 relative z-10 shadow-glow">
                                    <ShieldCheck size={64} className="text-pearl" strokeWidth={1} />
                                </div>
                            </div>
                            <h1 className="text-4xl lg:text-5xl font-display font-black text-white tracking-widest mb-6">
                                SOVEREIGN <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">INITIATION</span>
                            </h1>
                            <p className="text-sm font-mono text-slate-400 max-w-lg mx-auto leading-relaxed mb-12 uppercase tracking-wide">
                                You have gained access to the Sensory Lattice. <br />
                                <span className="opacity-40">Initialize your neural credentials to begin global synchronization.</span>
                            </p>
                            <button
                                onClick={() => setStep(2)}
                                className="bg-pearl text-black font-display font-bold py-4 px-12 rounded-xl text-xs tracking-[0.3em] hover:shadow-neon hover:scale-105 active:scale-95 transition-all flex items-center gap-3 mx-auto group"
                            >
                                START_SYNC <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    )}

                    {/* Step 2: Strategic Goal Choice */}
                    {step === 2 && (
                        <div className="animate-slide-up">
                            <h2 className="text-2xl font-display font-black text-white tracking-widest text-center mb-12">
                                SELECT <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">PRIMARY_OBJECTIVE</span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {goals.map(goal => (
                                    <button
                                        key={goal.id}
                                        onClick={() => handleGoalSelect(goal.id)}
                                        className="p-6 rounded-2xl bg-black/40 border border-white/5 hover:border-pearl/40 hover:bg-white/[0.03] transition-all text-left group/goal relative overflow-hidden"
                                    >
                                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover/goal:opacity-20 transition-opacity">
                                            <goal.icon size={80} strokeWidth={0.5} />
                                        </div>
                                        <div className="flex items-center gap-4 mb-3 relative z-10">
                                            <div className="p-2 rounded-lg bg-white/5 text-pearl group-hover/goal:bg-pearl group-hover/goal:text-black transition-all">
                                                <goal.icon size={18} />
                                            </div>
                                            <span className="text-[0.65rem] font-black text-white tracking-widest uppercase">NODE_{goal.id}</span>
                                        </div>
                                        <div className="text-lg font-bold text-slate-300 group-hover/goal:text-white transition-colors relative z-10 uppercase tracking-tight">{goal.label}</div>
                                        <div className="text-[0.6rem] font-mono text-slate-600 mt-2 italic group-hover/goal:text-slate-400 transition-colors relative z-10">e.g. "{goal.example}"</div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Step 3: Mission Definition Terminal */}
                    {step === 3 && (
                        <div className="animate-slide-up">
                            <h2 className="text-2xl font-display font-black text-white tracking-widest text-center mb-12">
                                INITIALIZE <span className="text-transparent bg-clip-text bg-gradient-to-r from-pearl to-white">FIRST_SWEEP</span>
                            </h2>
                            <div className="max-w-2xl mx-auto space-y-8">
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">
                                        <span>INPUT_QUERY_PARAMS</span>
                                        <Terminal size={12} />
                                    </div>
                                    <textarea
                                        value={missionQuery}
                                        onChange={(e) => setMissionQuery(e.target.value)}
                                        placeholder="e.g. SaaS CEOs in Austin raising Series A..."
                                        className="w-full bg-black/60 border border-white/10 rounded-2xl p-6 font-mono text-sm text-pearl outline-none focus:border-pearl/40 transition-all placeholder:text-slate-800 shadow-[inner_0_0_20px_rgba(0,0,0,0.5)] h-32"
                                    />
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    <div className="space-y-3">
                                        <span className="text-[0.6rem] font-mono text-slate-500 uppercase tracking-widest">TARGET_PLATFORM</span>
                                        <select
                                            value={platform}
                                            onChange={(e) => setPlatform(e.target.value)}
                                            className="w-full bg-black/60 border border-white/10 rounded-xl p-4 font-mono text-xs text-white outline-none focus:border-pearl/40 cursor-pointer appearance-none"
                                        >
                                            <option value="linkedin">LINKEDIN_CORE</option>
                                            <option value="google_maps">MAPS_INTEL</option>
                                            <option value="producthunt">LAUNCH_RADAR</option>
                                            <option value="tiktok">VIRAL_SIGNALS</option>
                                            <option value="google_news">GLOBAL_NEWS_FEED</option>
                                        </select>
                                    </div>
                                    <div className="flex items-end">
                                        <button
                                            onClick={handleCreateMission}
                                            disabled={creatingMission || !missionQuery.trim()}
                                            className="w-full bg-white text-black font-display font-bold py-4 rounded-xl text-[0.6rem] tracking-[0.3em] hover:shadow-neon transition-all flex items-center justify-center gap-2 group disabled:opacity-30 uppercase"
                                        >
                                            {creatingMission ? <Activity size={14} className="animate-spin" /> : <Rocket size={14} className="group-hover:-translate-y-1 transition-transform" />}
                                            LAUNCH_MISSION
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Swarm Deployment Visual */}
                    {step === 4 && (
                        <div className="text-center animate-slide-up">
                            <div className="mb-10 relative inline-block">
                                <div className="absolute -inset-16 bg-pearl/20 blur-[100px] rounded-full animate-pulse-slow"></div>
                                <div className="p-8 rounded-full bg-black/40 border border-pearl/20 relative z-10 shadow-glow animate-spin-slow">
                                    <Cpu size={64} className="text-pearl" strokeWidth={1} />
                                </div>
                            </div>
                            <h2 className="text-3xl font-display font-black text-white tracking-[0.2em] mb-4 uppercase">SWARM_DEPLOYED</h2>
                            <p className="text-[0.6rem] font-mono text-pearl/50 mb-12 tracking-[0.3em] uppercase">Workers successfully claimed mission #{missionId?.slice(0, 8)}</p>

                            <div className="max-w-md mx-auto bg-black/40 border border-white/5 rounded-2xl p-6 text-left space-y-4">
                                <div className="flex items-center gap-4">
                                    <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-neon-sm"></div>
                                    <span className="text-[0.65rem] font-mono text-slate-400">TELEMETRY_LINK_ESTABLISHED</span>
                                </div>
                                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-emerald-500 w-1/3 animate-pulse"></div>
                                </div>
                                <div className="grid grid-cols-2 gap-4 pt-2">
                                    <div className="flex flex-col">
                                        <span className="text-[0.5rem] font-black text-slate-600 uppercase">Latency</span>
                                        <span className="text-xs font-mono text-white">42ms</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[0.5rem] font-black text-slate-600 uppercase">Verification</span>
                                        <span className="text-xs font-mono text-white">Neural_V3</span>
                                    </div>
                                </div>
                            </div>

                            <button onClick={() => setStep(5)} className="mt-12 text-[0.65rem] font-display font-black text-pearl tracking-[0.5em] underline underline-offset-8 hover:text-white transition-colors uppercase">
                                PROCEED_TO_GRID
                            </button>
                        </div>
                    )}

                    {/* Step 5: Final Ready State */}
                    {step === 5 && (
                        <div className="text-center animate-slide-up">
                            <div className="mb-10 p-6 rounded-[2rem] bg-black/40 border border-emerald-500/20 relative inline-block shadow-glow-sm">
                                <Rocket size={64} className="text-emerald-500" strokeWidth={1} />
                            </div>
                            <h2 className="text-4xl font-display font-black text-white tracking-widest mb-6">ALL_SYSTEMS_GO</h2>
                            <p className="text-sm font-mono text-slate-400 max-w-lg mx-auto leading-relaxed mb-12 uppercase tracking-wide opacity-60">
                                Calibration complete. Your sensory dashboard is now fully synchronized with the global data hive.
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl mx-auto mb-12">
                                <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02] text-left">
                                    <div className="text-[0.5rem] font-black text-pearl uppercase mb-2">PRO_TIP_01</div>
                                    <div className="text-[0.65rem] text-slate-400 font-mono italic leading-relaxed">"High-intent nodes (>80%) are highlighted in your Neural Lattice."</div>
                                </div>
                                <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02] text-left">
                                    <div className="text-[0.5rem] font-black text-emerald-500 uppercase mb-2">PRO_TIP_02</div>
                                    <div className="text-[0.65rem] text-slate-400 font-mono italic leading-relaxed">"Use the Displacement Archive to deploy tactile outreach protocols."</div>
                                </div>
                            </div>

                            <button
                                onClick={handleComplete}
                                className="bg-emerald-500 text-black font-display font-bold py-5 px-16 rounded-2xl text-[0.7rem] tracking-[0.4em] hover:shadow-neon hover:scale-105 active:scale-95 transition-all uppercase"
                            >
                                ENTER_CLARITY_PEARL
                            </button>
                        </div>
                    )}
                </div>

                {/* SKIP BUTTON */}
                {step > 1 && step < 5 && (
                    <button
                        onClick={handleComplete}
                        className="mt-8 text-[0.55rem] font-mono font-bold text-slate-600 hover:text-white transition-colors uppercase tracking-[0.3em]"
                    >
                        BYPASS_INITIATION
                    </button>
                )}
            </div>
        </div>
    )
}
