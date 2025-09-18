import React, {useEffect,useState} from "react";
import FileExploreIcon from "./assets/folder.png";
import SidebarOutIcon from './assets/sidebar out.png';
import SidebarInIcon from './assets/sidebar in.png';

function buildFileTree(paths) {
  const tree = {};
  paths.forEach(path => {
    const parts = path.split("/");
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

function FileTree({ tree, level = 0 }) {
  const [expandedFolders, setExpandedFolders] = useState({});

  const toggleFolder = (path) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [path]: !prev[path]
    }));
  }; 


  return (
    <ul style={{ listStyle: "none", paddingLeft: level * 15 + "px" }}>
      {Object.entries(tree).map(([name, children]) => {
        const isFolder = children !== null;
        const path = `${level}-${name}`; // unique key for expanded state

        return (
          <li key={path}>
            {isFolder ? (
              <>
                <span
                  style={{ fontWeight: "bold", cursor: "pointer" }}
                  onClick={() => toggleFolder(path)}
                >
                  {expandedFolders[path] ? "📂" : "📁"} {name}
                </span>
                {expandedFolders[path] && <FileTree tree={children} level={level + 1} />}
              </>
            ) : (
              <span>📄 {name}</span>
            )}
          </li>
        );
      })}
    </ul>
  );
}

export default function Sidebar({ isOpen, toggleSidebar }) {
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
            <FileTree tree={tree} />
          ) : (
            <p>No files uploaded</p>
          )}
        </div>
      )}
    </div>
  );
}
