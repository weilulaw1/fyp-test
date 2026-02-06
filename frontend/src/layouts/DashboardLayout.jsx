import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function DashboardLayout({
  sidebarOpen,
  onToggleSidebar,
  children,
}) {
  return (
    <div style={{ minHeight: "100vh", background: "#f4f6fa" }}>
      <Sidebar isOpen={sidebarOpen} toggleSidebar={onToggleSidebar} />

      <Topbar
        sidebarOpen={sidebarOpen}
        onToggleSidebar={onToggleSidebar}
      />

      <main
        style={{
          marginLeft: sidebarOpen ? "250px" : "52px",
          paddingTop: "72px",
          padding: "24px",
          transition: "margin-left 0.3s ease",
        }}
      >
        {children}
      </main>
    </div>
  );
}
