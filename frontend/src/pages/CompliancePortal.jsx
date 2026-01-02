import React, { useState } from 'react';
import { Shield, CheckCircle, AlertTriangle } from 'lucide-react';

const CompliancePortal = () => {
    const [email, setEmail] = useState('');
    const [submitted, setSubmitted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Create SHA-256 hash of email for privacy
            const encoder = new TextEncoder();
            const data = encoder.encode(email.toLowerCase().trim());
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || ''}/api/opt-out`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ hash: hashHex, type: 'email' }),
            });

            if (!response.ok) throw new Error('Failed to process request');

            setSubmitted(true);
        } catch (err) {
            setError('An error occurred. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
            <div className="max-w-md w-full bg-slate-900/50 border border-slate-800 rounded-2xl p-8 backdrop-blur-xl shadow-2xl">
                <div className="flex items-center justify-center mb-6">
                    <div className="p-3 bg-blue-500/10 rounded-full border border-blue-500/20">
                        <Shield className="w-8 h-8 text-blue-500" />
                    </div>
                </div>

                <h1 className="text-2xl font-bold text-center mb-2">Compliance Shield</h1>
                <p className="text-slate-400 text-center mb-8 text-sm">
                    Clarity Pearl respects your privacy. Use this portal to globally opt-out of our data intelligence network.
                </p>

                {submitted ? (
                    <div className="text-center animate-in fade-in zoom-in duration-300">
                        <div className="flex justify-center mb-4">
                            <CheckCircle className="w-12 h-12 text-emerald-500" />
                        </div>
                        <h2 className="text-lg font-semibold text-emerald-400">Request Confirmed</h2>
                        <p className="text-slate-400 mt-2 text-sm">
                            Your identifier has been hashed and added to our global blocklist. You will no longer be tracked.
                        </p>
                        <button
                            onClick={() => setSubmitted(false)}
                            className="mt-6 text-slate-500 hover:text-slate-300 text-xs transition-colors"
                        >
                            Back to form
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
                                Email or Phone Number
                            </label>
                            <input
                                type="text"
                                required
                                placeholder="e.g. user@example.com"
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all text-sm"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs">
                                <AlertTriangle className="w-4 h-4" />
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-all shadow-lg shadow-blue-900/20 text-sm"
                        >
                            {loading ? 'Processing...' : 'Secure Opt-Out'}
                        </button>

                        <p className="text-[10px] text-slate-600 text-center mt-4">
                            By submitting, your data is immediately hashed and the original plain-text is never stored.
                        </p>
                    </form>
                )}
            </div>

            <div className="mt-12 text-slate-700 text-[10px] tracking-widest uppercase flex items-center gap-4">
                <span>Clarity Pearl Intelligence</span>
                <span className="w-1 h-1 bg-slate-800 rounded-full"></span>
                <span>Secure & Compliant</span>
            </div>
        </div>
    );
};

export default CompliancePortal;
