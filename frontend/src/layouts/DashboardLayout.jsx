import React, { useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar"; // your MenuBar

export default function DashboardLayout({
  sidebarOpen,
  onToggleSidebar,
  uploadedFiles,
  setUploadedFiles,
  activeFile,
  setActiveFile,
  children,
  rootKey,
  setRootKey,
  viewMode,
  setViewMode,
}) {
  const [showOutput, setShowOutput] = useState(true);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "transparent",
        overflow: "visible",
      }}
    >
      <Sidebar
        isOpen={sidebarOpen}
        toggleSidebar={onToggleSidebar}
        uploadedFiles={uploadedFiles}
        onFileClick={(f, root) => {
          setActiveFile(f);
          setRootKey(root);
        }}
        selectedFile={activeFile}
        setSelectedFile={setActiveFile}
        rootKey={rootKey}
        setRootKey={setRootKey}
      />

      <Topbar
        sidebarOpen={sidebarOpen}
        onToggleSidebar={onToggleSidebar}
        setUploadedFiles={setUploadedFiles}
        showOutput={showOutput}
        setShowOutput={setShowOutput}
        viewMode={viewMode}        
        setViewMode={setViewMode}
      />

      <main
        style={{
          marginLeft: sidebarOpen ? "250px" : "52px",
          paddingTop: "72px",
          padding: "24px",
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            maxHeight: showOutput ? "9999px" : "0px",
            opacity: showOutput ? 1 : 0,
            transform: showOutput ? "translateY(0)" : "translateY(-6px)",
            overflow: "hidden",
            transition: "max-height 300ms ease, opacity 200ms ease, transform 200ms ease",
            pointerEvents: showOutput ? "auto" : "none",
          }}
        >
          {children}
        </div>
      </main>
    </div>
  );
}