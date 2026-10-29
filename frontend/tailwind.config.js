/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          800: '#111827',
          900: '#0b0f19',
          950: '#06090e',
        },
      },
    },
  },
  plugins: [],
}

