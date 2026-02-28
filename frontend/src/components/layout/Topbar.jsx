import React, {  useRef, useState } from "react";

const PIPELINE_ENDPOINT = "http://127.0.0.1:8000/api/archrec/run-summarize/";
const UPLOAD_MEDIA_ENDPOINT = "http://127.0.0.1:8000/api/file/upload/";
const ARCHREC_UPLOAD_ENDPOINT = "http://127.0.0.1:8000/api/archrec/upload-project/";

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export default function MenuBar({  sidebarOpen, setUploadedFiles }) {
  const SingleFileUpload = useRef(null);
  const FileUploadAction = useRef(null);
  const ArchRecFolderUpload = useRef(null);

  // Pipeline UI state
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [pipelineMsg, setPipelineMsg] = useState("");
  const [pipelineResult, setPipelineResult] = useState(null);
  const [showPipelineDetails, setShowPipelineDetails] = useState(false);

  const isBusy = isPipelineRunning;

  // --- 1) Upload to MEDIA root
  const handleNormalUploadChange = async (e) => {
    const files = e.target.files;
    if (!files || !files.length) return;

    const formData = new FormData();
    const filePaths = [];

    for (let i = 0; i < files.length; i++) {
      const path = files[i].webkitRelativePath || files[i].name;

      if (
        path.includes("node_modules") ||
        path.includes("__pycache__") ||
        path.includes(".venv")
      ) {
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
      setUploadedFiles(Date.now()); // ✅ refresh FolderView
    } catch (err) {
      console.error("Upload failed:", err);
      alert(`Upload failed: ${err.message}`);
    } finally {
      e.target.value = null;
    }
  };

  // --- 2) Upload folder to ArchRec workspace
const handleArchRecUploadChange = async (e) => {
  const input = e.target;
  const fileList = input.files;
  if (!fileList || !fileList.length) return;

  // --- CONFIG ---
  const BATCH_SIZE = 150; // ✅ tune: 100–250 is usually safe on Windows
  const ENDPOINT = ARCHREC_UPLOAD_ENDPOINT;

  // ✅ folder names to exclude anywhere in the path
  const denyFolders = new Set([
    "node_modules",
    "__pycache__",
    ".venv",
    ".git",
    "dist",
    "build",
    "target",
    "out",
    ".idea",
    ".vscode",
    "coverage",
    "__MACOSX",
  ]);

  // ✅ file extensions to exclude (optional; keep if you want)
  const denyExts = new Set([
    ".log",
    ".tmp",
    ".DS_Store",
  ]);

  // Helper: returns true if file should be skipped
  const shouldSkip = (path) => {
    const norm = path.replace(/\\/g, "/");
    const parts = norm.split("/").filter(Boolean);

    // folder-based deny
    for (const p of parts) {
      if (denyFolders.has(p)) return true;
    }

    // extension-based deny
    const lower = norm.toLowerCase();
    for (const ext of denyExts) {
      if (lower.endsWith(ext.toLowerCase())) return true;
    }

    return false;
  };

  // Turn FileList into filtered array of { file, path }
  const all = [];
  for (let i = 0; i < fileList.length; i++) {
    const f = fileList[i];
    const path = f.webkitRelativePath || f.name;

    if (shouldSkip(path)) continue;

    all.push({ file: f, path });
  }

  if (all.length === 0) {
    alert("No files to upload after filtering (everything was excluded).");
    input.value = null;
    return;
  }

  // Optional: quick visibility
  console.log(`ArchRec upload: ${all.length} files (filtered from ${fileList.length})`);

  // Upload one batch
  const uploadBatch = async (batch, batchIndex, totalBatches) => {
    const formData = new FormData();
    const filePaths = [];

    for (const item of batch) {
      filePaths.push(item.path);
      formData.append("files", item.file);
    }

    formData.append("file_paths", JSON.stringify(filePaths));

    const res = await fetch(ENDPOINT, {
      method: "POST",
      body: formData,
    });

    // Backend returns JSON
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = data?.error || `Batch ${batchIndex + 1}/${totalBatches} upload failed`;
      throw new Error(msg);
    }

    return data;
  };

  // Run batches sequentially (safer than parallel)
  try {
    const totalBatches = Math.ceil(all.length / BATCH_SIZE);

    // Optional: simple progress feedback
    // (replace with your overlay/toast if you have one)
    // alert(`Uploading ${all.length} files in ${totalBatches} batches...`);

    let lastResponse = null;

    for (let start = 0, b = 0; start < all.length; start += BATCH_SIZE, b++) {
      const batch = all.slice(start, start + BATCH_SIZE);
      console.log(`Uploading batch ${b + 1}/${totalBatches} (${batch.length} files)...`);

      lastResponse = await uploadBatch(batch, b, totalBatches);
    }

    console.log("ArchRec upload done. Last batch response:", lastResponse);
    alert(`Loaded codebase into ArchRec workspace.\nBatches: ${Math.ceil(all.length / BATCH_SIZE)}\nFiles: ${all.length}`);

    // ✅ refresh your UI once at the end
    setUploadedFiles(Date.now());
  } catch (err) {
    console.error("ArchRec upload failed:", err);
    alert(`ArchRec upload failed: ${err.message}`);
  } finally {
    // ✅ allow re-upload of same folder (important)
    input.value = null;
  }
};
  // --- 3) Run Pipeline button action
  const runPipeline = async () => {
    if (isBusy) return;

    setIsPipelineRunning(true);
    setPipelineMsg("Running pipeline… (Summarize → UML → publish)");
    setPipelineResult(null);
    setShowPipelineDetails(false);

    try {
      const res = await fetch(PIPELINE_ENDPOINT, { method: "POST" });
      const text = await res.text();
      const data = safeJsonParse(text) ?? { raw: text };

      if (!res.ok) {
        const errMsg = data?.error || data?.detail || "Pipeline failed";
        throw new Error(errMsg);
      }

      setPipelineMsg("Done! Outputs published to folder view.");
      setPipelineResult(data);
      setUploadedFiles(Date.now()); // ✅ refresh FolderView
      setShowPipelineDetails(true);
    } catch (err) {
      console.error(err);
      setPipelineMsg(`Error: ${err.message}`);
      setPipelineResult({ error: err.message });
      setShowPipelineDetails(true);
    } finally {
      setTimeout(() => setIsPipelineRunning(false), 600);
    }
  };

  const btnStyle = (disabled) => ({
    padding: "6px 10px",
    borderRadius: "8px",
    border: "1px solid #333",
    background: disabled ? "#eee" : "white",
    cursor: disabled ? "not-allowed" : "pointer",
    fontWeight: "bold",
    color: "black",
  });

  return (
    <>
      {/* ===================== TOP BAR ===================== */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          background: "#fff",
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
       
        {/* ✅ 4 separate actions */}
        <button
          onClick={() => SingleFileUpload.current?.click()}
          style={btnStyle(false)}
        >
          Upload File
        </button>

        <button
          onClick={() => FileUploadAction.current?.click()}
          style={btnStyle(false)}
        >
          Upload Folder
        </button>

        <button
          onClick={() => ArchRecFolderUpload.current?.click()}
          style={btnStyle(false)}
        >
          Load Codebase (Arch Rec)
        </button>

        <button
          onClick={runPipeline}
          style={btnStyle(isBusy)}
          disabled={isBusy}
          title={isBusy ? "Pipeline is running" : "Run summarize → UML pipeline"}
        >
          {isBusy ? "Running Pipeline…" : "Run Pipeline"}
        </button>

        {/* Hidden file inputs */}
        <input
          type="file"
          ref={SingleFileUpload}
          style={{ display: "none" }}
          onChange={handleNormalUploadChange}
        />

        <input
          type="file"
          webkitdirectory="true"
          multiple
          ref={FileUploadAction}
          style={{ display: "none" }}
          onChange={handleNormalUploadChange}
        />

        <input
          type="file"
          webkitdirectory="true"
          multiple
          ref={ArchRecFolderUpload}
          style={{ display: "none" }}
          onChange={handleArchRecUploadChange}
        />
      </div>

      {/* ===================== PIPELINE OVERLAY ===================== */}
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

          {pipelineResult && (
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