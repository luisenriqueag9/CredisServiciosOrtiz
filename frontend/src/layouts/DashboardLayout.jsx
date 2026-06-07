import React from "react";
import { Link, useLocation, Outlet } from "react-router-dom";

export default function DashboardLayout() {
  const location = useLocation();

  const isActive = (path) =>
    location.pathname === path || location.pathname.startsWith(path + "/");

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

        <nav style={{ display: "flex", flexDirection: "column", gap: "15px" }}>

          <Link
            to="/"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            🏠 Dashboard
          </Link>

          <Link
            to="/clientes"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/clientes") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            👤 Clientes
          </Link>

          <Link
            to="/creditos"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/creditos") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            💰 Créditos
          </Link>

          <Link
            to="/pagos"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/pagos") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            💵 Pagos
          </Link>

          <Link
            to="/gastos"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/gastos") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            💸 Gastos
          </Link>

          <Link
            to="/reportes"
            style={{
              color: "white",
              textDecoration: "none",
              background: isActive("/reportes") ? "#1f2937" : "transparent",
              padding: "8px",
              borderRadius: "6px"
            }}
          >
            📊 Reportes
          </Link>

        </nav>
      </div>

      {/* CONTENIDO */}
      <div style={{
        flex: 1,
        background: "#f5f7fb"
      }}>

        {/* NAVBAR SUPERIOR */}
        <div style={{
          background: "white",
          padding: "15px 30px",
          borderBottom: "1px solid #eee",
          display: "flex",
          justifyContent: "space-between"
        }}>
          <h3>CREDIS</h3>
          <div>
            <span>👤 Admin</span>
          </div>
        </div>

        {/* CONTENIDO REAL */}
        <div style={{ padding: "30px" }}>
          <Outlet />
        </div>

      </div>

    </div>
  );
}