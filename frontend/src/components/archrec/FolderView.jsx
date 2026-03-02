import React, { useEffect, useMemo, useState } from "react";

// Helper: build nested folder tree
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

// Recursive tree renderer
function FileTree({
  tree,
  level = 0,
  parentPath = "",
  onFileClick,
  onFileDelete,
  selectedFile,
  rootKey,
}) {
  const [expandedFolders, setExpandedFolders] = useState({});

  const toggleFolder = (folderKey) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [folderKey]: !prev[folderKey],
    }));
  };

  const handleDelete = async (fullpath) => {
    if (!window.confirm(`Delete "${fullpath}"? This cannot be undone.`)) return;

    try {
      const formData = new FormData();
      formData.append("path", fullpath);
      formData.append("root", rootKey); 

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
                  isFolder ? () => toggleFolder(key) : () => onFileClick(fullpath)
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
                {/* Delete icon */}
                <span
                  style={{
                    cursor: "pointer",
                    color: "red",
                    marginLeft: "-5px",
                    flexShrink: 0,
                    marginRight: 6,
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(fullpath);
                  }}
                  title="Delete"
                >
                  ❌
                </span>

                {/* Folder/File icon */}
                <span style={{ marginRight: "6px" }}>
                  {isFolder ? (expandedFolders[key] ? "📂" : "📁") : "📄"}
                </span>

                <span>{name}</span>
              </div>
            </div>

            {isFolder && expandedFolders[key] && (
              <FileTree
                tree={children}
                level={level + 1}
                parentPath={fullpath}
                onFileClick={onFileClick}
                onFileDelete={onFileDelete}
                selectedFile={selectedFile}
                rootKey={rootKey}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
}

// MAIN COMPONENT
export default function FolderView({
  onFileClick,
  uploadedFiles = [],
  selectedFile,
  setSelectedFile,
  rootKey,
  setRootKey,
}) {
  const [files, setFiles] = useState(uploadedFiles);

  // Fetch file list from backend whenever root changes or uploads change
  useEffect(() => {
    fetch(`http://localhost:8000/api/files/?root=${encodeURIComponent(rootKey)}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.files)) setFiles(data.files);
        else setFiles([]);
      })
      .catch((err) => console.error("Failed to fetch files:", err));
  }, [uploadedFiles, rootKey]);

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
    setSelectedFile?.(fullpath);
    onFileClick?.(fullpath, rootKey);  
  };

  const tree = useMemo(() => buildFileTree(files), [files]);

  return (
    <div style={{ padding: "20px" }}>
      <h2>📁 Files</h2>

      {/* Root toggle */}
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button
          onClick={() => {
            setRootKey("media");
            setSelectedFile?.(null);
          }}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.2)",
            background: rootKey === "media" ? "rgba(255,255,255,0.15)" : "transparent",
            cursor: "pointer",
          }}
        >
          Uploads
        </button>

        <button
          onClick={() => {
            setRootKey("projects");
            setSelectedFile?.(null);
          }}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.2)",
            background:
              rootKey === "projects" ? "rgba(255,255,255,0.15)" : "transparent",
            cursor: "pointer",
          }}
        >
          Projects
        </button>
      </div>

      {files.length > 0 ? (
        <FileTree
          tree={tree}
          onFileClick={handleFileClick}
          onFileDelete={handleFileDelete}
          selectedFile={selectedFile}
          rootKey={rootKey}
        />
      ) : (
        <p>No files found</p>
      )}
    </div>
  );
}