import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App"; 
import "./index.css"; // ✅ Make sure this file exists!

// Wait until DOM is fully loaded before mounting React
document.addEventListener("DOMContentLoaded", () => {
    const rootElement = document.getElementById("root");
    if (rootElement) {
        const root = ReactDOM.createRoot(rootElement);
        root.render(<App />);
    } else {
        console.error("❌ React Error: No root element found!");
    }
});
