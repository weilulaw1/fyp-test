import React, { useState } from "react";

export default function DiagramView({ modeComponents = {} }) {
  const [viewMode, setViewMode] = useState(Object.keys(modeComponents)[0] || null);

  if (!viewMode) {
    return <div style={{ padding: "20px" }}>No diagram modes available.</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      {/* Mode Selector */}
      <div style={{ marginBottom: "20px" }}>
        {Object.keys(modeComponents).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            style={{
              marginRight: "10px",
              backgroundColor: viewMode === mode ? "#007bff" : "#f0f0f0",
              color: viewMode === mode ? "#fff" : "#000",
              border: "1px solid #ccc",
              padding: "6px 12px",
              borderRadius: "4px",
            }}
          >
            {mode} View
          </button>
        ))}
      </div>

      {/* Render current mode */}
      <div style={{ maxWidth: "1000px", margin: "0 auto", width: "100%" }}>
        {modeComponents[viewMode]}
      </div>
    </div>
  );
}
