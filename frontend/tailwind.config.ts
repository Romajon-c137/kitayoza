import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202a",
        muted: "#667085",
        line: "#d7dde5",
        panel: "#f6f7f9",
        accent: "#0f766e",
        danger: "#b42318"
      }
    }
  },
  plugins: []
};

export default config;
