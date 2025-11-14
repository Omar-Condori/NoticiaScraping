/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Habilitar dark mode con clase
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0a0a0f',
          card: '#121218',
          hover: '#1a1a24',
          border: '#2a2a35'
        },
        light: {
          bg: '#f8f9fa',
          card: '#ffffff',
          hover: '#f1f3f5',
          border: '#e9ecef'
        },
        accent: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444'
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
      },
      backdropBlur: {
        xs: '2px'
      }
    },
  },
  plugins: [],
}