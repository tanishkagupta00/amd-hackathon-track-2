/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#1E293B',  // Slate-800
          accent: '#EA580C',   // AMD Orange-600
        }
      }
    },
  },
  plugins: [],
}
