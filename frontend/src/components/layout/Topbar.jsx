import React, { useEffect, useMemo, useRef, useState } from "react";

const PIPELINE_ENDPOINT = "http://127.0.0.1:8000/api/archrec/run-summarize/";
const UPLOAD_MEDIA_ENDPOINT = "http://127.0.0.1:8000/api/file/upload/";
const ARCHREC_UPLOAD_ENDPOINT = "http://127.0.0.1:8000/api/archrec/upload-project/";

const menuItems = [
  {
    label: "File",
    actions: [
      { name: "Upload File", isSingleFile: true },
      { name: "Upload Folder", isFileUpload: true },
      { name: "Load Codebase (Arch Rec)", isArchRecFolderUpload: true },
      {
        name: "Run Pipeline (Summarize → UML)",
        endpoint: PIPELINE_ENDPOINT,
        method: "POST",
        isPipeline: true,
      },
    ],
  },
  
];

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export default function MenuBar({ onToggleSidebar, sidebarOpen, setUploadedFiles }) {
  const [openMenu, setOpenMenu] = useState(null);

  const SingleFileUpload = useRef(null);
  const FileUploadAction = useRef(null);
  const ArchRecFolderUpload = useRef(null);

  // Pipeline UI state
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [pipelineMsg, setPipelineMsg] = useState("");
  const [pipelineResult, setPipelineResult] = useState(null);
  const [showPipelineDetails, setShowPipelineDetails] = useState(false);

  const isBusy = isPipelineRunning;

  const menus = useMemo(() => menuItems, []);

  const runFetchAction = async (action) => {
    const isPipeline = !!action.isPipeline;

    if (isPipeline) {
      setIsPipelineRunning(true);
      setPipelineMsg("Running pipeline… (Summarize → UML → publish)");
      setPipelineResult(null);
      setShowPipelineDetails(false);
    }

    try {
      const res = await fetch(action.endpoint, {
        method: action.method || "GET",
      });

      // Some endpoints may return non-JSON on error; handle safely
      const text = await res.text();
      const data = safeJsonParse(text) ?? { raw: text };

      if (!res.ok) {
        const errMsg = data?.error || data?.detail || "Request failed";
        throw new Error(errMsg);
      }

      // success
      if (isPipeline) {
        setPipelineMsg("Done! Outputs published to folder view.");
        setPipelineResult(data);
        setUploadedFiles(Date.now());
        // keep details available
        setShowPipelineDetails(true);
      }

      // sidebar toggle
      if (action.endpoint?.includes("toggle_sidebar")) {
        onToggleSidebar();
      }

      console.log("Action response:", data);
    } catch (err) {
      console.error(err);
      if (isPipeline) {
        setPipelineMsg(`Error: ${err.message}`);
        setPipelineResult({ error: err.message });
        setShowPipelineDetails(true);
      }
    } finally {
      if (isPipeline) {
        // Let user read the final message briefly
        setTimeout(() => setIsPipelineRunning(false), 600);
      }
    }
  };

  const handleClick = (action) => {
    // Block pipeline double-clicks
    if (action.isPipeline && isBusy) return;

    if (action.isFileUpload) {
      FileUploadAction.current?.click();
    } else if (action.isArchRecFolderUpload) {
      ArchRecFolderUpload.current?.click();
    } else if (action.isSingleFile) {
      SingleFileUpload.current?.click();
    } else if (action.endpoint) {
      runFetchAction(action);
    }

    setOpenMenu(null);
  };

  // Upload to MEDIA root (file tree)
  const handleNormalUploadChange = async (e) => {
    const files = e.target.files;
    if (!files || !files.length) return;

    const formData = new FormData();
    const filePaths = [];

    for (let i = 0; i < files.length; i++) {
      const path = files[i].webkitRelativePath || files[i].name;

      if (path.includes("node_modules") || path.includes("__pycache__") || path.includes(".venv")) {
        continue;
      }

      filePaths.push(path);
      formData.append("files", files[i]);
    }

    formData.append("file_paths", JSON.stringify(filePaths));

    try {
      const res = await fetch(UPLOAD_MEDIA_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Upload failed");
      setUploadedFiles(Date.now());
    } catch (err) {
      console.error("Upload failed:", err);
      alert(`Upload failed: ${err.message}`);
    } finally {
      e.target.value = null;
    }
  };

  // Upload folder to ArchRec workspace
  const handleArchRecUploadChange = async (e) => {
    const files = e.target.files;
    if (!files || !files.length) return;

    const formData = new FormData();
    const filePaths = [];

    for (let i = 0; i < files.length; i++) {
      const path = files[i].webkitRelativePath || files[i].name;

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
      const res = await fetch(ARCHREC_UPLOAD_ENDPOINT, {
        method: "POST",
        body: formData,
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        console.error("ArchRec codebase load failed:", data);
        alert(data.error || "ArchRec codebase load failed");
        return;
      }

      console.log("ArchRec codebase loaded:", data);
      alert(`Loaded codebase into ArchRec workspace. Files saved: ${data.files_saved ?? "?"}`);
      setUploadedFiles(Date.now());
    } catch (err) {
      console.error("ArchRec upload failed:", err);
      alert(`ArchRec upload failed: ${err.message}`);
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
    <>
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
        {menus.map((menu, index) => (
          <div
            key={menu.label}
            style={{
              position: "relative",
              padding: "5px 15px",
              fontWeight: "bold",
              cursor: "pointer",
              color: "black",
              borderRight: index !== menus.length - 1 ? "2px solid #333" : "none",
              opacity: isBusy && menu.label === "File" ? 0.95 : 1,
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
                  minWidth: "220px",
                  color: "black",
                  zIndex: 1000,
                }}
                className="dropdown"
              >
                {menu.actions.map((action) => {
                  const disabled = isBusy && action.isPipeline;
                  return (
                    <div
                      key={action.name}
                      onClick={() => !disabled && handleClick(action)}
                      style={{
                        padding: "6px 10px",
                        cursor: disabled ? "not-allowed" : "pointer",
                        opacity: disabled ? 0.55 : 1,
                        userSelect: "none",
                      }}
                      onMouseEnter={(e) => {
                        if (!disabled) e.currentTarget.style.background = "#ddd";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "transparent";
                      }}
                    >
                      {disabled ? "Running Pipeline…" : action.name}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}

        {/* Single file upload */}
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

        {/* ArchRec workspace folder upload */}
        <input
          type="file"
          webkitdirectory="true"
          multiple
          ref={ArchRecFolderUpload}
          style={{ display: "none" }}
          onChange={handleArchRecUploadChange}
        />
      </div>

      {/* Pipeline overlay */}
      {(isPipelineRunning || pipelineMsg) && (
        <div
          style={{
            position: "fixed",
            top: "64px",
            right: "18px",
            background: "white",
            border: "1px solid #333",
            borderRadius: "10px",
            padding: "10px 12px",
            boxShadow: "2px 2px 7px rgba(0,0,0,0.2)",
            zIndex: 2000,
            minWidth: "310px",
            color: "black",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "14px",
                height: "14px",
                border: "2px solid #999",
                borderTop: "2px solid #111",
                borderRadius: "50%",
                animation: isPipelineRunning ? "spin 1s linear infinite" : "none",
              }}
            />
            <div style={{ fontWeight: "bold" }}>
              {isPipelineRunning ? "Pipeline running" : "Pipeline"}
            </div>
          </div>

          <div style={{ marginTop: "6px", fontSize: "13px" }}>{pipelineMsg}</div>

          {isPipelineRunning && (
            <div style={{ marginTop: "10px" }}>
              <div
                style={{
                  height: "6px",
                  background: "#ddd",
                  borderRadius: "999px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: "40%",
                    height: "100%",
                    background: "#333",
                    animation: "indet 1.2s ease-in-out infinite",
                  }}
                />
              </div>
              <div style={{ marginTop: "8px", fontSize: "12px", opacity: 0.8 }}>
                Please don’t close the tab while it’s running.
              </div>
            </div>
          )}

          {showPipelineDetails && pipelineResult && (
            <div style={{ marginTop: "10px" }}>
              <button
                onClick={() => setShowPipelineDetails((v) => !v)}
                style={{
                  padding: "6px 10px",
                  border: "1px solid #333",
                  background: "white",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                {showPipelineDetails ? "Hide details" : "Show details"}
              </button>

              {showPipelineDetails && (
                <pre
                  style={{
                    marginTop: "8px",
                    maxHeight: "220px",
                    overflow: "auto",
                    background: "#f6f6f6",
                    border: "1px solid #ddd",
                    padding: "8px",
                    borderRadius: "8px",
                    fontSize: "12px",
                    whiteSpace: "pre-wrap",
                  }}
                >
{JSON.stringify(pipelineResult, null, 2)}
                </pre>
              )}
            </div>
          )}

          <style>{`
            @keyframes spin { to { transform: rotate(360deg); } }
            @keyframes indet {
              0% { transform: translateX(-140%); }
              50% { transform: translateX(60%); }
              100% { transform: translateX(240%); }
            }
          `}</style>
        </div>
      )}
    </>
  );
}
