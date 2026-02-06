import "./styles/App.css";
import { useState } from "react";

import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";

import DiagramView from "./components/archrec/DiagramView";
import PlantUMLTestSVG from "./components/archrec/plantUMLsvg";
import PlantUMLpdfTest from "./components/archrec/plantUMLpdf";
import CodeViewer from "./components/archrec/CodeViewer";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  const modeComponents = {
    SVG: <PlantUMLTestSVG file={activeFile} />,
    PDF: <PlantUMLpdfTest file={activeFile} />,
    Code: <CodeViewer file={activeFile} />,
  };

  return (
    <div>
      <Sidebar
        isOpen={sidebarOpen}
        toggleSidebar={toggleSidebar}
        uploadedFiles={uploadedFiles}
        onFileClick={(filename) => {
          const relativePath = filename.replaceAll("\\", "/");
          setActiveFile(relativePath);
        }}
        selectedFile={activeFile}
        setSelectedFile={setActiveFile}
      />

      <Topbar
        onToggleSidebar={toggleSidebar}
        sidebarOpen={sidebarOpen}
        setUploadedFiles={setUploadedFiles}
      />

      <div
        style={{
          padding: "20px",
          paddingTop: "80px",
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
          marginLeft: sidebarOpen ? "250px" : "52px",
        }}
      >
        <DiagramView modeComponents={modeComponents} />
      </div>
    </div>
  );
}

export default App;
