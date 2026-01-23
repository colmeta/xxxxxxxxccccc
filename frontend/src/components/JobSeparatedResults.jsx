import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export default function JobSeparatedResults() {
    const [jobGroups, setJobGroups] = useState([])
    const [loading, setLoading] = useState(false)
    const [selectedCategory, setSelectedCategory] = useState('all')
    const [categories, setCategories] = useState([])

    useEffect(() => {
        fetchJobGroups()
        fetchCategories()
    }, [selectedCategory])

    const fetchCategories = async () => {
        const { data } = await supabase
            .from('jobs')
            .select('category')
            .not('category', 'is', null)

        if (data) {
            const uniqueCategories = [...new Set(data.map(j => j.category).filter(Boolean))]
            setCategories(uniqueCategories.sort())
        }
    }

    const fetchJobGroups = async () => {
        setLoading(true)

        let query = supabase
            .from('jobs')
            .select(`
                id,
                target_query,
                category,
                target_platform,
                created_at,
                result_count,
                delivery_metadata
            `)
            .order('created_at', { ascending: false })
            .limit(20)

        if (selectedCategory !== 'all') {
            query = query.eq('category', selectedCategory)
        }

        const { data: jobs } = await query

        if (jobs) {
            // Fetch results for each job
            const jobsWithResults = await Promise.all(
                jobs.map(async (job) => {
                    const { data: results } = await supabase
                        .from('results')
                        .select('*')
                        .eq('job_id', job.id)
                        .order('clarity_score', { ascending: false })
                        .limit(50)

                    return {
                        ...job,
                        results: results || []
                    }
                })
            )

            setJobGroups(jobsWithResults.filter(j => j.results.length > 0))
        }

        setLoading(false)
    }

    const exportJobCSV = (job) => {
        const headers = ["Name", "Title", "Company", "Email", "Phone", "Location", "LinkedIn", "Lead Score"]
        const csvRows = [headers.join(",")]

        job.results.forEach(r => {
            const data = r.data_payload || {}
            const row = [
                `"${(data.name || data.full_name || "").replace(/"/g, '""')}"`,
                `"${(data.title || "").replace(/"/g, '""')}"`,
                `"${(data.company || "").replace(/"/g, '""')}"`,
                `"${data.email || data.decision_maker_email || ""}"`,
                `"${data.phone || ""}"`,
                `"${data.location || ""}"`,
                `"${data.linkedin_url || data.source_url || ""}"`,
                r.clarity_score || 0
            ]
            csvRows.push(row.join(","))
        })

        const csvContent = csvRows.join("\n")
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        const filename = `${job.category || 'export'}_${new Date().toISOString().split('T')[0]}.csv`
        link.setAttribute("href", url)
        link.setAttribute("download", filename)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const markAsDelivered = async (job) => {
        if (!confirm(`Mark "${job.category || job.target_query}" as delivered? This will track these companies to prevent duplicates in future searches.`)) {
            return
        }

        try {
            const { data: { session } } = await supabase.auth.getSession()
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/deliveries/mark`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session?.access_token}`
                },
                body: JSON.stringify({
                    job_id: job.id,
                    category: job.category,
                    delivery_method: 'csv_export'
                })
            })

            const result = await response.json()
            if (response.ok) {
                alert(`✅ Marked ${result.delivered_count} leads as delivered in category: ${result.category}`)
                fetchJobGroups() // Refresh
            } else {
                alert(`Error: ${result.detail || 'Failed to mark as delivered'}`)
            }
        } catch (error) {
            alert(`Error: ${error.message}`)
        }
    }

    return (
        <div style={{ marginTop: '2rem' }}>
            <div className="supreme-glass" style={{ padding: '2.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }}>
                        <span style={{ color: 'hsl(var(--pearl-primary))' }}>📦</span> DATA SETS
                    </h2>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            style={{
                                padding: '0.6rem 1rem',
                                borderRadius: '12px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                background: 'rgba(255,255,255,0.05)',
                                color: '#fff',
                                fontSize: '0.85rem',
                                fontWeight: 600
                            }}
                        >
                            <option value="all">All Categories</option>
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                        <button onClick={fetchJobGroups} className="btn-primary" style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem' }}>
                            {loading ? '...' : 'REFRESH'}
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '4rem', color: 'rgba(255,255,255,0.5)' }}>
                        <div className="spinner"></div> Loading data sets...
                    </div>
                ) : jobGroups.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '4rem', color: 'rgba(255,255,255,0.5)' }}>
                        No data sets found. Create a mission to begin.
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                        {jobGroups.map((job, idx) => (
                            <div key={job.id} className="glass-panel" style={{
                                padding: '2rem',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '16px',
                                animation: `fadeIn 0.3s ease-out ${idx * 0.1}s both`
                            }}>
                                {/* Job Header */}
                                <div style={{ marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', flexWrap: 'wrap', gap: '1rem' }}>
                                        <div>
                                            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginBottom: '0.5rem' }}>
                                                📂 {job.category || job.target_query}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                                                <span>📅 {new Date(job.created_at).toLocaleDateString()}</span>
                                                <span>💎 {job.results.length} Leads</span>
                                                <span>🎯 {job.target_platform}</span>
                                                {job.delivery_metadata?.delivered_at && (
                                                    <span style={{ color: 'hsl(var(--pearl-success))' }}>
                                                        ✅ Delivered {new Date(job.delivery_metadata.delivered_at).toLocaleDateString()}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button
                                                onClick={() => exportJobCSV(job)}
                                                className="btn-secondary"
                                                style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', fontWeight: 700 }}
                                            >
                                                📥 EXPORT CSV
                                            </button>
                                            {!job.delivery_metadata?.delivered_at && (
                                                <button
                                                    onClick={() => markAsDelivered(job)}
                                                    className="btn-primary"
                                                    style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', fontWeight: 700 }}
                                                >
                                                    ✅ MARK DELIVERED
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Results Preview */}
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                                    {job.results.slice(0, 6).map(r => (
                                        <div key={r.id} style={{
                                            padding: '1rem',
                                            background: 'rgba(255,255,255,0.02)',
                                            borderRadius: '12px',
                                            border: '1px solid rgba(255,255,255,0.05)'
                                        }}>
                                            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.5rem', color: '#fff' }}>
                                                {r.data_payload?.name || r.data_payload?.full_name || 'Unknown'}
                                            </div>
                                            <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.3rem' }}>
                                                {r.data_payload?.title || 'No Title'}
                                            </div>
                                            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>
                                                🏢 {r.data_payload?.company || 'No Company'}
                                            </div>
                                            <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
                                                <span style={{ color: r.clarity_score > 80 ? 'hsl(var(--pearl-success))' : 'hsl(var(--pearl-primary))' }}>
                                                    Score: {r.clarity_score || 0}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {job.results.length > 6 && (
                                    <div style={{ textAlign: 'center', marginTop: '1rem', color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem' }}>
                                        + {job.results.length - 6} more leads
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
