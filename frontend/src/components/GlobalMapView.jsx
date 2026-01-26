import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Globe, MapPin, Activity, ShieldCheck, Target, Zap, Cpu } from 'lucide-react';

// Custom Tactical Ping Icon
const createTacticalPing = (color = '#00f7ff') => {
    return L.divIcon({
        className: 'tactical-ping',
        html: `
            <div class="relative flex items-center justify-center w-6 h-6">
                <div class="absolute inset-0 rounded-full bg-[${color}] opacity-20 animate-ping"></div>
                <div class="absolute inset-1 rounded-full bg-[${color}] opacity-40 animate-pulse"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-[${color}] shadow-[0_0_8px_${color}]"></div>
            </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
};

const GlobalMapView = ({ session }) => {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [center, setCenter] = useState([20, 0]);
    const [zoom, setZoom] = useState(2);

    useEffect(() => {
        fetchGeoData();
    }, []);

    const fetchGeoData = async () => {
        try {
            const token = session.access_token;
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/results/geodata`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setLeads(data);
            }
        } catch (error) {
            console.error('Error fetching geodata:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="h-[650px] flex flex-col items-center justify-center glass-panel bg-black/40 border-white/5 relative overflow-hidden group">
                <div className="absolute inset-0 bg-scanline opacity-10 pointer-events-none"></div>
                <div className="relative">
                    <div className="absolute -inset-12 bg-pearl/10 blur-3xl rounded-full animate-pulse-slow"></div>
                    <Globe size={80} strokeWidth={1} className="text-pearl animate-spin-slow relative z-10 opacity-30" />
                </div>
                <div className="mt-8 text-center space-y-2 relative z-10">
                    <p className="text-xl font-display font-black text-white tracking-[0.4em] uppercase">Initializing Swarm</p>
                    <p className="text-[0.6rem] font-mono text-pearl/50 uppercase tracking-widest px-4 py-1 border border-pearl/20 rounded">Syncing Global Telemetry...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-[750px] rounded-3xl overflow-hidden border border-pearl/10 relative shadow-2xl animate-slide-up group">

            {/* Map HUD Overlay */}
            <div className="absolute top-6 left-6 z-[1000] glass-panel p-6 min-w-[280px] bg-black/60 backdrop-blur-xl border-pearl/20">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-pearl/10 text-pearl group-hover:shadow-neon transition-all">
                        <Globe size={18} />
                    </div>
                    <div>
                        <h2 className="text-sm font-display font-black text-white tracking-widest uppercase">GLOBAL_SWARM</h2>
                        <div className="text-[0.5rem] font-mono text-pearl/50 flex items-center gap-1 uppercase tracking-widest">
                            <ShieldCheck size={10} className="text-pearl" />
                            NETWORK_SECURE
                        </div>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.03] border border-white/5">
                        <div className="space-y-1">
                            <span className="text-[0.55rem] font-bold text-slate-500 uppercase tracking-widest">Active Signals</span>
                            <div className="flex items-center gap-2">
                                <Activity size={12} className="text-emerald-500 animate-pulse" />
                                <span className="text-xl font-display font-black text-emerald-500">{leads.length}</span>
                            </div>
                        </div>
                        <div className="h-10 w-px bg-white/10"></div>
                        <div className="space-y-1 text-right">
                            <span className="text-[0.55rem] font-bold text-slate-500 uppercase tracking-widest">Hotspots</span>
                            <div className="flex items-center gap-2 justify-end">
                                <span className="text-xl font-display font-black text-pearl">03</span>
                                <Target size={12} className="text-pearl" />
                            </div>
                        </div>
                    </div>

                    <div className="p-3 rounded-lg bg-black/40 border border-white/5">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-[0.55rem] font-mono text-slate-500">SYNC_STATUS</span>
                            <span className="text-[0.55rem] font-mono text-emerald-500">100%</span>
                        </div>
                        <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                            <div className="h-full bg-pearl w-full animate-pulse-slow"></div>
                        </div>
                    </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/5">
                    <div className="text-[0.5rem] font-mono text-slate-600 uppercase tracking-widest flex items-center gap-2">
                        <Cpu size={10} /> SENSORY_LATTICE_V2.6
                    </div>
                </div>
            </div>

            {/* Tactical Stream (Bottom Right Overlay) */}
            <div className="absolute bottom-6 right-6 z-[1000] glass-panel p-4 w-64 bg-black/60 border-pearl/10 hidden xl:block">
                <div className="text-[0.6rem] font-black text-slate-500 tracking-widest uppercase mb-4 flex justify-between">
                    <span>LIVE_STREAM</span>
                    <span className="animate-pulse text-pearl underline underline-offset-4">DECRYPTING</span>
                </div>
                <div className="space-y-3">
                    {leads.slice(0, 3).map((l, i) => (
                        <div key={i} className="flex items-center gap-3 animate-slide-up" style={{ animationDelay: `${i * 200}ms` }}>
                            <div className="w-1 h-8 bg-pearl/20 rounded-full"></div>
                            <div className="min-w-0">
                                <div className="text-[0.65rem] font-bold text-white truncate">{l.data_payload?.company || 'INC_NODE'}</div>
                                <div className="text-[0.55rem] font-mono text-slate-500">INTENT: {l.intent_score}% // {l.data_payload?.location || 'COORD'}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <MapContainer
                center={center}
                zoom={zoom}
                className="h-full w-full bg-black"
                scrollWheelZoom={true}
                zoomControl={false}
            >
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; CARTO'
                />

                {leads.map((lead) => (
                    <Marker
                        key={lead.id}
                        position={[lead.geo_lat, lead.geo_lng]}
                        icon={createTacticalPing(lead.intent_score > 70 ? '#00f7ff' : '#f59e0b')}
                    >
                        <Popup className="tactical-popup border-none">
                            <div className="p-4 bg-black border border-pearl/20 rounded-xl shadow-2xl relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-2 opacity-10">
                                    <Target size={40} className="text-pearl" />
                                </div>
                                <h3 className="text-xs font-display font-black text-white tracking-widest uppercase border-b border-white/10 pb-2 mb-2">
                                    {lead.data_payload?.name || 'NODE_UNNAMED'}
                                </h3>
                                <p className="text-[0.65rem] font-mono text-slate-400 mb-3">
                                    {lead.data_payload?.title || lead.data_payload?.industry || 'Classified Profile'}
                                </p>

                                <div className="flex justify-between items-center bg-white/[0.05] p-2 rounded border border-white/5">
                                    <span className="text-[0.5rem] font-black text-slate-500 uppercase tracking-widest">Intent Rank</span>
                                    <span className={`text-xs font-black font-mono ${lead.intent_score > 70 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                        +{lead.intent_score || 0}%
                                    </span>
                                </div>
                                <div className="mt-3 flex justify-end">
                                    <div className="text-[0.5rem] font-bold text-pearl uppercase underline underline-offset-4 cursor-pointer hover:text-white transition-colors">
                                        VIEW_LATTICE_DETAILS
                                    </div>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            <style>{`
                .tactical-popup .leaflet-popup-content-wrapper {
                    background: transparent !important;
                    border: none !important;
                    box-shadow: none !important;
                    padding: 0 !important;
                }
                .tactical-popup .leaflet-popup-content {
                    margin: 0 !important;
                    width: 240px !important;
                }
                .tactical-popup .leaflet-popup-tip-container {
                    display: none !important;
                }
                .leaflet-container {
                    background: #000 !important;
                }
                @keyframes scan {
                    0% { top: 0; }
                    100% { top: 100%; }
                }
                .animate-scan {
                    animation: scan 3s linear infinite;
                }
            `}</style>
        </div>
    );
};

export default GlobalMapView;

