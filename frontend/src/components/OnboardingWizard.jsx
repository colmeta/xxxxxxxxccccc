import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import '../styles/design-tokens.css'

export default function OnboardingWizard({ session, onComplete }) {
    const [step, setStep] = useState(1)
    const [userGoal, setUserGoal] = useState(null)
    const [missionQuery, setMissionQuery] = useState('')
    const [platform, setPlatform] = useState('linkedin')
    const [creatingMission, setCreatingMission] = useState(false)
    const [missionId, setMissionId] = useState(null)

    // Check if onboarding was already completed
    useEffect(() => {
        const completed = localStorage.getItem('onboarding_completed')
        if (completed === 'true') {
            onComplete()
        }
    }, [])

    // Save progress
    useEffect(() => {
        localStorage.setItem('onboarding_step', step.toString())
    }, [step])

    const goals = [
        { id: 'sales', label: 'Sales Leads (B2B)', icon: '💼', example: 'SaaS CEOs in Austin raising Series A' },
        { id: 'product', label: 'Product Research', icon: '🛍️', example: 'Top Shopify stores in fashion niche' },
        { id: 'competitor', label: 'Competitor Intel', icon: '🔍', example: 'Companies using competitor XYZ' },
        { id: 'real-estate', label: 'Real Estate Leads', icon: '🏠', example: 'Commercial properties in NYC' }
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
                    priority: 5, // High priority for first mission
                    status: 'queued'
                })
                .select()
                .single()

            if (error) throw error
            setMissionId(data.id)
            setStep(4)
        } catch (error) {
            console.error('Mission creation error:', error)
            alert('Error creating mission. Please try again.')
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
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.95)',
            backdropFilter: 'blur(10px)',
            zIndex: 10000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            animation: 'fade-in 0.3s'
        }}>
            {/* Progress Bar */}
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                height: '4px',
                background: 'rgba(255,255,255,0.1)'
            }}>
                <div style={{
                    height: '100%',
                    width: `${progress}%`,
                    background: 'linear-gradient(90deg, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))',
                    transition: 'width 0.5s'
                }} />
            </div>

            {/* Modal */}
            <div className="glass-card-premium animate-scale-in" style={{
                maxWidth: '600px',
                width: '100%',
                padding: '3rem',
                textAlign: 'center'
            }}>
                {/* Step 1: Welcome */}
                {step === 1 && (
                    <>
                        <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>👋</div>
                        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '1rem', background: 'linear-gradient(to right, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            Welcome to Pearl!
                        </h1>
                        <p style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.7)', marginBottom: '2rem', lineHeight: '1.6' }}>
                            The Federal Reserve of Information<br />for AI Agents & Sales Teams
                        </p>
                        <button onClick={() => setStep(2)} className="btn-premium" style={{ fontSize: '1rem', padding: '1rem 2rem' }}>
                            Let's Get Started →
                        </button>
                    </>
                )}

                {/* Step 2: Choose Goal */}
                {step === 2 && (
                    <>
                        <h2 style={{ fontSize: '1.8rem', fontWeight: 900, marginBottom: '1rem', color: '#fff' }}>
                            What do you want to find?
                        </h2>
                        <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.6)', marginBottom: '2rem' }}>
                            Choose your primary use case
                        </p>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                            {goals.map(goal => (
                                <button
                                    key={goal.id}
                                    onClick={() => handleGoalSelect(goal.id)}
                                    className="interactive-card"
                                    style={{
                                        background: 'rgba(255,255,255,0.03)',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '12px',
                                        padding: '1.5rem',
                                        textAlign: 'left',
                                        cursor: 'pointer'
                                    }}
                                >
                                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{goal.icon}</div>
                                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
                                        {goal.label}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>
                                        e.g. "{goal.example}"
                                    </div>
                                </button>
                            ))}
                        </div>
                    </>
                )}

                {/* Step 3: Create First Mission */}
                {step === 3 && (
                    <>
                        <h2 style={{ fontSize: '1.8rem', fontWeight: 900, marginBottom: '1rem', color: '#fff' }}>
                            Create Your First Mission
                        </h2>
                        <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.6)', marginBottom: '2rem' }}>
                            Tell the Oracle what to find
                        </p>
                        <div style={{ textAlign: 'left', marginBottom: '2rem' }}>
                            <label style={{ fontSize: '0.8rem', fontWeight: 700, color: 'rgba(255,255,255,0.7)', display: 'block', marginBottom: '0.5rem' }}>
                                What are you looking for?
                            </label>
                            <textarea
                                value={missionQuery}
                                onChange={(e) => setMissionQuery(e.target.value)}
                                placeholder="e.g., SaaS CEOs in Austin raising Series A funding"
                                rows={4}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '12px',
                                    color: '#fff',
                                    fontSize: '0.95rem',
                                    resize: 'vertical',
                                    marginBottom: '1rem'
                                }}
                            />
                            <label style={{ fontSize: '0.8rem', fontWeight: 700, color: 'rgba(255,255,255,0.7)', display: 'block', marginBottom: '0.5rem' }}>
                                Platform
                            </label>
                            <select
                                value={platform}
                                onChange={(e) => setPlatform(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '1rem',
                                    background: 'rgba(0,0,0,0.3)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '12px',
                                    color: '#fff',
                                    fontSize: '0.95rem',
                                    cursor: 'pointer'
                                }}
                            >
                                <option value="linkedin">LinkedIn</option>
                                <option value="google_maps">Google Maps</option>
                                <option value="producthunt">Product Hunt</option>
                                <option value="tiktok">TikTok</option>
                                <option value="google_news">Google News</option>
                            </select>
                        </div>
                        <button
                            onClick={handleCreateMission}
                            disabled={creatingMission || !missionQuery.trim()}
                            className="btn-premium"
                            style={{ fontSize: '1rem', padding: '1rem 2rem' }}
                        >
                            {creatingMission ? '⏳ Creating...' : '🚀 Launch Mission'}
                        </button>
                    </>
                )}

                {/* Step 4: Watch Hydra Work */}
                {step === 4 && (
                    <>
                        <div className="animate-pulse-glow" style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🛸</div>
                        <h2 style={{ fontSize: '1.8rem', fontWeight: 900, marginBottom: '1rem', color: '#fff' }}>
                            Hydra is Searching...
                        </h2>
                        <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.6)', marginBottom: '2rem' }}>
                            Our global swarm is scanning {platform} for your targets
                        </p>
                        <div style={{
                            background: 'rgba(0,0,0,0.3)',
                            borderRadius: '12px',
                            padding: '1.5rem',
                            textAlign: 'left',
                            marginBottom: '2rem'
                        }}>
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                                <div className="spinner" />
                                <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.8)' }}>
                                    ✅ Mission queued successfully
                                </div>
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', marginBottom: '0.5rem' }}>
                                🔍 Workers will claim your job in seconds
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', marginBottom: '0.5rem' }}>
                                🧠 AI will verify and score each lead
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)' }}>
                                📊 Results will appear in the Intelligence View
                            </div>
                        </div>
                        <button onClick={() => setStep(5)} className="btn-premium" style={{ fontSize: '1rem', padding: '1rem 2rem' }}>
                            Continue →
                        </button>
                    </>
                )}

                {/* Step 5: Complete */}
                {step === 5 && (
                    <>
                        <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🎉</div>
                        <h2 style={{ fontSize: '1.8rem', fontWeight: 900, marginBottom: '1rem', color: '#fff' }}>
                            You're All Set!
                        </h2>
                        <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.6)', marginBottom: '2rem', lineHeight: '1.6' }}>
                            Your mission is running. Check the <strong style={{ color: 'hsl(var(--pearl-primary))' }}>Live Feed</strong> to watch progress in real-time, or visit <strong style={{ color: 'hsl(var(--pearl-primary))' }}>Intelligence View</strong> to see results.
                        </p>
                        <div style={{
                            background: 'rgba(147,51,234,0.1)',
                            border: '1px solid rgba(147,51,234,0.3)',
                            borderRadius: '12px',
                            padding: '1.5rem',
                            textAlign: 'left',
                            marginBottom: '2rem'
                        }}>
                            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'rgba(147,51,234,1)', marginBottom: '0.5rem' }}>
                                💡 PRO TIPS
                            </div>
                            <ul style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', lineHeight: '1.8', paddingLeft: '1.5rem', margin: 0 }}>
                                <li>High-intent leads (score &gt; 80) are auto-prioritized</li>
                                <li>Connect a CRM webhook for auto-sync</li>
                                <li>Monitor the Swarm Observatory to see global workers</li>
                                <li>Use Bulk Mission Control for CSV uploads</li>
                            </ul>
                        </div>
                        <button onClick={handleComplete} className="btn-premium" style={{ fontSize: '1rem', padding: '1rem 2rem' }}>
                            Explore Pearl →
                        </button>
                    </>
                )}

                {/* Skip Button (bottom-right) */}
                {step > 1 && step < 5 && (
                    <button
                        onClick={handleComplete}
                        style={{
                            position: 'absolute',
                            bottom: '1rem',
                            right: '1rem',
                            background: 'none',
                            border: 'none',
                            color: 'rgba(255,255,255,0.4)',
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            textDecoration: 'underline'
                        }}
                    >
                        Skip for now
                    </button>
                )}
            </div>
        </div>
    )
}
