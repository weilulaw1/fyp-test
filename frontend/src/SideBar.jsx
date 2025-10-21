import React from "react";
import SidebarOutIcon from './assets/sidebar out.png';
import SidebarInIcon from './assets/sidebar in.png';

export default function Sidebar({ isOpen, toggleSidebar, onSectionChange }) {
  return (
    <div
      style={{
        width: isOpen ? "250px" : "52px",
        transition: "width 0.3s ease",
        overflow: "hidden",
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        background: "#333",
        color: "white",
        zIndex: 1100,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: "60px",
      }}
    >
      {/* Sidebar toggle button */}
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          cursor: "pointer",
        }}
        onClick={toggleSidebar}
      >
        <img
          src={isOpen ? SidebarInIcon : SidebarOutIcon}
          alt="Toggle Sidebar"
          width={30}
          height={30}
          style={{ filter: "invert(1)" }}
        />
      </div>

      {/* Buttons */}
      {isOpen && (
        <>
          <button
            style={{
              margin: "10px 0",
              width: "180px",
              padding: "10px",
              backgroundColor: "#555",
              border: "none",
              borderRadius: "6px",
              color: "white",
              cursor: "pointer",
            }}
            onClick={() => onSectionChange("folder")}
          >
            📁 View Folder
          </button>

          <button
            style={{
              margin: "10px 0",
              width: "180px",
              padding: "10px",
              backgroundColor: "#555",
              border: "none",
              borderRadius: "6px",
              color: "white",
              cursor: "pointer",
            }}
            onClick={() => onSectionChange("diagram")}
          >
            🧩 View Diagram
          </button>
          
        </>
      )}
    </div>
  );
}
