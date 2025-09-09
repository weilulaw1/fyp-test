import React, { useEffect, useState , useRef} from "react";

const menuItems = [
  {
    label: "File",
    actions: [
      { name: "New", endpoint: "http://127.0.0.1:8000/api/file/new/" },
      { name: "Open", endpoint: "http://127.0.0.1:8000/api/file/open/", isFileUpload: true },
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

export default function MenuBar({onToggleSidebar, sidebarOpen }) {
  const [openMenu,setOpenMenu]= useState(null);
  const FileUploadAction = useRef(null);
  const handleClick = (action) => {
    if(action.isFileUpload) {
      FileUploadAction.current.click()
    } else{
    fetch(action.endpoint)
      .then((res) => res.json())
      //.then((data) => alert(data.message))
      .catch((err) => console.error(err));
    }
    setOpenMenu(null);    
    // Call the toggle function if the endpoint is the toggle sidebar action
    if (action.endpoint.includes("toggle_sidebar")) {
      onToggleSidebar();
    }
  };

  // Handle file selection
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("myfile", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/file/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      alert(data.message);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };

  //close menu when click outside
   useEffect(() => {
    const handleOutsideClick = () => setOpenMenu(null);
    window.addEventListener("click", handleOutsideClick);
    return () => window.removeEventListener("click", handleOutsideClick);
  }, []);

  return (
    <div style={
      { 
      display: "flex", 
      background: "#ffffffff", 
      padding: "10px",
      alignItems: "center",
      position: "fixed",      
      justifyContent: "flex-start",
      top: 0,
      left: sidebarOpen ? "290px" : "40px",       // dynamically shift
      width: sidebarOpen ? "calc(100% - 250px)" : "calc(100% - 20px)", 
      borderBottom: "2px solid #333",
      transition: "left 0.3s ease, width 0.3s ease", // smooth sliding
      zIndex: 1000,
      }}
      onClick={(e)=> e.stopPropagation()} //prevent menu from closing when clicking inside
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
            borderRight: index !== menuItems.length - 1 ? "2px solid #333" : "none", // add border between items
          }}
          onMouseEnter={() => setOpenMenu(menu.label)}
          onMouseLeave={() => setOpenMenu(null)}        
        >
          {menu.label}
          {/* Only show dropdown if this menu is active */}
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
              minWidth: "120px",
              color: "black",
              zIndex: 1000
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
      <input
        type="file"
        ref={FileUploadAction}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
    </div>
  );
}
