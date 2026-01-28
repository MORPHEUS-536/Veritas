export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          light: '#F8FAFC',
        },
        primary: {
          50: '#f0f4ff',
          100: '#e0d7ff',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
        success: '#10B981',
      },
    },
  },
  darkMode: "class",
  plugins: [],
}
