import React, { useState, useEffect } from "react";
import { deleteCliente } from "../services/clienteService";
import { useNavigate } from "react-router-dom";

function ClienteList({ clientes }) {
  const [busqueda, setBusqueda] = useState("");
  const [lista, setLista] = useState([]);
  const navigate = useNavigate();

  const azulCorporativo = "#0ea5e9";

  useEffect(() => {
    setLista(clientes);
  }, [clientes]);

  const clientesFiltrados = lista.filter((cliente) => {
    const texto = busqueda.toLowerCase();
    return (
      cliente.nombre.toLowerCase().includes(texto) ||
      cliente.identidad.toLowerCase().includes(texto)
    );
  });

  const handleDelete = async (id) => {
    const confirmar = window.confirm("¿Está seguro de eliminar este cliente?");
    if (!confirmar) return;
    const res = await deleteCliente(id);
    if (res) {
      setLista((prev) => prev.filter((c) => c.id !== id));
    }
  };

  // =========================
  // ESTILOS TIPO BANCO
  // =========================
  const buscadorStyle = {
    width: "100%",
    padding: "12px 20px",
    marginBottom: "25px",
    borderRadius: "12px",
    border: "1px solid #e2e8f0",
    fontSize: "15px",
    outline: "none",
    backgroundColor: "#f8fafc",
    boxSizing: "border-box",
    transition: "all 0.3s ease"
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    fontFamily: "'Inter', sans-serif",
    backgroundColor: "white",
  };

  const thStyle = {
    textAlign: "left",
    padding: "16px",
    fontSize: "13px",
    fontWeight: "600",
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    borderBottom: "2px solid #f1f5f9"
  };

  const tdStyle = {
    padding: "16px",
    fontSize: "15px",
    color: "#1e293b",
    borderBottom: "1px solid #f1f5f9"
  };

  const actionButtonStyle = {
    padding: "8px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    marginRight: "8px",
    backgroundColor: "#f1f5f9",
    transition: "background 0.2s"
  };

  return (
    <div style={{ padding: "10px" }}>
      {/* BUSCADOR */}
      <div style={{ position: "relative" }}>
        <input
          type="text"
          placeholder="🔍 Buscar por nombre o número de identidad..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          style={buscadorStyle}
          onFocus={(e) => e.target.style.borderColor = azulCorporativo}
          onBlur={(e) => e.target.style.borderColor = "#e2e8f0"}
        />
      </div>

      {/* TABLA PRO */}
      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={{ ...thStyle, width: "80px" }}>ID</th>
              <th style={thStyle}>Nombre del Cliente</th>
              <th style={thStyle}>Identidad</th>
              <th style={thStyle}>Teléfono</th>
              <th style={{ ...thStyle, textAlign: "right" }}>Acciones</th>
            </tr>
          </thead>

          <tbody>
            {clientesFiltrados.map((cliente) => (
              <tr
                key={cliente.id}
                onClick={() => navigate(`/clientes/${cliente.id}`)}
                style={{ 
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0f9ff"}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
              >
                <td style={{ ...tdStyle, color: "#94a3b8", fontWeight: "600" }}>#{cliente.id}</td>
                <td style={{ ...tdStyle, fontWeight: "500" }}>{cliente.nombre}</td>
                <td style={{ ...tdStyle, fontFamily: "monospace", color: "#475569" }}>{cliente.identidad}</td>
                <td style={tdStyle}>{cliente.telefono}</td>

                <td style={{ ...tdStyle, textAlign: "right" }}>
                  <button
                    title="Editar"
                    style={actionButtonStyle}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/clientes/editar/${cliente.id}`);
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#e0f2fe"}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#f1f5f9"}
                  >
                    <span style={{ color: azulCorporativo }}>✏️</span>
                  </button>

                  <button
                    title="Eliminar"
                    style={actionButtonStyle}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(cliente.id);
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#fee2e2"}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#f1f5f9"}
                  >
                    <span style={{ color: "#ef4444" }}>🗑</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {clientesFiltrados.length === 0 && (
        <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
          No se encontraron clientes con ese criterio.
        </div>
      )}
    </div>
  );
}

export default ClienteList;