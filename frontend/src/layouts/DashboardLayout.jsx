import React from "react";

export default function DashboardLayout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>

      {/* SIDEBAR */}
      <div style={{
        width: "220px",
        background: "#111827",
        color: "white",
        padding: "20px"
      }}>
        <h2 style={{ marginBottom: "30px" }}>Credis</h2>

        <p>Dashboard</p>
        <p>Clientes</p>
        <p>Créditos</p>
        <p>Pagos</p>
        <p>Reportes</p>
      </div>

      {/* CONTENIDO */}
      <div style={{
        flex: 1,
        background: "#f5f7fb",
        padding: "30px"
      }}>
        {children}
      </div>

    </div>
  );
}