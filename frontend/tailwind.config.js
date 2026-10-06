/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: "#09090B",
          900: "#18181B",
          800: "#27272A",
          700: "#3F3F46",
        },
        violet: {
          500: "#8B5CF6",
          600: "#7C3AED",
          700: "#6D28D9",
        },
        indigo: {
          500: "#6366F1",
          600: "#4F46E5",
        }
      }
    },
  },
  plugins: [],
}
