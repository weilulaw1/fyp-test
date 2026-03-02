import "./styles/App.css";
import { useEffect, useState } from "react";

import DashboardLayout from "./layouts/DashboardLayout";

import DiagramView from "./components/archrec/DiagramView";
import PlantUMLTestSVG from "./components/archrec/plantUMLsvg";
import CodeViewer from "./components/archrec/CodeViewer";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const [activeFile, setActiveFile] = useState(null);
  const [rootKey, setRootKey] = useState("media");

  const [viewMode, setViewMode] = useState("diagram"); // "diagram" | "code"

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const root = params.get("root") || "media";
    const file = params.get("file");

    setRootKey(root);

    if (file) {
      setActiveFile(file);
      setViewMode("diagram");
    }
  }, []);

  return (
    <DashboardLayout
      sidebarOpen={sidebarOpen}
      onToggleSidebar={toggleSidebar}
      uploadedFiles={uploadedFiles}
      setUploadedFiles={setUploadedFiles}
      activeFile={activeFile}
      setActiveFile={setActiveFile}
      rootKey={rootKey}
      setRootKey={setRootKey}
      viewMode={viewMode}
      setViewMode={setViewMode}
    >
      {/* Simple top toggle */}
      <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 10 }}>
        <button
          onClick={() => setViewMode("diagram")}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.2)",
            background: viewMode === "diagram" ? "rgba(255,255,255,0.15)" : "transparent",
            cursor: "pointer",
          }}
        >
          Diagram
        </button>

        <button
          onClick={() => setViewMode("code")}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.2)",
            background: viewMode === "code" ? "rgba(255,255,255,0.15)" : "transparent",
            cursor: "pointer",
          }}
        >
          Code
        </button>
      </div>

      {viewMode === "diagram" ? (
        <DiagramView>
          <PlantUMLTestSVG file={activeFile} />
        </DiagramView>
      ) : (
        <CodeViewer file={activeFile} rootKey={rootKey} />
      )}
    </DashboardLayout>
  );
}

export default App;