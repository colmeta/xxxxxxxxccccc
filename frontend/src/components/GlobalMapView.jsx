import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Globe, MapPin, Activity } from 'lucide-react';

// Fix for default marker icons in Leaflet + React
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const GlobalMapView = ({ session }) => {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [center, setCenter] = useState([20, 0]); // Default center of the world
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
            <div className="h-[600px] flex items-center justify-center bg-slate-900/40 rounded-2xl border border-white/5 animate-pulse">
                <div className="text-pearl font-black tracking-[0.2em] flex items-center gap-3">
                    <Globe className="animate-spin-slow" /> INITIALIZING GLOBAL INTELLIGENCE...
                </div>
            </div>
        );
    }

    return (
        <div className="h-[700px] rounded-2xl overflow-hidden border border-white/10 relative shadow-2xl animate-slide-up">
            {/* Map Overlay HUD */}
            <div className="absolute top-5 left-5 z-[1000] glass-panel p-4 min-w-[200px] bg-slate-900/90 backdrop-blur-md">
                <h2 className="text-sm font-black text-white flex items-center gap-2">
                    <Globe size={16} className="text-pearl" /> GLOBAL LEAD MAP
                </h2>
                <div className="mt-2 flex items-center justify-between">
                    <span className="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Active Signals</span>
                    <span className="text-lg font-black text-emerald-400">{leads.length}</span>
                </div>
                <div className="mt-1 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 w-full animate-pulse"></div>
                </div>
            </div>

            <MapContainer
                center={center}
                zoom={zoom}
                className="h-full w-full bg-slate-950"
                scrollWheelZoom={true}
            >
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                />

                {leads.map((lead) => (
                    <Marker
                        key={lead.id}
                        position={[lead.geo_lat, lead.geo_lng]}
                    >
                        <Popup className="custom-popup">
                            <div className="min-w-[200px] text-slate-900">
                                <h3 className="text-sm font-bold mb-1 border-b pb-1 border-slate-200">
                                    {lead.data_payload?.name || 'Unknown Entity'}
                                </h3>
                                <p className="text-xs text-slate-600 mb-2 font-medium">
                                    {lead.data_payload?.title || lead.data_payload?.industry}
                                </p>

                                <div className="flex justify-between items-center bg-slate-100 p-2 rounded">
                                    <span className="text-[0.6rem] font-bold text-slate-500 uppercase">Intent Score</span>
                                    <span className={`text-xs font-black ${lead.intent_score > 70 ? 'text-emerald-600' : 'text-amber-600'}`}>
                                        {lead.intent_score || 0}%
                                    </span>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            <style>{`
                .leaflet-popup-content-wrapper {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(4px);
                    border-radius: 12px;
                    border: none;
                }
                .leaflet-popup-tip {
                    background: rgba(255, 255, 255, 0.95);
                }
            `}</style>
        </div>
    );
};

export default GlobalMapView;
