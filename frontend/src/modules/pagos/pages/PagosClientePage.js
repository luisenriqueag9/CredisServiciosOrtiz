import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";


export default function PagosClientePage() {
    const { id } = useParams();
    const [pagos, setPagos] = useState([]);
    const navigate = useNavigate();
    const [cliente, setCliente] = useState(null);
    const totalPagado = pagos.reduce((acc, p) => acc + Number(p.monto_pagado), 0);
    const totalCapital = pagos.reduce((acc, p) => acc + Number(p.capital_pagado), 0);
    const totalInteres = pagos.reduce((acc, p) => acc + Number(p.interes_pagado), 0);

    const fetchCliente = async () => {
        try {
            const res = await fetch(`http://localhost:8000/clientes/${id}`);
            const data = await res.json();

            setCliente(data);

        } catch (error) {
            console.error("Error cargando cliente", error);
        }
    };

    const fetchPagos = async () => {
        try {
            const res = await fetch(`http://localhost:8000/pagos/?cliente_id=${id}`);
            const data = await res.json();

            if (data.success) {
                setPagos(data.data);
            }

        } catch (error) {
            console.error("Error cargando pagos del cliente", error);
        }
    };

    useEffect(() => {
        fetchPagos();
        fetchCliente();
    }, [id]);
    console.log("cliente:", cliente);

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
                {cliente ? `Historial de pagos de ${cliente.nombre}` : "Historial de pagos"}
            </h2>

            <div style={{
                display: "flex",
                gap: "20px",
                marginTop: "20px",
                marginBottom: "20px",
                flexWrap: "wrap"
            }}>

                <div style={{
                    background: "#16a34a",
                    color: "white",
                    padding: "15px",
                    borderRadius: "10px",
                    minWidth: "180px"
                }}>
                    💰 Total Pagado
                    <h3>L {totalPagado.toFixed(2)}</h3>
                </div>

                <div style={{
                    background: "#2563eb",
                    color: "white",
                    padding: "15px",
                    borderRadius: "10px",
                    minWidth: "180px"
                }}>
                    📉 Capital
                    <h3>L {totalCapital.toFixed(2)}</h3>
                </div>

                <div style={{
                    background: "#f59e0b",
                    color: "white",
                    padding: "15px",
                    borderRadius: "10px",
                    minWidth: "180px"
                }}>
                    📈 Intereses
                    <h3>L {totalInteres.toFixed(2)}</h3>
                </div>

            </div>

            <table style={{ width: "100%", marginTop: "20px" }}>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Monto</th>
                        <th>Capital</th>
                        <th>Interés</th>
                    </tr>
                </thead>

                <tbody>
                    {pagos.length > 0 ? (
                        pagos.map((p) => (
                            <tr key={p.id}>
                                <td>{new Date(p.fecha_pago).toLocaleDateString()}</td>
                                <td>L {p.monto_pagado}</td>
                                <td>L {p.capital_pagado}</td>
                                <td>L {p.interes_pagado}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4">No hay pagos</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}