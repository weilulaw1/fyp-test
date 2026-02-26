import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function DashboardLayout({
  sidebarOpen,
  onToggleSidebar,
  uploadedFiles,
  setUploadedFiles,
  activeFile,
  setActiveFile,
  children,
}) {
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
        onFileClick={(f) => setActiveFile(f)}
        selectedFile={activeFile}
        setSelectedFile={setActiveFile}
      />

      <Topbar 
      sidebarOpen={sidebarOpen} 
      onToggleSidebar={onToggleSidebar}
      setUploadedFiles={setUploadedFiles}   />

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
        {children}
      </main>
    </div>
  );
}
