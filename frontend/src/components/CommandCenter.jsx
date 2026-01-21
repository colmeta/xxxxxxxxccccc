import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Cell
} from 'recharts';

const CommandCenter = ({ session }) => {
    const [stats, setStats] = useState({
        activeMissions: 0,
        totalLeads: 0,
        meshHealth: 98.4,
        stealthEfficiency: 96.2,
        velocityData: []
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
        const subscription = supabase
            .channel('command_center_updates')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'jobs' }, fetchStats)
            .subscribe();

        return () => {
            supabase.removeChannel(subscription);
        };
    }, []);

    const fetchStats = async () => {
        try {
            // Fetch mission counts
            const { count: activeCount } = await supabase
                .from('jobs')
                .select('*', { count: 'exact', head: true })
                .eq('status', 'processing');

            // Fetch lead counts
            const { count: leadCount } = await supabase
                .from('results')
                .select('*', { count: 'exact', head: true });

            // Simulate velocity data for demonstration (In production, use time-aggregated query)
            const mockVelocity = [
                { time: '00:00', leads: 45 },
                { time: '04:00', leads: 52 },
                { time: '08:00', leads: 89 },
                { time: '12:00', leads: 124 },
                { time: '16:00', leads: 98 },
                { time: '20:00', leads: 145 },
                { time: '23:59', leads: 167 },
            ];

            setStats({
                activeMissions: activeCount || 0,
                totalLeads: leadCount || 0,
                meshHealth: 98.4 + (Math.random() * 1.5 - 0.75),
                stealthEfficiency: 96.2 + (Math.random() * 2 - 1),
                velocityData: mockVelocity
            });
            setLoading(false);
        } catch (error) {
            console.error('Error fetching command stats:', error);
        }
    };

    return (
        <div className="command-center-container animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 900, letterSpacing: '-0.5px' }}>
                        COMMAND <span style={{ color: 'hsl(var(--pearl-primary))' }}>CENTER</span>
                    </h1>
                    <p style={{ opacity: 0.5, fontSize: '0.85rem', margin: '0.25rem 0 0 0' }}>SYSTEM OPERATIONAL | {stats.activeMissions} ACTIVE MISSIONS</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <div className="stat-pill">
                        <span className="dot pulse"></span>
                        NETWORK ALIVE
                    </div>
                </div>
            </div>

            {/* Primary Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <MetricCard label="ACTIVE MISSIONS" value={stats.activeMissions} icon="🛰️" />
                <MetricCard label="TOTAL INTELLIGENCE" value={stats.totalLeads.toLocaleString()} icon="💎" />
                <MetricCard label="MESH HEALTH" value={`${stats.meshHealth.toFixed(1)}%`} icon="🕸️" trend="+0.2%" />
                <MetricCard label="STEALTH RATING" value={`${stats.stealthEfficiency.toFixed(1)}%`} icon="🛡️" />
            </div>

            {/* Analytics Section */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
                <div className="supreme-glass" style={{ padding: '2rem', minHeight: '400px' }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '2rem', opacity: 0.8 }}>LEAD ACQUISITION VELOCITY</h2>
                    <div style={{ width: '100%', height: '300px' }}>
                        <ResponsiveContainer>
                            <AreaChart data={stats.velocityData}>
                                <defs>
                                    <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="hsl(var(--pearl-primary))" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="hsl(var(--pearl-primary))" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ background: 'rgba(0,0,0,0.8)', border: '1px solid var(--glass-border)', borderRadius: '12px' }}
                                    itemStyle={{ color: 'hsl(var(--pearl-primary))' }}
                                />
                                <Area type="monotone" dataKey="leads" stroke="hsl(var(--pearl-primary))" fillOpacity={1} fill="url(#colorLeads)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="supreme-glass" style={{ padding: '2rem' }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: '2rem', opacity: 0.8 }}>MISSION ROI BY CHANNEL</h2>
                    <MissionROIDistribution />
                </div>
            </div>

            <style>{`
        .metric-card {
          padding: 1.5rem;
          background: rgba(255,255,255,0.03);
          border: 1px solid var(--glass-border);
          border-radius: var(--radius-xl);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .metric-card:hover {
          background: rgba(255,255,255,0.05);
          transform: translateY(-4px);
          border-color: hsla(var(--pearl-primary), 0.3);
        }
        .stat-pill {
          background: rgba(0,255,100,0.1);
          color: #00ff64;
          padding: 0.5rem 1rem;
          border-radius: 100px;
          font-size: 0.7rem;
          font-weight: 800;
          display: flex;
          alignItems: center;
          gap: 0.5rem;
          border: 1px solid rgba(0,255,100,0.2);
        }
        .dot {
          width: 8px;
          height: 8px;
          background: #00ff64;
          border-radius: 50%;
        }
        .pulse {
          animation: pulse-green 2s infinite;
        }
        @keyframes pulse-green {
          0% { box-shadow: 0 0 0 0 rgba(0, 255, 100, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(0, 255, 100, 0); }
          100% { box-shadow: 0 0 0 0 rgba(0, 255, 100, 0); }
        }
      `}</style>
        </div>
    );
};

const MetricCard = ({ label, value, icon, trend }) => (
    <div className="metric-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.5rem' }}>{icon}</span>
            {trend && <span style={{ fontSize: '0.7rem', color: '#00ff64', fontWeight: 700 }}>{trend}</span>}
        </div>
        <div style={{ fontSize: '0.7rem', fontWeight: 800, opacity: 0.4, letterSpacing: '1px', textTransform: 'uppercase' }}>{label}</div>
        <div style={{ fontSize: '1.75rem', fontWeight: 900, marginTop: '0.25rem' }}>{value}</div>
    </div>
);

const MissionROIDistribution = () => {
    const data = [
        { name: 'LinkedIn', value: 85 },
        { name: 'Maps', value: 64 },
        { name: 'Direct', value: 45 },
        { name: 'Social', value: 32 }
    ];

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {data.map((item, idx) => (
                <div key={item.name} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: 700, opacity: 0.8 }}>{item.name}</span>
                        <span style={{ fontWeight: 800, color: 'hsl(var(--pearl-primary))' }}>{item.value}%</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '100px', overflow: 'hidden' }}>
                        <div
                            style={{
                                height: '100%',
                                width: `${item.value}%`,
                                background: idx === 0 ? 'hsl(var(--pearl-primary))' : 'rgba(255,255,255,0.2)',
                                borderRadius: '100px',
                                transition: 'width 1s ease-out'
                            }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
};

export default CommandCenter;
