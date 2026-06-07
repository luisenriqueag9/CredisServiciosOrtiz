import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function PagosPage() {
    const [pagos, setPagos] = useState([]);
    const [filtroActivo, setFiltroActivo] = useState("todos");
    const navigate = useNavigate();

    const handleFiltro = (tipo) => {
        setFiltroActivo(tipo);
    };

    const fetchPagos = async (desde = null) => {
        try {
            let url = "http://localhost:8000/pagos/";

            if (desde) {
                url += `?desde=${desde}`;
            }

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                setPagos(data.data);
            }

        } catch (error) {
            console.error("Error cargando pagos", error);
        }
    };

    useEffect(() => {
        let desde = null;

        if (filtroActivo === "ultimo_mes") {
            const hoy = new Date();
            const haceUnMes = new Date();
            haceUnMes.setMonth(hoy.getMonth() - 1);
            desde = haceUnMes.toISOString().split("T")[0];
        }

        fetchPagos(desde);

    }, [filtroActivo]);
    useEffect(() => {
        console.log("PAGOS:", pagos);
    }, [pagos]);

    return (
        <div className="card">
            <h2>Pagos</h2>

            <div style={{
                display: "flex",
                gap: "10px",
                marginBottom: "20px"
            }}>
                {[
                    { key: "todos", label: "Todos" },
                    { key: "ultimo_mes", label: "Último mes" },
                ].map((f) => (
                    <button
                        key={f.key}
                        onClick={() => handleFiltro(f.key)}
                        style={{
                            padding: "8px 14px",
                            borderRadius: "20px",
                            border: "none",
                            cursor: "pointer",
                            background:
                                filtroActivo === f.key ? "#2563eb" : "#e5e7eb",
                            color:
                                filtroActivo === f.key ? "white" : "black",
                        }}
                    >
                        {f.label}
                    </button>
                ))}
            </div>

            <table style={{ width: "100%", marginTop: "20px" }}>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Cliente</th>
                        <th>Monto</th>
                        <th>Capital</th>
                        <th>Interés</th>
                    </tr>
                </thead>

                <tbody>
                    {pagos.length > 0 ? (
                        pagos.map((p) => (
                            <tr
                                key={p.id}
                                onClick={() => navigate(`/clientes/${p.cliente_id}/pagos`)}
                                style={{ cursor: "pointer" }}
                            >
                                <td>{new Date(p.fecha_pago).toLocaleDateString()}</td>
                                <td>{p.cliente_nombre}</td>
                                <td>L {p.monto_pagado}</td>
                                <td>L {p.capital_pagado}</td>
                                <td>L {p.interes_pagado}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5">No hay pagos</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}