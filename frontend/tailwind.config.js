/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // The Void Palette
                background: '#000000', // True Void
                void: '#030014', // Deep Space

                // Glass-morphism bases
                glass: {
                    DEFAULT: 'rgba(255, 255, 255, 0.03)',
                    hover: 'rgba(255, 255, 255, 0.08)',
                    border: 'rgba(255, 255, 255, 0.08)',
                },

                // Identity Colors - Neon Bioluminescence
                pearl: {
                    DEFAULT: '#00F0FF', // Cyber Cyan
                    glow: '#00F0FF80',
                    dim: '#003840',
                },
                obsidian: {
                    DEFAULT: '#0F1115',
                    light: '#1A1D26',
                    dark: '#050608',
                },
                accent: {
                    purple: '#7000FF',
                    gold: '#FFD700',
                    alert: '#FF003C',
                    success: '#00FF94',
                },

                // Semantic
                surface: {
                    DEFAULT: '#050608',
                    light: '#0F1218',
                }
            },
            fontFamily: {
                sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
                display: ['Orbitron', 'sans-serif'], // For headers if available, else fallback
            },
            boxShadow: {
                'neon': '0 0 20px -5px var(--tw-shadow-color)',
                'neon-strong': '0 0 40px -10px var(--tw-shadow-color)',
                'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
                'inner-light': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.05)',
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'scanline': 'scanline 8s linear infinite',
                'float': 'float 6s ease-in-out infinite',
                'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
            },
            keyframes: {
                scanline: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                'glow-pulse': {
                    '0%, 100%': { boxShadow: '0 0 20px -5px rgba(0, 240, 255, 0.3)' },
                    '50%': { boxShadow: '0 0 30px -5px rgba(0, 240, 255, 0.6)' },
                }
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'grid-pattern': "linear-gradient(to right, #1f2937 1px, transparent 1px), linear-gradient(to bottom, #1f2937 1px, transparent 1px)",
            }
        },
    },
    plugins: [],
}
