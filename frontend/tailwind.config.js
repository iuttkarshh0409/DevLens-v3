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
          base: "#000000",
          surface: "#1a1a1a",
          terminal: "#000000",
        },
        brand: {
          purple: "#995cd6",
          textPrimary: "#fafafa",
          textSecondary: "#a6a6a6",
          textInverse: "#9ca3af",
          borderDefault: "#333333",
          borderStrong: "#2e2e2e",
        },
        accent: {
          emerald: "#995cd6", // Map emerald usages to NAMESPACE purple to ease transition
          emeraldLight: "#fafafa",
          sky: "#38BDF8",
          amber: "#FBBF24",
        }
      },
      fontFamily: {
        sans: ["'Inter'", "sans-serif"],
        display: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      }
    },
  },
  plugins: [],
}

