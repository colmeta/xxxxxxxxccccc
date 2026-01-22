import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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
            <div style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ color: 'hsl(var(--pearl-primary))', fontWeight: 900, letterSpacing: '2px' }}>LOADING GLOBAL INTELLIGENCE...</div>
            </div>
        );
    }

    return (
        <div style={{ height: '700px', borderRadius: '16px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)', position: 'relative' }}>
            <div style={{
                position: 'absolute',
                top: '20px',
                left: '20px',
                zIndex: 1000,
                background: 'rgba(10, 10, 10, 0.8)',
                backdropFilter: 'blur(10px)',
                padding: '1rem',
                borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0.1)'
            }}>
                <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 900, color: '#fff' }}>🗺️ GLOBAL LEAD MAP</h2>
                <p style={{ margin: '5px 0 0 0', fontSize: '0.7rem', color: 'hsl(var(--pearl-primary))', fontWeight: 700 }}>{leads.length} INTEL POINTS DETECTED</p>
            </div>

            <MapContainer
                center={center}
                zoom={zoom}
                style={{ height: '100%', width: '100%', background: '#0a0a0a' }}
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
                        <Popup>
                            <div style={{ color: '#000', minWidth: '200px' }}>
                                <h3 style={{ margin: '0 0 5px 0', fontSize: '0.9rem' }}>{lead.data_payload?.name || 'Unknown Entity'}</h3>
                                <p style={{ margin: '0 0 5px 0', fontSize: '0.75rem', fontWeight: 600 }}>{lead.data_payload?.title || lead.data_payload?.industry}</p>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #eee' }}>
                                    <span style={{ fontSize: '0.7rem', color: '#666' }}>INTENT SCORE</span>
                                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: lead.intent_score > 70 ? '#10b981' : '#f59e0b' }}>{lead.intent_score || 0}</span>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

export default GlobalMapView;
