import React from 'react'
import { Loader2 } from 'lucide-react'

export default function Loader({ fullScreen = false, message = "LOADING..." }) {
    const content = (
        <div className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className="w-12 h-12 text-pearl animate-spin" />
            <div className="text-xs font-black tracking-[0.3em] text-pearl animate-pulse uppercase">
                {message}
            </div>
        </div>
    )

    if (fullScreen) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
                {content}
            </div>
        )
    }

    return content
}
