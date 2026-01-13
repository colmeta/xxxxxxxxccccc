import React from 'react'

export default function Layout({ children, session }) {
    const handleLogout = () => {
        // Simple reload to clear for now or proper auth signout
        import('../lib/supabase').then(({ supabase }) => supabase.auth.signOut())
    }

    return (
        <div className="layout-container" style={{ maxWidth: '1400px', margin: '0 auto', padding: '1rem 2rem' }}>
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
                <div className="logo-section" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div className="logo-section" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        {/* Code-based Logo for reliability */}
                        <div style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, hsl(var(--pearl-primary)), hsl(var(--pearl-accent)))',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 0 15px hsla(var(--pearl-primary), 0.5)'
                        }}>
                            <span style={{ fontSize: '1.5rem', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}>💎</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontWeight: 800, fontSize: '1.4rem', letterSpacing: '-0.5px', color: 'hsl(var(--pearl-primary))' }}>CLARITY <span style={{ color: '#fff', fontWeight: 300 }}>PEARL</span></span>
                            <span className="desktop-only" style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '2px', textTransform: 'uppercase' }}>Always-On Intelligence</span>
                        </div>
                    </div>

                    <div className="user-section" style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                        <div className="desktop-hidden mobile-stack" style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{session?.user?.email?.split('@')[0]}</div>
                            <div style={{ fontSize: '0.65rem', color: 'var(--success)', fontWeight: 700 }}>VERIFIED AGENT</div>
                        </div>
                        <div className="mobile-hidden" style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{session?.user?.email?.split('@')[0]}</div>
                            <div style={{ fontSize: '0.65rem', color: 'var(--success)', fontWeight: 700 }}>VERIFIED AGENT</div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="btn-primary"
                            style={{ padding: '0.5rem 1.25rem', fontSize: '0.7rem', borderRadius: '12px' }}
                        >
                            <span className="desktop-only">SECURE </span>LOGOUT
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
                justifyContent: 'center',
                alignItems: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.7rem',
                letterSpacing: '1px'
            }}>
                <div>© 2026 CLARITY PEARL | SUPREME EDITION</div>
            </footer>
        </div>
    )
}
        </div >
    )
}
