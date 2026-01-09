import React, { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import EmptyStates, { SkeletonLoader } from './EmptyStates'
import '../styles/design-tokens.css'

export default function CRMHub({ session, orgId }) {
    const [crmLogs, setCrmLogs] = useState([])
    const [webhookUrl, setWebhookUrl] = useState('')
    const [loading, setLoading] = useState(true)
    const [syncing, setSyncing] = useState(false)

    useEffect(() => {
        loadCRMLogs()
        loadWebhookSettings()
    }, [])

    const loadCRMLogs = async () => {
        try {
            const { data, error } = await supabase
                .from('crm_injection_logs')
                .select('*')
                .eq('org_id', orgId)
                .order('created_at', { ascending: false })
                .limit(50)

            if (error) throw error
            setCrmLogs(data || [])
        } catch (error) {
            console.error('CRM logs error:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadWebhookSettings = async () => {
        try {
            const { data, error } = await supabase
                .from('organizations')
                .select('slack_webhook')
                .eq('id', orgId)
                .single()

            if (error) throw error
            setWebhookUrl(data?.slack_webhook || '')
        } catch (error) {
            console.error('Webhook load error:', error)
        }
    }

    const saveWebhook = async () => {
        try {
            const { error } = await supabase
                .from('organizations')
                .update({ slack_webhook: webhookUrl })
                .eq('id', orgId)

            if (error) throw error
            alert('✅ Webhook saved! High-intent leads will auto-notify.')
        } catch (error) {
            alert('Error saving webhook: ' + error.message)
        }
    }

    const triggerManualSync = async () => {
        setSyncing(true)
        try {
            const token = session.access_token
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/crm/sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })

            const data = await response.json()
            alert(`✅ Synced ${data.count || 0} leads to CRM`)
            loadCRMLogs()
        } catch (error) {
            alert('Sync error: ' + error.message)
        } finally {
            setSyncing(false)
        }
    }

    const getStatusColor = (status) => {
        if (status === 'success') return 'rgba(0,255,100,1)'
        if (status === 'pending') return 'rgba(255,200,0,1)'
        return 'rgba(255,100,100,1)'
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
                🔗 CRM INTEGRATION HUB
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginBottom: '2rem' }}>
                Connect your CRM and automation tools via webhooks (free forever)
            </p>

            {/* Webhook Configuration */}
            <div style={{
                background: 'rgba(0,0,0,0.3)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '2rem',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'rgba(255,255,255,0.8)', marginBottom: '1rem' }}>
                    ⚡ Webhook Automation
                </h3>
                <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', marginBottom: '1rem', lineHeight: '1.6' }}>
                    Connect to <strong>Slack</strong>, <strong>Make.com</strong>, <strong>Zapier</strong>, or any webhook-compatible tool.
                    We'll send high-intent leads automatically.
                </div>

                <div style={{ display: 'grid', gap: '1rem' }}>
                    <div>
                        <label style={{ fontSize: '0.7rem', fontWeight: 700, color: 'rgba(255,255,255,0.6)', display: 'block', marginBottom: '0.5rem' }}>
                            Webhook URL (Slack / Make.com / Zapier)
                        </label>
                        <input
                            type="url"
                            value={webhookUrl}
                            onChange={(e) => setWebhookUrl(e.target.value)}
                            placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                background: 'rgba(0,0,0,0.4)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                                color: '#fff',
                                fontSize: '0.8rem',
                                fontFamily: 'monospace'
                            }}
                        />
                    </div>

                    <button
                        onClick={saveWebhook}
                        style={{
                            background: 'linear-gradient(135deg, hsl(var(--pearl-primary)) 0%, hsl(var(--pearl-accent)) 100%)',
                            color: '#fff',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '8px',
                            border: 'none',
                            fontSize: '0.8rem',
                            fontWeight: 800,
                            cursor: 'pointer',
                            textTransform: 'uppercase'
                        }}
                    >
                        💾 Save Webhook
                    </button>
                </div>

                {/* Setup Guide */}
                <details style={{ marginTop: '1rem' }}>
                    <summary style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: 'hsl(var(--pearl-primary))',
                        cursor: 'pointer',
                        padding: '0.5rem',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '6px'
                    }}>
                        📚 How to connect Make.com / Zapier
                    </summary>
                    <div style={{
                        marginTop: '0.75rem',
                        padding: '1rem',
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '8px',
                        fontSize: '0.75rem',
                        lineHeight: '1.8',
                        color: 'rgba(255,255,255,0.7)'
                    }}>
                        <strong>Make.com:</strong>
                        <ol style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                            <li>Create a new scenario</li>
                            <li>Add "Webhooks" → "Custom Webhook" trigger</li>
                            <li>Copy the webhook URL</li>
                            <li>Paste above and save</li>
                            <li>Add actions: HubSpot, Salesforce, Google Sheets, etc.</li>
                        </ol>
                        <br />
                        <strong>Zapier:</strong>
                        <ol style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                            <li>Create a new Zap</li>
                            <li>Trigger: "Webhooks by Zapier" → "Catch Hook"</li>
                            <li>Copy the webhook URL</li>
                            <li>Continue as URL appeared above</li>
                        </ol>
                    </div>
                </details>
            </div>

            {/* Manual Sync Button */}
            <div style={{ marginBottom: '2rem' }}>
                <button
                    onClick={triggerManualSync}
                    disabled={syncing}
                    style={{
                        background: syncing ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        color: syncing ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.8)',
                        padding: '1rem 2rem',
                        borderRadius: '12px',
                        fontSize: '0.85rem',
                        fontWeight: 800,
                        cursor: syncing ? 'not-allowed' : 'pointer',
                        width: '100%',
                        textTransform: 'uppercase',
                        transition: 'all 0.3s'
                    }}
                >
                    {syncing ? '⏳ SYNCING...' : '🔄 MANUAL CRM SYNC'}
                </button>
            </div>

            {/* Injection Logs */}
            <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'rgba(255,255,255,0.8)', marginBottom: '1rem' }}>
                    📊 Sync History
                </h3>

                {loading ? (
                    <SkeletonLoader type="list-item" count={3} />
                ) : crmLogs.length === 0 ? (
                    <EmptyStates type="no-crm-logs" />
                ) : (
                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                        {crmLogs.map(log => (
                            <div key={log.id} style={{
                                background: 'rgba(0,0,0,0.2)',
                                borderRadius: '8px',
                                padding: '1rem',
                                border: `1px solid ${getStatusColor(log.status)}30`,
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center'
                            }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fff', marginBottom: '0.25rem' }}>
                                        {log.crm_name || 'Webhook'} Sync
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)' }}>
                                        {new Date(log.created_at).toLocaleString()}
                                    </div>
                                </div>
                                <div style={{
                                    background: getStatusColor(log.status) + '15',
                                    border: `1px solid ${getStatusColor(log.status)}`,
                                    borderRadius: '6px',
                                    padding: '0.5rem 1rem',
                                    fontSize: '0.7rem',
                                    fontWeight: 700,
                                    color: getStatusColor(log.status),
                                    textTransform: 'uppercase'
                                }}>
                                    {log.status}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
