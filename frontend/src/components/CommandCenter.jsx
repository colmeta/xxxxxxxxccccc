import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Activity, Shield, Users, Radio } from 'lucide-react';

const CommandCenter = ({ session }) => {
    const [stats, setStats] = useState({
        activeMissions: 0,
        totalLeads: 0,
        meshHealth: 98.4,
        stealthEfficiency: 96.2,
        velocityData: []
    });

    useEffect(() => {
        // Mock data fetch for display purposes since backend connection might vary
        setTimeout(() => {
            setStats({
                activeMissions: 5,
                totalLeads: 12430,
                meshHealth: 99.1,
                stealthEfficiency: 97.5,
                velocityData: []
            })
        }, 1000)
    }, []);

    return (
        <div className="space-y-8 animate-slide-up">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-black text-white tracking-tight">
                        SYSTEM <span className="text-pearl">METRICS</span>
                    </h1>
                    <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest font-bold">System Operational | {stats.activeMissions} Active Missions</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-500 text-[0.65rem] font-bold uppercase tracking-wider">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    Network Alive
                </div>
            </div>

            {/* Primary Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard label="Active Missions" value={stats.activeMissions} icon={<Radio size={20} className="text-pearl" />} />
                <MetricCard label="Total Intelligence" value={stats.totalLeads.toLocaleString()} icon={<Users size={20} className="text-purple-400" />} />
                <MetricCard label="Mesh Health" value={`${stats.meshHealth}%`} icon={<Activity size={20} className="text-emerald-400" />} trend="+0.2%" />
                <MetricCard label="Stealth Efficiency" value={`${stats.stealthEfficiency}%`} icon={<Shield size={20} className="text-amber-400" />} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="glass-panel p-8 bg-white/5 lg:col-span-2">
                    <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Lead Acquisition Velocity</h2>
                    <div className="h-64 flex items-end gap-2">
                        {/* Visual Bar Chart Mockup */}
                        {Array.from({ length: 20 }).map((_, i) => (
                            <div key={i} className="flex-1 bg-slate-800 hover:bg-pearl/50 transition-colors rounded-t-sm relative group">
                                <div style={{ height: `${30 + Math.random() * 70}%` }} className="w-full bg-slate-700/50 absolute bottom-0 rounded-t-sm group-hover:bg-pearl"></div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="glass-panel p-8 bg-white/5">
                    <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Channel ROI Distribution</h2>
                    <div className="space-y-6">
                        <ROIBar label="LinkedIn" value={85} color="bg-blue-500" />
                        <ROIBar label="Google Maps" value={64} color="bg-emerald-500" />
                        <ROIBar label="Direct" value={45} color="bg-purple-500" />
                        <ROIBar label="Social" value={32} color="bg-amber-500" />
                    </div>
                </div>
            </div>
        </div>
    );
};

const MetricCard = ({ label, value, icon, trend }) => (
    <div className="glass-panel p-6 bg-white/5 hover:-translate-y-1 transition-transform duration-300">
        <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-white/5 rounded-lg">{icon}</div>
            {trend && <span className="text-[0.65rem] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">{trend}</span>}
        </div>
        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">{label}</div>
        <div className="text-2xl font-black text-white mt-1">{value}</div>
    </div>
);

const ROIBar = ({ label, value, color }) => (
    <div>
        <div className="flex justify-between text-xs font-bold mb-2">
            <span className="text-slate-300">{label}</span>
            <span className="text-white">{value}%</span>
        </div>
        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div className={`h-full ${color}`} style={{ width: `${value}%` }}></div>
        </div>
    </div>
);

export default CommandCenter;
