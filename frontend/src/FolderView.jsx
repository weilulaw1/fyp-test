import React, { useEffect, useState } from "react";

// Helper: build nested folder tree (UNCHANGED)
function buildFileTree(paths) {
  const tree = {};
  paths.forEach((path) => {
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

// Recursive tree renderer (UNCHANGED structure)
function FileTree({
  tree,
  level = 0,
  parentPath = "",
  onFileClick,
  onFileDelete,
  selectedFile,
}) {
  const [expandedFolders, setExpandedFolders] = useState({});

  const toggleFolder = (path) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [path]: !prev[path],
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

      const data = await res.json();
      if (data.success) {
        onFileDelete(fullpath);
      } else {
        alert(`Failed to delete: ${data.error}`);
      }
    } catch (err) {
      console.error(err);
      alert("Error deleting file");
    }
  };

  return (
    <ul style={{ listStyle: "none", paddingLeft: level * 20 + "px", margin: 0 }}>
      {Object.entries(tree).map(([name, children]) => {
        const isFolder = children !== null;
        const fullpath = parentPath ? `${parentPath}/${name}` : name;
        const key = `${level}-${fullpath}`;
        const isSelected = selectedFile === fullpath;

        return (
          <li key={key} style={{ margin: "4px 0" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                backgroundColor: isSelected
                  ? "rgba(255, 255, 255, 0.1)"
                  : "transparent",
                borderRadius: "4px",
                padding: "2px 6px",
                cursor: "pointer",
              }}
            >
              <div
                onClick={
                  isFolder
                    ? () => toggleFolder(key)
                    : () => onFileClick(fullpath)
                }
                style={{
                  display: "flex",
                  alignItems: "center",
                  flexGrow: 1,
                  textDecoration: isSelected ? "underline" : "none",
                  textDecorationColor: isSelected ? "red" : "inherit",
                  fontWeight: isFolder ? "bold" : "normal",
                }}
              >
                <span style={{ marginRight: "6px" }}>
                  {isFolder
                    ? expandedFolders[key]
                      ? "📂"
                      : "📁"
                    : "📄"}
                </span>
                <span>{name}</span>
              </div>

              <span
                style={{
                  cursor: "pointer",
                  color: "red",
                  marginLeft: "10px",
                  flexShrink: 0,
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(fullpath);
                }}
              >
                ❌
              </span>
            </div>

            {isFolder && expandedFolders[key] && (
              <FileTree
                tree={children}
                level={level + 1}
                parentPath={fullpath}
                onFileClick={onFileClick}
                onFileDelete={onFileDelete}
                selectedFile={selectedFile}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
}

// MAIN COMPONENT (minimal fix only)
export default function FolderView({
  onFileClick,
  uploadedFiles = [],
  selectedFile,
  setSelectedFile,
}) {
  const [files, setFiles] = useState(uploadedFiles);


  // On refresh: fetch from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/files/")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.files)) {
          setFiles(data.files);
        }
      })
      .catch((err) => console.error("Failed to fetch files:", err));
  }, [uploadedFiles]);
  

  const handleFileDelete = (fullpath) => {
    if (setSelectedFile && selectedFile === fullpath) {
      setSelectedFile(null);
    }

    // remove file or entire folder subtree from UI
    setFiles((prev) =>
      prev.filter((p) => p !== fullpath && !p.startsWith(fullpath + "/"))
    );
  };

  const handleFileClick = (fullpath) => {
    if (setSelectedFile) setSelectedFile(fullpath);
    if (onFileClick) onFileClick(fullpath);
  };

  const tree = buildFileTree(files);

  return (
    <div style={{ padding: "20px" }}>
      <h2>📁 Folder View</h2>
      {files.length > 0 ? (
        <FileTree
          tree={tree}
          onFileClick={handleFileClick}
          onFileDelete={handleFileDelete}
          selectedFile={selectedFile}
        />
      ) : (
        <p>No files uploaded</p>
      )}
    </div>
  );
}