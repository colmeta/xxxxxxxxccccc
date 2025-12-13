import React from 'react'

export default function Layout({ children, session }) {
    const handleLogout = () => {
        // Simple reload to clear for now or proper auth signout
        import('../lib/supabase').then(({ supabase }) => supabase.auth.signOut())
    }

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '12px', height: '12px', background: 'var(--success)', borderRadius: '50%', boxShadow: '0 0 10px var(--success)' }} className="animate-pulse-slow"></div>
                    <span style={{ fontWeight: 700, fontSize: '1.25rem', letterSpacing: '1px' }}>CLARITY PEARL</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                        {session?.user?.email}
                    </span>
                    <button
                        onClick={handleLogout}
                        style={{ background: 'transparent', border: '1px solid var(--border-accent)', color: 'var(--primary)', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem' }}
                    >
                        TERMINATE
                    </button>
                </div>
            </header>

            <main>
                {children}
            </main>

            <footer style={{ marginTop: '4rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', color: '#475569', fontSize: '0.75rem' }}>
                <div>STATUS: ONLINE</div>
                <div>LATENCY: 12ms</div>
                <div>WORKERS: ACTIVE</div>
            </footer>
        </div>
    )
}
