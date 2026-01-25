import React from 'react'

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true }
    }

    componentDidCatch(error, errorInfo) {
        console.error('❌ REACT ERROR BOUNDARY CAUGHT:', error, errorInfo)
        this.setState({ error, errorInfo })
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-8">
                    <div className="max-w-2xl w-full bg-red-950/20 border border-red-500/50 rounded-2xl p-8">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-red-500/20 rounded-lg">
                                <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-red-400">SYSTEM ERROR DETECTED</h1>
                                <p className="text-sm text-slate-400 font-mono mt-1">React Error Boundary Triggered</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <h2 className="text-sm font-bold text-slate-300 mb-2">Error Message:</h2>
                                <pre className="bg-black/50 p-4 rounded-lg text-red-400 text-xs overflow-auto">
                                    {this.state.error && this.state.error.toString()}
                                </pre>
                            </div>

                            {this.state.errorInfo && (
                                <div>
                                    <h2 className="text-sm font-bold text-slate-300 mb-2">Component Stack:</h2>
                                    <pre className="bg-black/50 p-4 rounded-lg text-slate-400 text-xs overflow-auto max-h-64">
                                        {this.state.errorInfo.componentStack}
                                    </pre>
                                </div>
                            )}

                            <button
                                onClick={() => window.location.reload()}
                                className="w-full mt-6 bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-xl transition-all"
                            >
                                RELOAD APPLICATION
                            </button>

                            <p className="text-xs text-slate-500 text-center mt-4">
                                Check browser console (F12) for additional debug information
                            </p>
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
