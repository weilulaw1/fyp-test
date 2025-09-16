import './App.css'
import { useState } from "react";
import MenuBar from './MenuBar';
import Sidebar from './SideBar';
import PlantUMLViewer from './plantUML';

function App() {
    // State to control sidebar visibility
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    //Fucntion to Toggle sidebar, will be passed to menubar
    const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  return (
    <div>
       {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} 
      uploadedFiles={uploadedFiles} 

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
          transition: "margin-left 0.3s ease",
        }}
      >
        <h1>Home Page 1</h1>
        <PlantUMLViewer/>
      </div>
    </div>
  );
}
export default App;