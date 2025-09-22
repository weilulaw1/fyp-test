import './App.css'
import { useState } from "react";
import MenuBar from './MenuBar';
import Sidebar from './SideBar';
import PlantUMLViewer from './plantUML';
import PlantUMLTest from './plantUMLtest'
import PlantUMLTestSVG from './plantUMLsvgTest';
import PlantUMLpdfTest from './plantUMLpdfTest';

function App() {
    // State to control sidebar visibility
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [viewMode, setViewMode] = useState("pdf");

    //Fucntion to Toggle sidebar, will be passed to menubar
    const toggleSidebar = () => setSidebarOpen((prev) => !prev);

    
  return (
    <div>
       {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} 
      uploadedFiles={uploadedFiles} 
      toggleSidebar={toggleSidebar} 


      />
      {/* MenuBar now receives toggleSidebar function */}
      <MenuBar onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen} 
      setUploadedFiles={setUploadedFiles} 
      />
      {/* Main content, shifts when sidebar is open */}
      <div
        style={{
          marginLeft: sidebarOpen ? "250px" : "0",
          padding: "20px",
          paddingTop: "80px",
          transition: "margin-left 0.3s ease",
          minHeight: "100vh",
        }}
      >
        {/*Switch Buttons*/}
        <div style={{ marginBottom: "20px" }}>
          <button 
            onClick={() => setViewMode("pdf")} 
            style={{ marginRight: "10px" }}
          >
            PDF View
          </button>
          <button onClick={() => setViewMode("svg")}>
            SVG View
          </button>
        </div>
        
        <div style={{ 
          maxWidth: "1000px",
          width:"100%",
          margin: "0 auto",
          }}>
         {viewMode === "pdf"? <PlantUMLpdfTest/>:<PlantUMLTestSVG/>}
        </div>      </div>
    </div>
  );
}
export default App;