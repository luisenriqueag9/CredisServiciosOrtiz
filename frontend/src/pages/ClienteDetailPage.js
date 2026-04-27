import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getClienteById } from "../services/clienteService";

export default function ClienteDetailWrapper() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [creditos, setCreditos] = useState([]);

  useEffect(() => {
    const fetchCliente = async () => {
      const data = await getClienteById(id);
      setCliente(data);
    };

    fetchCliente();
  }, [id]);

  useEffect(() => {
    setCreditos([]);
  }, [id]);

  if (!cliente) return <p>Cargando...</p>;

  return (
    <div className="card detail-card">
      <button onClick={() => navigate("/clientes/lista")}>
        ← Volver
      </button>

      <h2>Detalle del Cliente</h2>

      <div className="detail-grid">
        <div>
          <label>Nombre</label>
          <p>{cliente.nombre}</p>
        </div>

        <div>
          <label>Identidad</label>
          <p>{cliente.identidad}</p>
        </div>

        <div>
          <label>Teléfono</label>
          <p>{cliente.telefono}</p>
        </div>

        <div>
          <label>Dirección</label>
          <p>{cliente.direccion}</p>
        </div>
      </div>

      <div style={{ marginTop: "20px" }}>
        <button onClick={() => navigate(`/clientes/editar/${cliente.id}`)}>
          ✏️ Editar
        </button>
      </div>

      <h3 style={{ marginTop: "30px" }}>Créditos</h3>

      <div className="card" style={{ marginTop: "10px" }}>
        <ul>
          {creditos.map((c) => (
            <li key={c.id}>
              Crédito #{c.id} - L {c.monto}
            </li>
          ))}
        </ul>

        <button
          onClick={() => navigate(`/creditos/nuevo/${cliente.id}`)}
        >
          + Nuevo Crédito
        </button>
      </div>
    </div>
  );
}