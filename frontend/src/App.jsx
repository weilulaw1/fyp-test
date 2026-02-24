import "./styles/App.css";
import { useState } from "react";

import DashboardLayout from "./layouts/DashboardLayout";

import DiagramView from "./components/archrec/DiagramView";
import PlantUMLTestSVG from "./components/archrec/plantUMLsvg";
import PlantUMLpdfTest from "./components/archrec/plantUMLpdf";
import CodeViewer from "./components/archrec/CodeViewer";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

/*  const modeComponents = {
    SVG: <PlantUMLTestSVG file={activeFile} />,
    PDF: <PlantUMLpdfTest file={activeFile} />,
    Code: <CodeViewer file={activeFile} />,
  }; */

  return (
    <DashboardLayout
      sidebarOpen={sidebarOpen}
      onToggleSidebar={toggleSidebar}
      uploadedFiles={uploadedFiles}
      setUploadedFiles={setUploadedFiles}
      activeFile={activeFile}
      setActiveFile={setActiveFile}
    >
      <DiagramView>
        <PlantUMLTestSVG file = {activeFile}/>
        </DiagramView>
    </DashboardLayout>
  );
}

export default App;
