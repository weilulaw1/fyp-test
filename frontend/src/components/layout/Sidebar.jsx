import React, {useState} from "react";
import SidebarOutIcon from '../../assets/sidebar-out.png';
import SidebarInIcon from '../../assets/sidebar-in.png';
import FolderView from "../archrec/FolderView";

export default function Sidebar({
  isOpen,
  toggleSidebar,
  uploadedFiles = [],
  onFileClick,
  selectedFile,
  setSelectedFile,
  rootKey,
  setRootKey,
})
{

  const [selectedFileToUpload, setSelectedFileToUpload] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFileToUpload(e.target.files[0]);
  };

  const handleUploadAndRun = async (e) => {
    e?.preventDefault();
  
    if (!selectedFileToUpload) {
      alert("Please select a JSON file first!");
      return;
    }
  
    const formData = new FormData();
    formData.append("json_file", selectedFileToUpload);
  
    const res = await fetch("http://localhost:8000/api/run-json-to-uml/", {
      method: "POST",
      body: formData,
    });
  
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); }
    catch { data = { error: text }; }
  
    if (!res.ok) {
      alert(`❌ HTTP ${res.status}\n${data.error || "Request failed"}\n\n${data.details || ""}`);
      return;
    }
  
    alert(`✅ ${data.status || "OK"}`);
  };
  
  return (
    <div
      style={{
        width: isOpen ? "250px" : "52px",
        transition: "width 0.3s ease",
        overflowY: "auto",
        overflowX: "hidden",
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        background: "#333",
        color: "white",
        zIndex: 1100,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: "60px",
      }}
    >
      {/* Sidebar toggle button */}
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          cursor: "pointer",
        }}
        onClick={toggleSidebar}
      >
        <img
          src={isOpen ? SidebarInIcon : SidebarOutIcon}
          alt="Toggle Sidebar"
          width={30}
          height={30}
          style={{ filter: "invert(1)" }}
        />
      </div>

      {/* Sidebar content */}
      {isOpen && (
        <>
          {/* File input */}
          <input
            type="file"
            accept=".json"
            onChange={handleFileChange}
            style={{
              margin: "10px 0",
              width: "180px",
              padding: "5px",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          />

          {/* Upload & run button */}
          <button
            style={{
              margin: "10px 0",
              width: "180px",
              padding: "10px",
              backgroundColor:selectedFileToUpload?"#555": "#888",
              border: "none",
              borderRadius: "6px",
              color: "white",
              cursor: selectedFileToUpload ? "pointer" : "not-allowed",
            }}
            onClick={handleUploadAndRun}
            disabled={!selectedFileToUpload}
          >
            JSON to UML
          </button>

          {/* Folder view inside sidebar */}
          <div
            style={{
              width: "100%",
              padding: "10px",
              overflowY: "auto",
              flexGrow: 1,
            }}
          >
            <FolderView
              onFileClick={onFileClick}
              uploadedFiles={uploadedFiles}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              rootKey={rootKey}
              setRootKey={setRootKey}
            />
          </div>
        </>
      )}
    </div>
  );
}
