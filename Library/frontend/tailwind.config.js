/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        library: {
          bg: '#FAF9F5',
          card: '#FFFFFF',
          border: '#E8E5DD',
          darkBg: '#0D1117',
          darkCard: '#161B22',
          darkBorder: '#30363D',
          navy: {
            DEFAULT: '#0F172A',
            50: '#F8FAFC',
            100: '#F1F5F9',
            600: '#475569',
            700: '#334155',
            800: '#1E293B',
            900: '#0F172A',
          },
          emerald: {
            DEFAULT: '#065F46',
            light: '#ECFDF5',
            border: '#A7F3D0',
            text: '#047857',
            hover: '#047857',
          },
          amber: {
            DEFAULT: '#D97706',
            light: '#FFFBEB',
            border: '#FDE68A',
            text: '#B45309',
          },
        }
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'book': '0 8px 30px rgba(0, 0, 0, 0.08)',
        'book-hover': '0 14px 40px rgba(0, 0, 0, 0.14)',
      }
    },
  },
  plugins: [],
}
