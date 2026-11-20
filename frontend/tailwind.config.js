/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#F3F0E8",
        ink: "#17312F",
        mist: "#5E6F6C",
        line: "#E4DDD0",
        teal: {
          DEFAULT: "#1F6F68",
          dark: "#174E4A",
          deep: "#143F3C",
        },
        coral: "#F08A3A",
        sand: "#F7F1E4",
      },
      boxShadow: {
        card: "0 18px 50px rgba(23, 49, 47, 0.06)",
      },
      borderRadius: {
        card: "28px",
      },
    },
  },
  plugins: [],
};
