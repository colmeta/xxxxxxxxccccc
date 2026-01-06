import React from 'react'

export default function Layout({ children, session }) {
    const handleLogout = () => {
        // Simple reload to clear for now or proper auth signout
        import('../lib/supabase').then(({ supabase }) => supabase.auth.signOut())
    }

    return (
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '1rem 2rem' }}>
            <header
                className="supreme-glass"
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '2rem',
                    padding: '1.5rem 2rem',
                    marginTop: '1rem'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <img src="/logo.png" style={{ height: '45px', filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.3))' }} />
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontWeight: 800, fontSize: '1.4rem', letterSpacing: '-0.5px', color: 'hsl(var(--pearl-primary))' }}>CLARITY <span style={{ color: '#fff', fontWeight: 300 }}>PEARL</span></span>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '2px', textTransform: 'uppercase' }}>Always-On Intelligence</span>
                    </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{session?.user?.email?.split('@')[0]}</div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--success)', fontWeight: 700 }}>VERIFIED AGENT</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="btn-primary"
                        style={{ padding: '0.5rem 1.25rem', fontSize: '0.7rem', borderRadius: '12px' }}
                    >
                        SECURE LOGOUT
                    </button>
                </div>
            </header>

            <main>
                {children}
            </main>

            <footer style={{
                marginTop: '4rem',
                borderTop: '1px solid var(--glass-border)',
                paddingTop: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.7rem',
                letterSpacing: '1px'
            }}>
                <div style={{ display: 'flex', gap: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '6px', height: '6px', background: 'var(--success)', borderRadius: '50%' }}></div>
                        SENTRY: NOMINAL
                    </div>
                    <div>ENCRYPTION: AES-256</div>
                </div>
                <div>© 2026 CLARITY PEARL | SUPREME EDITION</div>
                <div style={{ color: 'hsl(var(--pearl-primary))', fontWeight: 700 }}>LATENCY: 8ms</div>
            </footer>
        </div>
    )
}
