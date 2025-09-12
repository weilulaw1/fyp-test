import React from "react";
import FileExploreIcon from "./assets/folder.png";

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

function FileTree({ tree }) {
  return (
    <ul style={{ listStyle: "none", paddingLeft: "15px" }}>
      {Object.entries(tree).map(([name, children]) => (
        <li key={name}>
          {children ? (
            <>
              <span style={{ fontWeight: "bold" }}>📂 {name}</span>
              <FileTree tree={children} />
            </>
          ) : (
            <span>📄 {name}</span>
          )}
        </li>
      ))}
    </ul>
  );
}

export default function Sidebar({ isOpen, uploadedFiles = [] }) {
  const tree = buildFileTree(uploadedFiles);

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: isOpen ? 0 : "-250px",
        height: "100%",
        width: "250px",
        background: "#333",
        color: "#fff",
        padding: "20px",
        transition: "left 0.3s ease",
        zIndex: 999,
        overflowY: "auto"
      }}
    >
      <h2>Sidebar</h2>
      <div>
        <img
          src={FileExploreIcon}
          alt="FileExploreIcon"
          width={32}
          height={32}
          style={{ filter: "invert(1)" }}
        />
      </div>

      <h2>Uploaded Files</h2>
      {uploadedFiles.length > 0 ? (
        <FileTree tree={tree} />
      ) : (
        <p>No files uploaded</p>
      )}
    </div>
  );
}
