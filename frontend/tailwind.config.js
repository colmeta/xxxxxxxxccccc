/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#020617', // Deep Ocean
                card: 'rgba(15, 23, 42, 0.95)',
                input: 'rgba(30, 41, 59, 0.8)',

                pearl: {
                    DEFAULT: 'hsl(190, 100%, 50%)', // Electric Cyan
                    50: 'hsl(190, 100%, 95%)',
                    100: 'hsl(190, 100%, 90%)',
                    200: 'hsl(190, 100%, 80%)',
                    300: 'hsl(190, 100%, 70%)',
                    400: 'hsl(190, 100%, 60%)',
                    500: 'hsl(190, 100%, 50%)', // Primary
                    600: 'hsl(190, 100%, 40%)',
                    700: 'hsl(190, 100%, 30%)',
                    800: 'hsl(190, 100%, 20%)',
                    900: 'hsl(190, 100%, 10%)',
                },
                secondary: {
                    DEFAULT: 'hsl(200, 90%, 60%)', // Soft Sky
                },
                accent: {
                    DEFAULT: 'hsl(217, 91%, 60%)', // Professional Blue
                },
                success: 'hsl(150, 100%, 50%)', // Sharp Emerald
                warning: 'hsl(35, 100%, 55%)',  // Amber
                danger: 'hsl(0, 90%, 60%)',     // Red
            },
            fontFamily: {
                sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            boxShadow: {
                'glow': '0 0 20px hsla(190, 100%, 50%, 0.3)',
                'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'shine': 'shine 2s infinite',
            },
            keyframes: {
                shine: {
                    '0%': { backgroundPosition: '-100% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                }
            }
        },
    },
    plugins: [],
}
