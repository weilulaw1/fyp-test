import React, {useEffect,useState} from "react";
import FileExploreIcon from "./assets/folder.png";
import SidebarOutIcon from './assets/sidebar out.png';
import SidebarInIcon from './assets/sidebar in.png';

function buildFileTree(paths) {
  const tree = {};
  paths.forEach(path => {
  const parts = path.split(/[\\/]/);
    let current = tree;
    parts.forEach((part, idx) => {
      if (!current[part]) {
        current[part] = idx === parts.length - 1 ? null : {};
      }
      current = current[part];
    });
  });
  return tree;
}

function FileTree({ tree, level = 0, parentPath="",onFileClick, onFileDelete }) {
  const [expandedFolders, setExpandedFolders] = useState({});

  const toggleFolder = (path) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [path]: !prev[path]
    }));
  }; 
  const handleDelete = async (fullpath) => {
    if (!window.confirm(`Delete "${fullpath}"? This cannot be undone.`)) return;
    try {
      const formData = new FormData();
      formData.append("path", fullpath);

      const res = await fetch("http://localhost:8000/api/delete-file/", {
        method: "POST",
        body: formData,
      });

      let data;
      try {
        data = await res.json();
      } catch {
        alert("Server returned invalid JSON");
        return;
      }
      if (data.success) {
        alert(`Deleted "${fullpath}" successfully`);
        onFileDelete(fullpath); // notify parent to update file list
      } else {
        alert(`Failed to delete: ${data.error}`);
      }
    } catch (err) {
      console.error(err);
      alert("Error deleting file");
    }
  };

  return (
    <ul style={{ listStyle: "none", paddingLeft: level * 15 + "px" }}>
      {Object.entries(tree).map(([name, children]) => {
        const isFolder = children !== null;
        const fullpath = parentPath ? `${parentPath}/${name}` : name;
        const key = `${level}-${fullpath}`; // unique key for expanded state

        return (
          <li key={key}>
            {isFolder ? (
              <>
                <span
                  style={{ fontWeight: "bold", cursor: "pointer" }}
                  onClick={() => toggleFolder(key)}
                >
                  <span
                  style={{ cursor: "pointer", color: "red" }}
                  onClick={(e) => {
                    e.stopPropagation(); // prevent toggling folder
                    handleDelete(fullpath);
                  }}
                >
                  ❌
                </span>
                  {expandedFolders[key] ? "📂" : "📁"} {name}
                </span>
                {expandedFolders[key] && <FileTree 
                tree={children} 
                level={level + 1} 
                parentPath = {fullpath}
                onFileClick={onFileClick} 
                onFileDelete={onFileDelete}
                />}
              </>
            ) : (
              <>
              <span
                style={{fontWeight: "bold", cursor: "pointer"}}
                onClick={()=>onFileClick && onFileClick(fullpath)}
              >📄 {name}
              </span>
              <span
              style={{ cursor: "pointer", color: "red" }}
              onClick={() => handleDelete(fullpath)}
              >
                ❌  
              </span>
              </>
              )}
          </li>
        );
      })}
    </ul>
  );
}

export default function Sidebar({ isOpen, toggleSidebar, onFileClick }) {
  const [uploadedFiles , setUploadedFiles] = useState([]);
  useEffect(() => {
    fetch("http://localhost:8000/api/files/")      
    .then((res) => res.json())
      .then((data) => {
        if (data.files) {
          setUploadedFiles(data.files);
        }
      })
      .catch((err) => console.error("Failed to fetch files:", err));
  }, []);
  const handleFileDelete = (fullpath) => {
    setUploadedFiles((prev) => prev.filter((file) => file !== fullpath));
  };

  const tree = buildFileTree(uploadedFiles);
    
  return (
    <div
      style={{
        width: isOpen ? '250px' : '52px',
        transition: 'width 0.3s ease',
        overflow: 'hidden',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        background: '#333',
        borderRight: '2px solid #333',
        zIndex: 1100,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Sidebar toggle button - always visible */}
      <div
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          cursor: 'pointer',
          zIndex: 1000
        }}
        onClick={toggleSidebar}
      >
        <img
          src={isOpen ? SidebarInIcon : SidebarOutIcon}
          alt="Toggle Sidebar"
          width={30}
          height={30}
          style={{ filter: 'invert(1)' }}
        />
      </div>

      {/* Scrollable content */}
      {isOpen && (
        <div
          style={{
            padding: '50px 10px 10px 10px',
            overflowY: 'auto',       // enable vertical scroll
            flex: 1,                  // take remaining height
          }}
        >
          <h2>Sidebar</h2>
          <div>
            <img
              src={FileExploreIcon}
              alt="FileExploreIcon"
              width={32}
              height={32}
              style={{ filter: 'invert(1)' }}
            />
          </div>

          <h2>Uploaded Files</h2>
          {uploadedFiles.length > 0 ? (
            <FileTree 
            tree={tree} 
            onFileClick={onFileClick}
            onFileDelete={handleFileDelete} 
            />
          ) : (
            <p>No files uploaded</p>
          )}
        </div>
      )}
    </div>
  );
}
