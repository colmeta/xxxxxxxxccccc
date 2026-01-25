import React, { useState, useEffect } from 'react';
import { Mail, Plus, Send, Edit3, MessageCircle } from 'lucide-react';
import { SkeletonLoader } from './EmptyStates';

const GhostwriterHub = ({ session }) => {
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newCampaign, setNewCampaign] = useState({ name: '', description: '' });
    const [selectedCampaign, setSelectedCampaign] = useState(null);

    useEffect(() => {
        // Fetch logic would go here
        // Simulating data for now since we don't have the backend active for this demo
        setTimeout(() => {
            setCampaigns([
                { id: 1, name: 'Austin Tech Outreach', description: 'Targeting CTOs for recruitment', outreach_sequences: [{ id: 1, template_subject: 'Intro', delay_days: 0, template_body: 'Hi...' }] },
                { id: 2, name: 'Real Estate Investors', description: 'Miami high-net worth', outreach_sequences: [] }
            ])
            setLoading(false)
        }, 1000)
    }, []);

    const handleCreateCampaign = () => {
        // Create mock campaign
        setCampaigns([...campaigns, { id: campaigns.length + 1, ...newCampaign, outreach_sequences: [] }])
        setShowCreate(false)
        setNewCampaign({ name: '', description: '' })
    }

    if (loading) return <SkeletonLoader count={3} type="card" />;

    return (
        <div className="space-y-6 animate-slide-up">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-xl font-black text-white flex items-center gap-2">
                        <Edit3 className="text-pearl" size={24} /> GHOSTWRITER v2
                    </h1>
                    <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest font-bold">Autonomous Engagement Swarm</p>
                </div>
                <button
                    onClick={() => setShowCreate(true)}
                    className="btn-primary"
                >
                    <Plus size={16} className="mr-2" /> NEW CAMPAIGN
                </button>
            </div>

            {showCreate && (
                <div className="glass-panel p-6 border-pearl/50">
                    <h3 className="text-sm font-bold text-white mb-4 uppercase">Initialize New Campaign</h3>
                    <div className="space-y-4">
                        <input
                            type="text"
                            placeholder="Campaign Name (e.g. Austin Tech Outreach)"
                            value={newCampaign.name}
                            onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                            className="input-cyber"
                        />
                        <textarea
                            placeholder="Description & Goal"
                            value={newCampaign.description}
                            onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                            className="input-cyber min-h-[100px]"
                        />
                        <div className="flex gap-2">
                            <button onClick={handleCreateCampaign} className="btn-primary">CREATE</button>
                            <button onClick={() => setShowCreate(false)} className="btn-ghost">CANCEL</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Campaign List */}
                <div className="lg:col-span-1 space-y-3">
                    <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Active Campaigns</h2>
                    {campaigns.map(c => (
                        <div
                            key={c.id}
                            onClick={() => setSelectedCampaign(c)}
                            className={`glass-panel p-4 cursor-pointer transition-all ${selectedCampaign?.id === c.id
                                    ? 'bg-pearl/10 border-pearl/30 shadow-glow'
                                    : 'bg-white/5 hover:bg-white/10'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className={`font-bold ${selectedCampaign?.id === c.id ? 'text-white' : 'text-slate-300'}`}>{c.name}</span>
                                <span className="badge bg-slate-800 text-pearl border-white/5">{c.outreach_sequences?.length || 0} STEPS</span>
                            </div>
                            <p className="text-xs text-slate-500">{c.description}</p>
                        </div>
                    ))}
                </div>

                {/* Sequence Editor */}
                <div className="lg:col-span-2">
                    {selectedCampaign ? (
                        <div className="glass-panel p-6 bg-slate-900/50">
                            <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2 border-b border-white/5 pb-4">
                                <Mail size={18} /> SEQUENCE EDITOR: <span className="text-pearl">{selectedCampaign.name}</span>
                            </h2>

                            <div className="space-y-6">
                                {selectedCampaign.outreach_sequences?.length > 0 ? (
                                    selectedCampaign.outreach_sequences.sort((a, b) => a.step_order - b.step_order).map((s, idx) => (
                                        <div key={s.id} className="flex gap-4">
                                            <div className="flex flex-col items-center">
                                                <div className="w-8 h-8 rounded-full bg-slate-800 border-2 border-pearl text-pearl flex items-center justify-center font-black text-xs">
                                                    {idx + 1}
                                                </div>
                                                {idx < selectedCampaign.outreach_sequences.length - 1 && (
                                                    <div className="w-0.5 flex-1 bg-white/10 my-2" />
                                                )}
                                            </div>
                                            <div className="flex-1 p-4 bg-white/5 rounded-xl border border-white/5">
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="font-bold text-sm text-white">{s.template_subject}</span>
                                                    <span className="text-[0.6rem] font-bold text-slate-500 bg-black/20 px-2 py-1 rounded">DELAY: {s.delay_days} DAYS</span>
                                                </div>
                                                <p className="text-xs text-slate-400 leading-relaxed font-mono">{s.template_body}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-12 text-slate-600">
                                        <MessageCircle size={40} className="mx-auto mb-3 opacity-20" />
                                        <p className="text-xs uppercase tracking-widest font-bold">No sequences defined. Add steps to automate.</p>
                                    </div>
                                )}

                                <button
                                    className="btn-ghost w-full border border-dashed border-white/20 text-slate-400 hover:text-white"
                                >
                                    + ADD SEQUENCE STEP
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center p-12 text-slate-600 border border-dashed border-white/10 rounded-2xl bg-white/5">
                            <div className="text-center">
                                <Edit3 size={40} className="mx-auto mb-3 opacity-20" />
                                <p className="text-xs uppercase tracking-widest font-bold">Select a campaign to edit sequence</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GhostwriterHub;
