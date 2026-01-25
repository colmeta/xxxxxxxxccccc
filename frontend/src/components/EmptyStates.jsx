import React from 'react'
import { AlertCircle, Search, Database } from 'lucide-react'

export const SkeletonLoader = ({ type = 'card', count = 1 }) => {
    return (
        <div className="space-y-4 w-full">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className={`animate-pulse rounded-xl bg-slate-800/50 border border-white/5 ${type === 'card' ? 'h-32' : 'h-12'}`}></div>
            ))}
        </div>
    )
}

export default function EmptyStates({ type, title, description, action }) {
    const getContent = () => {
        switch (type) {
            case 'no-results':
                return {
                    icon: <Search size={48} className="text-slate-600 mb-4" />,
                    text: title || "No Results Found",
                    sub: description || "Try adjusting your filters or search query."
                }
            case 'no-data':
                return {
                    icon: <Database size={48} className="text-slate-600 mb-4" />,
                    text: title || "The Vault is Empty",
                    sub: description || "Launch a mission to populate this view."
                }
            default:
                return {
                    icon: <AlertCircle size={48} className="text-slate-600 mb-4" />,
                    text: title || "Nothing to see here",
                    sub: description || "Check back later."
                }
        }
    }

    const content = getContent()

    return (
        <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in border border-dashed border-white/10 rounded-2xl bg-white/5 mx-auto w-full max-w-2xl">
            {content.icon}
            <h3 className="text-lg font-bold text-white mb-2">{content.text}</h3>
            <p className="text-sm text-slate-400 max-w-xs mx-auto mb-6">{content.sub}</p>
            {action && (
                <div className="mt-2">
                    {action}
                </div>
            )}
        </div>
    )
}
