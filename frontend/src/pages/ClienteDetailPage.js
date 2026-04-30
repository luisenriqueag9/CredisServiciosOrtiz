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
  const [resumen, setResumen] = useState(null);


  useEffect(() => {
    const fetchData = async () => {
      const clienteData = await getClienteById(id);
      setCliente(clienteData);

      const creditosData = await obtenerCreditosPorCliente(id);
      setCreditos(creditosData);

      if (creditosData.length > 0) {
        const res = await fetch(`http://localhost:8000/creditos/${creditosData[0].id}/resumen`);
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

      {resumen && (
        <div className="card" style={{ marginTop: "20px" }}>
          <h3>Resumen del crédito</h3>


          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "16px",
            marginTop: "15px"
          }}>

            <div style={{
              background: "#2563eb",
              color: "white",
              padding: "18px",
              borderRadius: "16px"
            }}>
              <p style={{ opacity: 0.8 }}>Saldo actual</p>
              <h2>L {resumen.credito.saldo_actual}</h2>
            </div>

            <div style={{
              background: "#10b981",
              color: "white",
              padding: "18px",
              borderRadius: "16px"
            }}>
              <p style={{ opacity: 0.8 }}>Total pagado</p>
              <h2>L {resumen.pagos.total}</h2>
            </div>

            <div style={{
              background: "#f59e0b",
              color: "white",
              padding: "18px",
              borderRadius: "16px"
            }}>
              <p style={{ opacity: 0.8 }}>Pendiente</p>
              <h2>L {resumen.credito.saldo_actual}</h2>
            </div>

            <div style={{
              background: "#6366f1",
              color: "white",
              padding: "18px",
              borderRadius: "16px"
            }}>
              <p style={{ opacity: 0.8 }}>% pagado</p>
              <h2>
                {(() => {
                  const total = resumen.pagos.total + resumen.credito.saldo_actual;
                  return total > 0
                    ? ((resumen.pagos.total / total) * 100).toFixed(1)
                    : 0;
                })()}%
              </h2>
            </div>

          </div>
        </div>

      )}


      <h3 style={{ marginTop: "30px" }}>Documentos</h3>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "16px",
        marginTop: "15px"
      }}>
        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: "30px" }}>📄</div>
          <p>Plan de pagos</p>

          <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
            <button onClick={() => window.open(resumen?.documentos?.plan_url, "_blank")}>
              Ver
            </button>

            
          </div>
        </div>

        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: "30px" }}>📄</div>
          <p>Pagaré</p>

          <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
            <button onClick={() => window.open(resumen?.documentos?.pagare_url, "_blank")}>
              Ver
            </button>

            
          </div>
        </div>

        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: "30px" }}>📄</div>
          <p>Contrato</p>

          <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
            <button onClick={() => window.open(resumen?.documentos?.contrato_url, "_blank")}>
              Ver
            </button>

          
          </div>
        </div>
      </div>

      <h3 style={{ marginTop: "30px" }}>Créditos</h3>

      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: "10px"
      }}>
        <p style={{ margin: 0 }}>Listado de créditos del cliente</p>

        {creditos.length === 0 && (
          <button
            onClick={() => navigate(`/creditos/nuevo/${cliente.id}`)}
          >
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