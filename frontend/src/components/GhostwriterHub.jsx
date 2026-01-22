import React, { useState, useEffect } from 'react';
import { Mail, Plus, Send, Clock, AlertCircle, ChevronRight, Edit3 } from 'lucide-react';

const GhostwriterHub = ({ session }) => {
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newCampaign, setNewCampaign] = useState({ name: '', description: '' });
    const [selectedCampaign, setSelectedCampaign] = useState(null);

    useEffect(() => {
        fetchCampaigns();
    }, []);

    const fetchCampaigns = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/campaigns/`, {
                headers: { 'Authorization': `Bearer ${session.access_token}` }
            });
            if (response.ok) {
                setCampaigns(await response.json());
            }
        } catch (error) {
            console.error('Error fetching campaigns:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateCampaign = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/campaigns/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newCampaign)
            });
            if (response.ok) {
                setShowCreate(false);
                setNewCampaign({ name: '', description: '' });
                fetchCampaigns();
            }
        } catch (error) {
            console.error('Error creating campaign:', error);
        }
    };

    if (loading) return <div className="loading">SYNCING GHOSTWRITER ENGINE...</div>;

    return (
        <div className="ghostwriter-hub" style={{ animation: 'fadeIn 0.5s ease-out' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.5rem', fontWeight: 900, letterSpacing: '-1px' }}>✍️ GHOSTWRITER v2</h1>
                    <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginTop: '0.25rem' }}>Autonomous Engagement & Lead Nurturing Swarm</p>
                </div>
                <button
                    onClick={() => setShowCreate(true)}
                    className="supreme-button"
                    style={{ padding: '0.75rem 1.5rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    <Plus size={16} /> NEW CAMPAIGN
                </button>
            </div>

            {showCreate && (
                <div className="card" style={{ marginBottom: '2rem', border: '1px solid hsl(var(--pearl-primary))' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '1rem' }}>INITIALIZE NEW CAMPAIGN</h3>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <input
                            type="text"
                            placeholder="Campaign Name (e.g. Austin Tech Outreach)"
                            value={newCampaign.name}
                            onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                            className="supreme-input"
                        />
                        <textarea
                            placeholder="Description & Goal"
                            value={newCampaign.description}
                            onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                            className="supreme-input"
                            style={{ minHeight: '100px' }}
                        />
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button onClick={handleCreateCampaign} className="supreme-button">CREATE</button>
                            <button onClick={() => setShowCreate(false)} className="supreme-button" style={{ background: 'rgba(255,255,255,0.05)', color: '#fff' }}>CANCEL</button>
                        </div>
                    </div>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
                {/* Campaign List */}
                <div className="campaign-list">
                    <h2 style={{ fontSize: '0.9rem', fontWeight: 800, color: 'rgba(255,255,255,0.4)', marginBottom: '1rem' }}>ACTIVE CAMPAIGNS</h2>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {campaigns.map(c => (
                            <div
                                key={c.id}
                                onClick={() => setSelectedCampaign(c)}
                                className="card"
                                style={{
                                    cursor: 'pointer',
                                    border: selectedCampaign?.id === c.id ? '1px solid hsl(var(--pearl-primary))' : '1px solid rgba(255,255,255,0.05)',
                                    background: selectedCampaign?.id === c.id ? 'rgba(255,255,255,0.05)' : 'none'
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontWeight: 800 }}>{c.name}</span>
                                    <span style={{ fontSize: '0.6rem', color: 'hsl(var(--pearl-primary))' }}>{c.outreach_sequences?.length || 0} STEPS</span>
                                </div>
                                <p style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', marginTop: '0.5rem' }}>{c.description}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Sequence Editor */}
                <div className="sequence-editor">
                    {selectedCampaign ? (
                        <div className="card">
                            <h2 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Edit3 size={18} /> SEQUENCE: {selectedCampaign.name}
                            </h2>

                            <div style={{ display: 'grid', gap: '1.5rem' }}>
                                {selectedCampaign.outreach_sequences?.length > 0 ? (
                                    selectedCampaign.outreach_sequences.sort((a, b) => a.step_order - b.step_order).map((s, idx) => (
                                        <div key={s.id} style={{ display: 'flex', gap: '1rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'hsl(var(--pearl-primary))', color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '0.8rem' }}>
                                                    {idx + 1}
                                                </div>
                                                {idx < selectedCampaign.outreach_sequences.length - 1 && (
                                                    <div style={{ width: '2px', flex: 1, background: 'rgba(255,255,255,0.1)', margin: '0.5rem 0' }} />
                                                )}
                                            </div>
                                            <div style={{ flex: 1, background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                                    <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>{s.template_subject}</span>
                                                    <span style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.4)' }}>DELAY: {s.delay_days} DAYS</span>
                                                </div>
                                                <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', lineHeight: '1.5' }}>{s.template_body}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255,255,255,0.3)' }}>
                                        <Mail size={40} style={{ marginBottom: '1rem', opacity: 0.2 }} />
                                        <p style={{ fontSize: '0.8rem' }}>No sequences defined. Add your first step to start automation.</p>
                                    </div>
                                )}

                                <button
                                    className="supreme-button"
                                    style={{ background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px dashed rgba(255,255,255,0.2)', marginTop: '1rem' }}
                                >
                                    + ADD SEQUENCE STEP
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.2)', background: 'rgba(0,0,0,0.1)', borderRadius: '16px', border: '1px dashed rgba(255,255,255,0.05)' }}>
                            <div style={{ textAlign: 'center' }}>
                                <Send size={40} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                                <p style={{ fontWeight: 700, letterSpacing: '1px' }}>SELECT A CAMPAIGN TO VIEW SEQUENCE</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GhostwriterHub;
