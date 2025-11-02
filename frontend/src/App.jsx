import './App.css';
import { useState } from "react";
import MenuBar from './MenuBar';
import Sidebar from './SideBar';
import DiagramView from './DiagramView';
import PlantUMLTestSVG from './plantUMLsvg';
import PlantUMLpdfTest from './plantUMLpdf';
import CodeViewer from './CodeViewer';

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
      {/* Sidebar */}
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

      {/* Menu bar */}
      <MenuBar
        onToggleSidebar={toggleSidebar}
        sidebarOpen={sidebarOpen}
        setUploadedFiles={setUploadedFiles}
      />

      {/* Main content */}
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
