/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  safelist: [
    'bg-slate-950',
    'border-slate-800',
    'bg-slate-900',
    'bg-slate-800',
    'text-white',
    'flex',
    'grid',
    'rounded',
    'border',
    'text-slate-100',
    'text-slate-200',
    'text-slate-300',
    'text-slate-400',
    'text-slate-500',
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: '#080B11',
          panel: '#0D131F',
          surface: '#111927',
          elevated: '#172133',
          hover: '#1D2A42',
          border: '#1E293B',
          'border-light': '#2A3B53',
        },
        risk: {
          critical: '#EF4444',
          high: '#F97316',
          medium: '#F59E0B',
          low: '#10B981',
          info: '#06B6D4',
          purple: '#8B5CF6',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'soc-subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'soc-card': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
        'glow-critical': '0 0 15px rgba(239, 68, 68, 0.25)',
        'glow-high': '0 0 15px rgba(249, 115, 22, 0.25)',
        'glow-cyan': '0 0 15px rgba(6, 182, 212, 0.25)',
      }
    },
  },
  plugins: [],
};
