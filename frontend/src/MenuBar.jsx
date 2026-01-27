import React, { useEffect, useState, useRef } from "react";

const menuItems = [
  {
    label: "File",
    actions: [
      { name: "Upload File", isSingleFile: true },

      // Keep your existing folder upload (to MEDIA/file tree)
      { name: "Upload Folder", isFileUpload: true },

      // NEW: load codebase into ArchRec workspace (files/codebases/current/)
      { name: "Load Codebase (Arch Rec)", isArchRecFolderUpload: true },

      // Repurpose Save -> Run Arch Rec
      { name: "Run Summarize (Arch Rec)", endpoint: "http://127.0.0.1:8000/api/archrec/run-summarize/", method: "POST" },
    ],
  },
  {
    label: "Edit",
    actions: [
      { name: "Undo", endpoint: "http://127.0.0.1:8000/api/edit/undo/" },
      { name: "Redo", endpoint: "http://127.0.0.1:8000/api/edit/redo/" },
    ],
  },
  {
    label: "View",
    actions: [
      { name: "Toggle Sidebar", endpoint: "http://127.0.0.1:8000/api/view/toggle_sidebar/" },
    ],
  },
];

export default function MenuBar({ onToggleSidebar, sidebarOpen, setUploadedFiles }) {
  const [openMenu, setOpenMenu] = useState(null);

  const SingleFileUpload = useRef(null);
  const FileUploadAction = useRef(null);

  // NEW: separate input for ArchRec codebase load
  const ArchRecFolderUpload = useRef(null);

  const handleClick = (action) => {
    if (action.isFileUpload) {
      FileUploadAction.current.click();
    } else if (action.isArchRecFolderUpload) {
      ArchRecFolderUpload.current.click();
    } else if (action.isSingleFile) {
      SingleFileUpload.current.click();
    } else {
      fetch(action.endpoint, {
        method: action.method || "GET",
      })
        .then(async (res) => {
          const data = await res.json().catch(() => ({}));
          if (!res.ok) throw new Error(data.error || "Request failed");
          return data;
        })
        .then((data) => {
          // optional: show something
          console.log("Action response:", data);

          // refresh file tree after running arch rec
          if (action.endpoint.includes("/api/archrec/run-summarize/")) {
            setUploadedFiles(Date.now());
          }
        })
        .catch((err) => console.error(err));
    }

    setOpenMenu(null);

    if (action.endpoint && action.endpoint.includes("toggle_sidebar")) {
      onToggleSidebar();
    }
  };

  // -----------------------------
  // Existing: Upload to MEDIA root (file tree)
  // -----------------------------
  const handleNormalUploadChange = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    const formData = new FormData();
    const filePaths = [];

    for (let i = 0; i < files.length; i++) {
      const path = files[i].webkitRelativePath || files[i].name;

      // your current exclusions (good)
      if (path.includes("node_modules") || path.includes("__pycache__") || path.includes(".venv")) {
        continue;
      }

      filePaths.push(path);
      formData.append("files", files[i]);
    }

    formData.append("file_paths", JSON.stringify(filePaths));

    try {
      const res = await fetch("http://127.0.0.1:8000/api/file/upload/", {
        method: "POST",
        body: formData,
      });
      await res.json();
      setUploadedFiles(Date.now());
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      e.target.value = null; // allow reselecting same folder
    }
  };

  // -----------------------------
  // NEW: Upload folder as "current codebase" for Arch Rec
  // Backend should:
  // - clear files/codebases/current/
  // - rebuild uploaded folder there
  // Endpoint: POST /api/archrec/upload-codebase/
  // -----------------------------
  const handleArchRecUploadChange = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    const formData = new FormData();
    const filePaths = [];

    for (let i = 0; i < files.length; i++) {
      const path = files[i].webkitRelativePath || files[i].name;

      // Keep excluding true junk. ArchRec does NOT need these.
      if (
        path.includes("node_modules") ||
        path.includes("__pycache__") ||
        path.includes(".venv") ||
        path.includes(".git") ||
        path.includes("dist") ||
        path.includes("build")
      ) {
        continue;
      }

      filePaths.push(path);
      formData.append("files", files[i]);
    }

    formData.append("file_paths", JSON.stringify(filePaths));

    try {
        const res = await fetch("http://127.0.0.1:8000/api/archrec/upload-project/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        console.error("ArchRec codebase load failed:", data);
        alert(data.error || "ArchRec codebase load failed");
        return;
      }

      console.log("ArchRec codebase loaded:", data);
      alert(`Loaded codebase into ArchRec workspace. Files saved: ${data.files_saved ?? "?"}`);

      // refresh file tree (if your UI shows codebases/current or artifacts)
      setUploadedFiles(Date.now());
    } catch (err) {
      console.error("ArchRec upload failed:", err);
      alert("ArchRec upload failed (network/server error)");
    } finally {
      e.target.value = null;
    }
  };

  // close menu when click outside
  useEffect(() => {
    const handleOutsideClick = () => setOpenMenu(null);
    window.addEventListener("click", handleOutsideClick);
    return () => window.removeEventListener("click", handleOutsideClick);
  }, []);

  return (
    <div
      style={{
        display: "flex",
        background: "#ffffffff",
        padding: "10px",
        alignItems: "center",
        position: "fixed",
        justifyContent: "flex-start",
        top: 0,
        left: sidebarOpen ? "250px" : "52px",
        width: sidebarOpen ? "calc(100% - 250px)" : "calc(100% - 20px)",
        borderBottom: "2px solid #333",
        transition: "left 0.3s ease, width 0.3s ease",
        zIndex: 1000,
      }}
      onClick={(e) => e.stopPropagation()}
    >
      {menuItems.map((menu, index) => (
        <div
          key={menu.label}
          style={{
            position: "relative",
            padding: "5px 15px",
            fontWeight: "bold",
            cursor: "pointer",
            color: "black",
            borderRight: index !== menuItems.length - 1 ? "2px solid #333" : "none",
          }}
          onMouseEnter={() => setOpenMenu(menu.label)}
          onMouseLeave={() => setOpenMenu(null)}
        >
          {menu.label}
          {openMenu === menu.label && (
            <div
              style={{
                position: "absolute",
                top: "35px",
                left: 0,
                background: "#f9f9f9",
                border: "1px solid #333",
                borderRadius: "4px",
                padding: "5px 0",
                boxShadow: "1px 1px 3px rgba(0,0,0,0.2)",
                minWidth: "180px",
                color: "black",
                zIndex: 1000,
              }}
              className="dropdown"
            >
              {menu.actions.map((action) => (
                <div
                  key={action.name}
                  onClick={() => handleClick(action)}
                  style={{ padding: "5px 10px", cursor: "pointer" }}
                  onMouseEnter={(e) => (e.target.style.background = "#ddd")}
                  onMouseLeave={(e) => (e.target.style.background = "white")}
                >
                  {action.name}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Single file upload (JSON etc.) */}
      <input
        type="file"
        ref={SingleFileUpload}
        style={{ display: "none" }}
        onChange={handleNormalUploadChange}
      />

      {/* Existing folder upload -> MEDIA */}
      <input
        type="file"
        webkitdirectory="true"
        multiple
        ref={FileUploadAction}
        style={{ display: "none" }}
        onChange={handleNormalUploadChange}
      />

      {/* NEW folder upload -> ArchRec workspace */}
      <input
        type="file"
        webkitdirectory="true"
        multiple
        ref={ArchRecFolderUpload}
        style={{ display: "none" }}
        onChange={handleArchRecUploadChange}
      />
    </div>
  );
}
