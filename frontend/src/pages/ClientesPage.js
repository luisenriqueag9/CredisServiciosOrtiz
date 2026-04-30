import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import ClienteForm from "../components/ClienteForm";
import {
  getClienteById,
  updateCliente
} from "../services/clienteService";

/* =========================
   MENU PRINCIPAL
========================= */
function ClientesPage() {
  return (
    <div>
      <h1 style={{ color: "#0f172a" }}>Clientes</h1>

      <div className="card">
        <h3>¿Qué deseas hacer?</h3>

        <div style={{ display: "flex", gap: "20px" }}>
          <Link to="/clientes/nuevo">
            <button>➕ Crear Cliente</button>
          </Link>

          <Link to="/clientes/lista">
            <button>📋 Ver Clientes</button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ClientesPage;

/* =========================
   FORM WRAPPER
========================= */
export function ClienteFormWrapper() {
  const navigate = useNavigate();

  return (
    <div className="card">
      <button onClick={() => navigate("/clientes")}>
        ← Volver
      </button>

      <h2>Crear Cliente</h2>

      <ClienteForm onClienteCreado={() => navigate("/clientes/lista")} />
    </div>
  );
}

/* =========================
   EDIT WRAPPER
========================= */
export function ClienteEditWrapper() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);

  useEffect(() => {
    const fetchCliente = async () => {
      const data = await getClienteById(id);
      setCliente(data);
    };

    fetchCliente();
  }, [id]);

  const handleUpdate = async (data) => {
    try {
      await updateCliente(id, data);
      navigate("/clientes/lista");
    } catch (err) {
      console.error(err);
    }
  };

  if (!cliente || !cliente.nombre) return <p>Cargando...</p>;

  return (
    <div className="card">
      <button onClick={() => navigate("/clientes/lista")}>
        ← Volver
      </button>

      <h2>Editar Cliente</h2>

      <ClienteForm
        onClienteCreado={handleUpdate}
        clienteInicial={cliente}
      />
    </div>
  );
}