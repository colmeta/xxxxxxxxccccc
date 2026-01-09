import React, { useState } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import '../styles/design-tokens.css'

export default function BulkMissionControl({ session }) {
    const [csvFile, setCSVFile] = useState(null)
    const [linkedinUrls, setLinkedinUrls] = useState('')
    const [platform, setPlatform] = useState('linkedin')
    const [preview, setPreview] = useState([])
    const [loading, setLoading] = useState(false)
    const [jobIds, setJobIds] = useState([])

    const handleCSVUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        const text = await file.text()
        const lines = text.split('\n').filter(line => line.trim())
        const queries = lines.slice(1).map(line => line.split(',')[0].trim()).filter(q => q)

        setPreview(queries.slice(0, 10)) // Show first 10
        setCSVFile(queries)
    }

    const handleLinkedInPaste = (e) => {
        const urls = e.target.value.split('\n').filter(url => url.trim())
        setLinkedinUrls(e.target.value)
        setPreview(urls.slice(0, 10))
    }

    const executeBulkMission = async () => {
        setLoading(true)
        try {
            const token = session.access_token
            const queries = csvFile || linkedinUrls.split('\n').filter(l => l.trim())

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/bulk/create`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    queries,
                    platform,
                    priority: 3
                })
            })

            const data = await response.json()
            setJobIds(data.job_ids || [])
            alert(`✅ ${data.job_ids?.length || 0} missions created!`)
        } catch (error) {
            alert('Error creating bulk missions: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            background: 'rgba(0,0,0,0.3)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.05)'
        }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '1rem', color: 'hsl(var(--pearl-primary))' }}>
                ⚡ BULK MISSION CONTROL
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginBottom: '2rem' }}>
                Upload CSV or paste LinkedIn URLs/queries to create hundreds of jobs instantly
            </p>

            <div style={{ display: 'grid', gap: '1.5rem' }}>
                {/* CSV Upload */}
                <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'rgba(255,255,255,0.7)', display: 'block', marginBottom: '0.5rem' }}>
                        📄 Upload CSV (Column 1 = Queries)
                    </label>
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleCSVUpload}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'rgba(0,0,0,0.4)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: '#fff',
                            cursor: 'pointer'
                        }}
                    />
                </div>

                {/* LinkedIn URLs */}
                <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'rgba(255,255,255,0.7)', display: 'block', marginBottom: '0.5rem' }}>
                        🔗 Or Paste LinkedIn URLs / Queries (One Per Line)
                    </label>
                    <textarea
                        value={linkedinUrls}
                        onChange={handleLinkedInPaste}
                        placeholder="https://linkedin.com/in/example&#10;SaaS CEOs in Austin&#10;Tech founders in NYC"
                        rows={6}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'rgba(0,0,0,0.4)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: '#fff',
                            fontFamily: 'monospace',
                            fontSize: '0.8rem',
                            resize: 'vertical'
                        }}
                    />
                </div>

                {/* Platform Selector */}
                <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 700, color: 'rgba(255,255,255,0.7)', display: 'block', marginBottom: '0.5rem' }}>
                        🎯 Target Platform
                    </label>
                    <select
                        value={platform}
                        onChange={(e) => setPlatform(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'rgba(0,0,0,0.4)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: '#fff',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="linkedin">LinkedIn</option>
                        <option value="google_maps">Google Maps</option>
                        <option value="tiktok">TikTok</option>
                        <option value="producthunt">Product Hunt</option>
                        <option value="google_news">Google News</option>
                    </select>
                </div>

                {/* Preview */}
                {preview.length > 0 && (
                    <div style={{
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '8px',
                        padding: '1rem',
                        border: '1px solid rgba(255,255,255,0.05)'
                    }}>
                        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.5)', marginBottom: '0.5rem' }}>
                            PREVIEW ({preview.length} of {csvFile?.length || linkedinUrls.split('\n').length})
                        </div>
                        {preview.map((item, idx) => (
                            <div key={idx} style={{
                                fontSize: '0.75rem',
                                color: 'hsl(var(--pearl-primary))',
                                padding: '0.25rem 0',
                                borderBottom: idx < preview.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none'
                            }}>
                                {idx + 1}. {item.substring(0, 60)}{item.length > 60 ? '...' : ''}
                            </div>
                        ))}
                    </div>
                )}

                {/* Execute Button */}
                <button
                    onClick={executeBulkMission}
                    disabled={loading || (!csvFile && !linkedinUrls.trim())}
                    style={{
                        background: loading ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, hsl(var(--pearl-primary)) 0%, hsl(var(--pearl-accent)) 100%)',
                        color: '#fff',
                        padding: '1rem 2rem',
                        borderRadius: '12px',
                        border: 'none',
                        fontSize: '0.9rem',
                        fontWeight: 900,
                        cursor: loading ? 'not-allowed' : 'pointer',
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        transition: 'all 0.3s',
                        boxShadow: '0 4px 16px rgba(var(--pearl-primary-rgb), 0.3)'
                    }}
                >
                    {loading ? '⚡ LAUNCHING SWARM...' : `🚀 LAUNCH ${preview.length} MISSIONS`}
                </button>

                {/* Results */}
                {jobIds.length > 0 && (
                    <div style={{
                        background: 'rgba(0,255,100,0.05)',
                        border: '1px solid rgba(0,255,100,0.2)',
                        borderRadius: '8px',
                        padding: '1rem',
                        fontSize: '0.8rem',
                        color: 'rgba(0,255,100,0.9)'
                    }}>
                        ✅ {jobIds.length} missions deployed. Check Live Feed for progress.
                    </div>
                )}
            </div>
        </div>
    )
}
