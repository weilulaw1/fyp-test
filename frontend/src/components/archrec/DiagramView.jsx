import React, { useEffect, useRef, useState } from "react";

export default function DiagramView({ children }) {
  const viewportRef = useRef(null);

  const [dragging, setDragging] = useState(false);
  const [spaceDown, setSpaceDown] = useState(false);

  const draggingRef = useRef(false);
  const startRef = useRef({ x: 0, y: 0, left: 0, top: 0 });

  // Auto-center when content changes
  useEffect(() => {
    const el = viewportRef.current;
    if (!el) return;

    const center = () => {
      el.scrollLeft = Math.max(0, (el.scrollWidth - el.clientWidth) / 2);
      el.scrollTop = Math.max(0, (el.scrollHeight - el.clientHeight) / 2);
    };

    requestAnimationFrame(center);
    setTimeout(center, 60);
  }, [children]);

  // Track Space key globally
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.code === "Space") 
        {
    const tag = document.activeElement?.tagName;
    const isTyping =
      tag === "INPUT" ||
      tag === "TEXTAREA" ||
      document.activeElement?.isContentEditable;

    if (!isTyping) {
      e.preventDefault();  // only block page scroll
      setSpaceDown(true);
    }
  };
    };
    const onKeyUp = (e) => {
      if (e.code === "Space") setSpaceDown(false);
    };

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, []);

  const onMouseDown = (e) => {
    // Only pan when Space is held
    if (!spaceDown) return;
    if (e.button !== 0) return;

    const el = viewportRef.current;
    if (!el) return;

    e.preventDefault(); // stop page scroll / weird selection only while panning

    draggingRef.current = true;
    setDragging(true);

    startRef.current = {
      x: e.clientX,
      y: e.clientY,
      left: el.scrollLeft,
      top: el.scrollTop,
    };
  };

  const onMouseMove = (e) => {
    if (!draggingRef.current) return;

    const el = viewportRef.current;
    if (!el) return;

    e.preventDefault();

    const dx = e.clientX - startRef.current.x;
    const dy = e.clientY - startRef.current.y;

    el.scrollLeft = startRef.current.left - dx;
    el.scrollTop = startRef.current.top - dy;
  };

  const endDrag = () => {
    draggingRef.current = false;
    setDragging(false);
  };

  return (
    <div style={{ padding: "20px 0" }}>
      <h2 style={{ textAlign: "center", marginBottom: 16 }}>
        PlantUML Diagram
      </h2>

      <div
        ref={viewportRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={endDrag}
        onMouseLeave={endDrag}
        className="diagramPanel"
        style={{
          width: "100%",
          height: "calc(100vh - 72px - 120px)",
          overflowX: "auto",
          overflowY: "auto",
          cursor: spaceDown ? (dragging ? "grabbing" : "grab") : "auto",
          userSelect: "text", 
          padding: "0 12px",
        }}
        title={spaceDown ? "Drag to pan" : "Hold Space + drag to pan"}
      >
        <div
          style={{
            display: "inline-block",
            width: "max-content",
            minWidth: "100%",
            padding: "12px 0",
          }}
        >
          {children}
        </div>
      </div>

      <div style={{ textAlign: "center", marginTop: 8, fontSize: 12, opacity: 0.7 }}>
        Tip: Hold <b>Space</b> and drag to pan
      </div>
    </div>
  );
}