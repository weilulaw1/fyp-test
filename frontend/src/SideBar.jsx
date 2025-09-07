import React from "react";

export default function Sidebar({ isOpen }) {
  return (
    <div
      style={{
        position: "fixed",          // stay in place
        top: 0,
        left: isOpen ? 0 : "-250px", // slide in/out
        height: "100%",
        width: "250px",
        background: "#333",
        color: "#fff",
        padding: "20px",
        transition: "left 0.3s ease",
        zIndex: 999,
      }}
    >
      <h2>Sidebar</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li>Option 1</li>
        <li>Option 2</li>
        <li>Option 3</li>
      </ul>
    </div>
  );
}
