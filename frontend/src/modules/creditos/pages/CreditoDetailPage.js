import { useParams, useNavigate } from "react-router-dom";
import { useCredito } from "../hooks/useCredito";
import PagosList from "../components/PagosList";
import ResumenCredito from "../components/ResumenCredito";

export default function CreditoDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { resumen, loading } = useCredito(id);
    if (loading || !resumen) return <p>Cargando crédito...</p>;
    console.log(resumen);

    const verRecibo = async (pagoId) => {
        try {
            const res = await fetch(`http://localhost:8000/recibos/${pagoId}`);
            const data = await res.json();

            if (data.success) {
                window.open(data.data.url, "_blank");
            }
        } catch (error) {
            console.error("Error al obtener recibo", error);
        }
    };



    if (loading) return <p>Cargando crédito...</p>;

    const total = (resumen?.pagos?.total || 0) + (resumen?.credito?.saldo_actual || 0);

    const porcentaje = total > 0
        ? ((resumen.pagos.total / total) * 100).toFixed(1)
        : 0;

    return (
        <div className="card">

            <button
                onClick={() => navigate(-1)}
                style={{
                    marginBottom: "10px",
                    background: "transparent",
                    border: "none",
                    color: "#2563eb",
                    cursor: "pointer",
                    fontWeight: "bold"
                }}
            >
                ← Volver
            </button>

            <h2>
                {resumen.cliente?.nombre} - Crédito #{resumen.credito.id}
            </h2>
            <ResumenCredito resumen={resumen} />

            {/* DOCUMENTOS */}
            {resumen.documentos && (
                <>
                    <h3 style={{ marginTop: "30px" }}>Documentos</h3>

                    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                        <button onClick={() => window.open(resumen.documentos.pagare_url)}>📄 Pagaré</button>
                        <button onClick={() => window.open(resumen.documentos.contrato_url)}>📄 Contrato</button>
                        <button onClick={() => window.open(resumen.documentos.plan_url)}>📄 Plan</button>
                    </div>
                </>
            )}


            {/* PAGOS */}
            <PagosList
                pagos={resumen.pagos_list || []}
                onVerRecibo={verRecibo}
            />

            {/* BOTÓN */}
            <div style={{ marginTop: "20px" }}>
                <button
                    onClick={() => navigate(`/pagos/nuevo/${id}`)}
                    style={{
                        background: "#16a34a",
                        color: "white",
                        padding: "12px 18px",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer"
                    }}
                >
                    💰 Registrar pago
                </button>
            </div>

        </div>
    );
}


// 🔹 componente interno simple (no modular todavía)
function Card({ title, value, color }) {
    return (
        <div style={{
            background: color,
            color: "white",
            padding: "18px",
            borderRadius: "16px"
        }}>
            <p>{title}</p>
            <h2>{typeof value === "string" ? value : `L ${value}`}</h2>
        </div>


    );
}