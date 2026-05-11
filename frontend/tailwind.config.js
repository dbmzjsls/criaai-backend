/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          900: '#0a0a0f',
          800: '#12121a',
          700: '#1a1a2e',
          600: '#25253d',
          500: '#2d2d4a',
        },
        neon: {
          magenta: '#d946ef',
          purple: '#7c3aed',
          cyan: '#22d3ee',
          green: '#22c55e',
          yellow: '#eab308',
          orange: '#f97316',
          pink: '#ec4899',
        },
        brand: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#d946ef',
          500: '#c026d3',
          600: '#a21caf',
          700: '#86198f',
          800: '#701a75',
          900: '#4a044e',
        },
        accent: {
          magenta: '#d946ef',
          purple: '#7c3aed',
          cyan: '#22d3ee',
          pink: '#ec4899',
        }
      },
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
        heading: ['Outfit', 'Plus Jakarta Sans', 'sans-serif'],
        mono: ['Space Mono', 'Courier New', 'monospace'],
      },
      animation: {
        'spin-slow': 'spin 30s linear infinite',
        'spin-slow-reverse': 'spin 40s linear infinite reverse',
        'float': 'float 6s ease-in-out infinite',
        'float-reverse': 'float 8s ease-in-out infinite reverse',
        'pulse-soft': 'pulseGlow 3s ease-in-out infinite',
        'pulse-neon': 'pulseNeon 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'fade-up': 'fadeUp 0.5s ease forwards',
        'scale-in': 'scaleIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.5s ease forwards',
        'scan-line': 'scanLine 3s linear infinite',
        'pill-flow': 'pillFlow 2s ease-in-out infinite',
        'breathing': 'breathing 3s ease-in-out infinite',
        'number-tick': 'numberTick 0.3s ease-out',
        'beam-sweep': 'beamSweep 4s linear infinite',
        'grid-pulse': 'gridPulse 8s ease-in-out infinite',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
