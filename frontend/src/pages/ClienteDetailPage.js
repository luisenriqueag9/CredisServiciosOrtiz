import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getClienteById } from "../services/clienteService";
import { obtenerCreditosPorCliente } from "../services/clienteService";

export default function ClienteDetailWrapper() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [creditos, setCreditos] = useState([]);
  const [tipoPeriodo, setTipoPeriodo] = useState("MENSUAL");
  const [tipoPlan, setTipoPlan] = useState("CUOTA_FIJA");


  useEffect(() => {
    const fetchData = async () => {
      const clienteData = await getClienteById(id);
      setCliente(clienteData);

      const creditosData = await obtenerCreditosPorCliente(id);
      setCreditos(creditosData);
    };

    fetchData();
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

      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: "10px"
      }}>
        <p style={{ margin: 0 }}>Listado de créditos del cliente</p>

        <button
          onClick={() => navigate(`/creditos/nuevo/${cliente.id}`)}
        >
          + Nuevo Crédito
        </button>
      </div>

      <div className="card" style={{ marginTop: "15px" }}>
        <table style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Monto</th>
              <th>Cuotas</th>
              <th>Saldo</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {creditos.map((c) => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>L {c.monto}</td>
                <td>{c.cuotas}</td>
                <td>L {c.saldo_actual}</td>
                <td>{c.estado}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}