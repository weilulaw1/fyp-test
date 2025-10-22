import './App.css';
import { useState } from "react";
import MenuBar from './MenuBar';
import Sidebar from './SideBar';
import DiagramView from './DiagramView'; 
import PlantUMLTestSVG from './plantUMLsvg';
import PlantUMLpdfTest from './plantUMLpdf';
import CodeViewer from './CodeViewer';
import FolderView from './FolderView'; 
function App() {
  // Sidebar + view control
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [activeSection, setActiveSection] = useState("folder");

  // Toggle sidebar visibility
  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  // Components for each diagram mode
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
        uploadedFiles={uploadedFiles}
        toggleSidebar={toggleSidebar}
        onFileClick={(filename) => {
          const relativePath = filename.replaceAll("\\", "/");
          setActiveFile(relativePath);
        }}
        onSectionChange={setActiveSection}
      />

      {/* MenuBar */}
      <MenuBar
        onToggleSidebar={toggleSidebar}
        sidebarOpen={sidebarOpen}
        setUploadedFiles={setUploadedFiles}
      />

      {/* Main content area */}
      <div
        style={{
          padding: "20px",
          paddingTop: "80px",
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
          marginLeft: sidebarOpen ? "250px" : "52px",
        }}
      >
        {activeSection === "diagram" ? (
          <DiagramView modeComponents={modeComponents} />
        ) : (
          <FolderView
            onFileClick={(file) => setActiveFile(file)}
            uploadedFiles={uploadedFiles}
            selectedFile={activeFile}
            setSelectedFile={setActiveFile}
          />
        )}
      </div>
    </div>
  );
}

export default App;
