import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export default function AnalyticsLab() {
    const [stats, setStats] = useState({ groupA: 0, groupB: 0, accuracyA: 0, accuracyB: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    async function fetchStats() {
        const { data, error } = await supabase
            .from('jobs')
            .select(`
                ab_test_group,
                results (
                    verified,
                    clarity_score
                )
            `)
            .eq('status', 'completed');

        if (data) {
            const groupA = data.filter(j => j.ab_test_group === 'A');
            const groupB = data.filter(j => j.ab_test_group === 'B');

            const getAcc = (group) => {
                const verifiedCount = group.filter(j => j.results[0]?.verified).length;
                return group.length > 0 ? (verifiedCount / group.length) * 100 : 0;
            };

            setStats({
                countA: groupA.length,
                countB: groupB.length,
                accuracyA: getAcc(groupA).toFixed(1),
                accuracyB: getAcc(groupB).toFixed(1)
            });
        }
        setLoading(false);
    }

    return (
        <div className="supreme-glass" style={{ padding: '2rem', marginTop: '2rem' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ color: 'hsl(var(--nexus-accent))' }}>🧪</span> ANALYTICS LAB: STRATEGY PERFORMANCE
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Group A */}
                <div style={{ padding: '1.5rem', borderRadius: '15px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.5rem', fontWeight: 700 }}>STRATEGY A: STEALTH (CONTROL)</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900 }}>{stats.accuracyA}%</div>
                        <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>{stats.countA} Missions</div>
                    </div>
                    <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '1rem', overflow: 'hidden' }}>
                        <div style={{ width: `${stats.accuracyA}%`, height: '100%', background: 'hsl(var(--nexus-primary))' }}></div>
                    </div>
                </div>

                {/* Group B */}
                <div style={{ padding: '1.5rem', borderRadius: '15px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.5rem', fontWeight: 700 }}>STRATEGY B: AGGRESSIVE (LAB)</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 900 }}>{stats.accuracyB}%</div>
                        <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>{stats.countB} Missions</div>
                    </div>
                    <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '1rem', overflow: 'hidden' }}>
                        <div style={{ width: `${stats.accuracyB}%`, height: '100%', background: 'hsl(var(--nexus-accent))' }}></div>
                    </div>
                </div>
            </div>
        </div>
    );
}
