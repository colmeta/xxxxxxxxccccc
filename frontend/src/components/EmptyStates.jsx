import React from 'react'

export default function EmptyStates({ type = 'no-data', title, description, action }) {
    const states = {
        'no-data': {
            icon: '🔍',
            defaultTitle: 'No Data Yet',
            defaultDescription: 'Start by creating your first mission to see results here.'
        },
        'no-jobs': {
            icon: '🚀',
            defaultTitle: 'Ready to Launch?',
            defaultDescription: 'Create your first mission using the Oracle above.'
        },
        'no-results': {
            icon: '⏳',
            defaultTitle: 'Hydra is Searching...',
            defaultDescription: 'Our swarm is actively scanning the web for your targets.'
        },
        'no-workers': {
            icon: '🛸',
            defaultTitle: 'Swarm Offline',
            defaultDescription: 'No workers detected. Start Hydra to activate the global network.'
        },
        'no-crm': {
            icon: '🔗',
            defaultTitle: 'Connect Your CRM',
            defaultDescription: 'Set up a webhook to automate lead sync to HubSpot, Salesforce, or any tool.'
        },
        'no-crm-logs': {
            icon: '📭',
            defaultTitle: 'No Sync History',
            defaultDescription: 'Configure your webhook above to start tracking CRM injections.'
        },
        'error': {
            icon: '⚠️',
            defaultTitle: 'Something Went Wrong',
            defaultDescription: 'Unable to load data. Please try refreshing the page.'
        },
        'success': {
            icon: '✅',
            defaultTitle: 'All Set!',
            defaultDescription: 'Everything is working perfectly.'
        },
        'maintenance': {
            icon: '🔧',
            defaultTitle: 'Under Maintenance',
            defaultDescription: 'We're making improvements.Check back soon.'
        }
    }

    const state = states[type] || states['no-data']

    return (
        <div className="empty-state animate-fade-in">
            <div className="empty-state-icon">
                {state.icon}
            </div>
            <div className="empty-state-title">
                {title || state.defaultTitle}
            </div>
            <div className="empty-state-description">
                {description || state.defaultDescription}
            </div>
            {action && (
                <div style={{ marginTop: '2rem' }}>
                    {action}
                </div>
            )}
        </div>
    )
}

// Skeleton Loader Component
export function SkeletonLoader({ type = 'card', count = 1 }) {
    const skeletons = {
        'text': (
            <div className="skeleton skeleton-text" />
        ),
        'title': (
            <div className="skeleton skeleton-title" />
        ),
        'card': (
            <div className="skeleton skeleton-card" />
        ),
        'circle': (
            <div className="skeleton skeleton-circle" />
        ),
        'list-item': (
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                <div className="skeleton skeleton-circle" />
                <div style={{ flex: 1 }}>
                    <div className="skeleton skeleton-text" style={{ width: '80%' }} />
                    <div className="skeleton skeleton-text" style={{ width: '60%' }} />
                </div>
            </div>
        ),
        'result-card': (
            <div className="glass-card-premium" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ flex: 1 }}>
                        <div className="skeleton skeleton-title" />
                        <div className="skeleton skeleton-text" style={{ width: '70%' }} />
                    </div>
                    <div className="skeleton skeleton-circle" style={{ width: '60px', height: '60px' }} />
                </div>
                <div className="skeleton skeleton-text" />
                <div className="skeleton skeleton-text" style={{ width: '90%' }} />
            </div>
        )
    }

    return (
        <>
            {Array.from({ length: count }).map((_, idx) => (
                <div key={idx}>
                    {skeletons[type]}
                </div>
            ))}
        </>
    )
}

// Loading Spinner Component
export function Spinner({ size = 'md', text }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            padding: '2rem'
        }}>
            <div className={`spinner spinner-${size}`} />
            {text && (
                <div style={{
                    fontSize: '0.9rem',
                    color: 'rgba(255,255,255,0.6)',
                    fontWeight: 600
                }}>
                    {text}
                </div>
            )}
        </div>
    )
}
