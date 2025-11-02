import React from "react";
import SidebarOutIcon from './assets/sidebar out.png';
import SidebarInIcon from './assets/sidebar in.png';
import FolderView from "./FolderView";

export default function Sidebar({
  isOpen,
  toggleSidebar,
  uploadedFiles = [],
  onFileClick,
  selectedFile,
  setSelectedFile,
}) {
  return (
    <div
      style={{
        width: isOpen ? "250px" : "52px",
        transition: "width 0.3s ease",
        overflowY: "auto",
        overflowX: "hidden",
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

      {/* Sidebar content */}
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
            onClick={() => {
              fetch("http://localhost:8000/api/run-json-to-uml/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename: "bash_summary.json" }),
              })
                .then((res) => res.json())
                .then((data) => alert(`✅ ${data.message || "Command executed"}`))
                .catch((err) => alert(`❌ Error: ${err.message}`));
            }}
          >
            JSON to UML
          </button>

          {/* Folder view inside sidebar */}
          <div
            style={{
              width: "100%",
              padding: "10px",
              overflowY: "auto",
              flexGrow: 1,
            }}
          >
            <FolderView
              onFileClick={onFileClick}
              uploadedFiles={uploadedFiles}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
            />
          </div>
        </>
      )}
    </div>
  );
}
