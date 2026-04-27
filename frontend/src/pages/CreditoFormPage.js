import { useNavigate, useParams } from "react-router-dom";
import { getClienteById } from "../services/clienteService";
import React, { useEffect, useState } from "react";

export default function CreditoFormWrapper() {
    const { cliente_id } = useParams();
    const navigate = useNavigate();
    const [monto, setMonto] = useState("");
    const [cliente, setCliente] = useState(null);
    const [plazo, setPlazo] = useState("");
    const [tasa, setTasa] = useState("");

    useEffect(() => {
        const fetchCliente = async () => {
            const data = await getClienteById(cliente_id);
            setCliente(data);
        };

        fetchCliente();
    }, [cliente_id]);

    return (
        <div className="card">
            <button onClick={() => navigate(`/clientes/${cliente_id}`)}>
                ← Volver
            </button>

            <h2>Nuevo Crédito</h2>
            <form>
                <input
                    type="number"
                    placeholder="Monto del crédito"
                    value={monto}
                    onChange={(e) => setMonto(e.target.value)}
                />

                <input
                    type="number"
                    placeholder="Plazo (meses)"
                    value={plazo}
                    onChange={(e) => setPlazo(e.target.value)}
                />

                <input
                    type="number"
                    placeholder="Tasa de interés (%)"
                    value={tasa}
                    onChange={(e) => setTasa(e.target.value)}
                />

                <button
                    onClick={async () => {
                        const data = {
                            credito: {
                                cliente_id: Number(cliente_id),
                                sucursal_id: 1,
                                monto: Number(monto),
                                tasa_interes: Number(tasa),
                                tipo_interes: "FIJO",
                                modalidad_pago: "MENSUAL",
                                plazo_numero: 12,
                                fecha_inicio: new Date().toISOString().split("T")[0],
                                total_con_interes: Number(monto) * 1.1,
                                saldo_actual: Number(monto)
                            },
                            cliente: cliente
                        };

                        try {
                            const res = await fetch("http://localhost:8000/creditos/procesar", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify(data)
                            });

                            const result = await res.json();

                            if (result.success) {
                                alert("Crédito creado correctamente");
                            } else {
                                alert("Error al crear crédito");
                            }

                        } catch (error) {
                            console.error(error);
                        }
                    }}
                >
                    Guardar Crédito
                </button>
            </form>

            <p>Cliente ID: {cliente_id}</p>
        </div>
    );
}