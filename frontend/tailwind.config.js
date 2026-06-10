/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#050505",
          surface: "#0A0A0A",
          terminal: "#000000",
        },
        accent: {
          emerald: "#10B981",
          emeraldLight: "#34D399",
          sky: "#38BDF8",
          amber: "#FBBF24",
        }
      },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "sans-serif"],
        display: ["'Outfit'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      }
    },
  },
  plugins: [],
}
