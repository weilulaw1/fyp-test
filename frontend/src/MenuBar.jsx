import React from "react";

const menuItems = [
  {
    label: "File",
    actions: [
      { name: "New", endpoint: "http://127.0.0.1:8000/api/file/new/" },
      { name: "Open", endpoint: "http://127.0.0.1:8000/api/file/open/" },
      { name: "Save", endpoint: "http://127.0.0.1:8000/api/file/save/" },
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

export default function MenuBar() {
  const handleClick = (endpoint) => {
    fetch(endpoint)
      .then((res) => res.json())
      .then((data) => alert(data.message))
      .catch((err) => console.error(err));
  };

  return (
    <div style={{ display: "flex", gap: "20px", background: "#eee", padding: "10px" }}>
      {menuItems.map((menu) => (
        <div key={menu.label} style={{ position: "relative" }}>
          <div style={{ cursor: "pointer", fontWeight: "bold", color: "black" }}>{menu.label}</div>
          <div
            style={{
              position: "absolute",
              top: "30px",
              left: 0,
              background: "f9f9f9",
              border: "1px solid #333",
              borderRadius: "4px",
              display: "none",
              padding: "5px 15px",
              boxShadow: "1px 1px 3px rgba(0,0,0,0.2)",
              color:"black",
            }}
            className="dropdown"
          >
            {menu.actions.map((action) => (
              <div
                key={action.name}
                onClick={() => handleClick(action.endpoint)}
                style={{ padding: "5px 10px", cursor: "pointer" }}
                onMouseEnter={(e) => (e.target.style.background = "#ddd")}
                onMouseLeave={(e) => (e.target.style.background = "white")}
              >
                {action.name}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
