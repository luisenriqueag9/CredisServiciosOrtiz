import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getClienteById, obtenerCreditosPorCliente }
  from "../services/clienteService";

export default function ClienteDetailWrapper() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [cliente, setCliente] = useState(null);
  const [creditos, setCreditos] = useState([]);
  const [resumen, setResumen] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const clienteData = await getClienteById(id);
      setCliente(clienteData);

      const creditosData = await obtenerCreditosPorCliente(id);
      setCreditos(creditosData);

      if (creditosData.length > 0) {
        const res = await fetch(
          `http://localhost:8000/creditos/${creditosData[0].id}/resumen`
        );
        const data = await res.json();

        if (data.success) {
          setResumen(data.data);
        }
      }
    };

    fetchData();
  }, [id]);

  if (!cliente) return <p>Cargando...</p>;

  return (
    <div className="card">
      <button onClick={() => navigate("/clientes/lista")}>
        ← Volver
      </button>

      <h2>Detalle del Cliente</h2>

      {/* DATOS CLIENTE */}
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

      {/* RESUMEN */}
      {resumen && (
        <div className="card" style={{ marginTop: "20px" }}>
          <h3>Resumen del crédito</h3>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "16px",
              marginTop: "15px",
            }}
          >
            <div style={{ background: "#2563eb", color: "white", padding: "18px", borderRadius: "16px" }}>
              <p>Saldo actual</p>
              <h2>L {resumen.credito.saldo_actual}</h2>
            </div>

            <div style={{ background: "#10b981", color: "white", padding: "18px", borderRadius: "16px" }}>
              <p>Total pagado</p>
              <h2>L {resumen.pagos.total}</h2>
            </div>

            <div style={{ background: "#f59e0b", color: "white", padding: "18px", borderRadius: "16px" }}>
              <p>Pendiente</p>
              <h2>L {resumen.credito.saldo_actual}</h2>
            </div>

            <div style={{ background: "#6366f1", color: "white", padding: "18px", borderRadius: "16px" }}>
              <p>% pagado</p>
              <h2>
                {(() => {
                  const total =
                    resumen.pagos.total + resumen.credito.saldo_actual;
                  return total > 0
                    ? ((resumen.pagos.total / total) * 100).toFixed(1)
                    : 0;
                })()}
                %
              </h2>
            </div>
          </div>
        </div>
      )}

      {/* DOCUMENTOS */}
      {resumen?.documentos && (
        <>
          <h3 style={{ marginTop: "30px" }}>Documentos</h3>

          {/* BOTÓN WHATSAPP */}
          <div style={{ marginBottom: "15px" }}>
            <button
              onClick={() => {
                const telefono = cliente.telefono.replace(/[^0-9]/g, "");

                const mensaje = `Hola ${cliente.nombre},

Aquí están tus documentos:

📄 Pagaré: ${resumen.documentos.pagare_url}
📄 Contrato: ${resumen.documentos.contrato_url}
📄 Plan de pagos: ${resumen.documentos.plan_url}

Saludos.`;

                const url = `https://wa.me/504${telefono}?text=${encodeURIComponent(
                  mensaje
                )}`;

                window.open(url, "_blank");
              }}
            >
              📲 Compartir todo por WhatsApp
            </button>
          </div>

          {/* CARDS DOCUMENTOS */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
            }}
          >
            <div className="card" style={{ textAlign: "center" }}>
              <p>Plan de pagos</p>
              <button onClick={() => window.open(resumen.documentos.plan_url, "_blank")}>
                Ver
              </button>
            </div>

            <div className="card" style={{ textAlign: "center" }}>
              <p>Pagaré</p>
              <button onClick={() => window.open(resumen.documentos.pagare_url, "_blank")}>
                Ver
              </button>
            </div>

            <div className="card" style={{ textAlign: "center" }}>
              <p>Contrato</p>
              <button onClick={() => window.open(resumen.documentos.contrato_url, "_blank")}>
                Ver
              </button>
            </div>
          </div>
        </>
      )}

      {/* CRÉDITOS */}
      <h3 style={{ marginTop: "30px" }}>Créditos</h3>

      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <p>Listado de créditos del cliente</p>

        {creditos.length === 0 && (
          <button onClick={() => navigate(`/creditos/nuevo/${cliente.id}`)}>
            + Nuevo Crédito
          </button>
        )}
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
              <th>Acciones</th>
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

                <td>
                  <button onClick={() => navigate(`/creditos/${c.id}`)}>
                    Ver detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}