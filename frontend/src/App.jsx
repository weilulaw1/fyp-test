import './App.css'
import { useState } from "react";
import MenuBar from './MenuBar';
import Sidebar from './SideBar';
import PlantUMLViewer from './plantUML';
import PlantUMLTestSVG from './plantUMLsvg';
import PlantUMLpdfTest from './plantUMLpdf';
import CodeViewer from './CodeViewer';

function App() {
    // State to control sidebar visibility
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [viewMode, setViewMode] = useState("SVG");
    const [activeFile, setActiveFile] = useState(null);

    //Fucntion to Toggle sidebar, will be passed to menubar
    const toggleSidebar = () => setSidebarOpen((prev) => !prev);


    const modeComponents = {
    SVG: (<PlantUMLTestSVG
      file = {activeFile} 
      />),      

    PDF: (<PlantUMLpdfTest 
      file = {activeFile}
    />),

    Code: (<CodeViewer
    file = {activeFile}
      />) ,  
    // just add more later
    // txt: <PlantUMLtxtTest />
  };
    
  return (
    <div>
       {/* Sidebar */}
      <Sidebar
      isOpen={sidebarOpen} 
      uploadedFiles={uploadedFiles} 
      toggleSidebar={toggleSidebar} 
      onFileClick={(filename)=>{
        const relativePath = filename.replaceAll("\\","/")
        setActiveFile(relativePath);
        //setViewMode("Code")
      }}
      />
      {/* MenuBar now receives toggleSidebar function */}
      <MenuBar onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen} 
      setUploadedFiles={setUploadedFiles} 
      />

      {/* Main content */}
      <div
        style={{
          marginLeft: sidebarOpen ? "250px" : "0",
          padding: "20px",
          paddingTop: "80px",
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
        }}
      >
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
    </div>
  );
}

export default App;