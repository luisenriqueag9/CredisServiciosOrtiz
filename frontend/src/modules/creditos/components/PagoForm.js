import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function PagoForm() {
    const { credito_id } = useParams();
    const navigate = useNavigate();

    const [monto, setMonto] = useState("");
    const [simulacion, setSimulacion] = useState(null);
    const [error, setError] = useState("");

    const calcularPago = async () => {
        setError("");
        setSimulacion(null);

        const res = await fetch("http://localhost:8000/pagos/simular", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                credito_id: Number(credito_id),
                monto: Number(monto),
            }),
        });

        const data = await res.json();

        if (data.success) {
            setSimulacion(data.data);
        } else {
            setError(data.message);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const res = await fetch("http://localhost:8000/pagos/rapido", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                credito_id: Number(credito_id),
                monto: Number(monto),
            }),
        });

        const data = await res.json();

        if (data.success) {
            navigate(`/creditos/${credito_id}`, {
                state: { nuevoPago: data.data }
            });
        } else {
            alert("❌ Error al pagar");
        }
    };

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

            <h2>Registrar Pago</h2>

            <div style={{ marginTop: "15px" }}>
                <label>Monto</label>
                <input
                    type="number"
                    value={monto}
                    onChange={(e) => setMonto(e.target.value)}
                />
            </div>

            <button
                onClick={calcularPago}
                style={{
                    marginTop: "15px",
                    background: "#2563eb",
                    color: "white",
                    padding: "10px 16px",
                    border: "none",
                    borderRadius: "8px"
                }}
            >
                🔍 Calcular pago
            </button>

            {error && (
                <p style={{ color: "red", marginTop: "10px" }}>
                    ⚠️ {error}
                </p>
            )}

            {simulacion && (
                <div style={{
                    marginTop: "20px",
                    padding: "15px",
                    background: "#f3f4f6",
                    borderRadius: "10px"
                }}>
                    <p>Interés: L {simulacion.interes}</p>
                    <p>Capital: L {simulacion.capital}</p>
                    <p>Saldo restante: L {simulacion.saldo_restante ?? 0}</p>
                </div>
            )}

            <button
                onClick={handleSubmit}
                disabled={!simulacion}
                style={{
                    marginTop: "20px",
                    background: simulacion ? "#16a34a" : "#9ca3af",
                    color: "white",
                    padding: "10px 16px",
                    border: "none",
                    borderRadius: "8px",
                    cursor: simulacion ? "pointer" : "not-allowed"
                }}
            >
                💰 Confirmar pago
            </button>
        </div>
    );
}