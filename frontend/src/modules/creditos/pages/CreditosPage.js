import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function CreditosPage() {
    const [creditos, setCreditos] = useState([]);
    const [filtroActivo, setFiltroActivo] = useState("todos");
    const navigate = useNavigate();

    const fetchCreditos = async (desde = null, estado = null) => {
        try {
            let url = "http://localhost:8000/creditos";

            const params = [];

            if (desde) params.push(`desde=${desde}`);
            if (estado) params.push(`estado=${estado}`);

            if (params.length > 0) {
                url += "?" + params.join("&");
            }

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                setCreditos(data.data);
            }
        } catch (error) {
            console.error("Error cargando créditos", error);
        }
    };
    const filtrarUltimoMes = () => {
        const hoy = new Date();
        const haceUnMes = new Date();

        haceUnMes.setMonth(hoy.getMonth() - 1);

        const fecha = haceUnMes.toISOString().split("T")[0];

        fetchCreditos(fecha);
    };

    const handleFiltro = (tipo) => {
        setFiltroActivo(tipo);

        if (tipo === "todos") return fetchCreditos();

        if (tipo === "ultimo_mes") return filtrarUltimoMes();

        if (tipo === "activos") return fetchCreditos(null, "ACTIVO");

        if (tipo === "finalizados") return fetchCreditos(null, "FINALIZADO");
    };

    useEffect(() => {
        fetchCreditos();
    }, []);

    return (
        <div className="card">
            <h2>Créditos</h2>

            <div style={{
                display: "flex",
                gap: "10px",
                marginTop: "20px",
                marginBottom: "20px",
                flexWrap: "wrap"
            }}>
                {[
                    { key: "todos", label: "Todos" },
                    { key: "ultimo_mes", label: "Último mes" },
                    { key: "activos", label: "Activos" },
                    { key: "finalizados", label: "Finalizados" },
                    { key: "mora", label: "En mora" },
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

            <table style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Cliente</th>
                        <th>Monto</th>
                        <th>Saldo</th>
                        <th>Estado</th>
                    </tr>
                </thead>

                <tbody>
                    {creditos.length > 0 ? (
                        creditos.map((c) => (
                            <tr
                                key={c.id}
                                onClick={() => navigate(`/creditos/${c.id}`)}
                                style={{ cursor: "pointer" }}
                            >
                                <td>{c.cliente_nombre}</td>
                                <td>L {c.monto}</td>
                                <td>L {c.saldo_actual}</td>
                                <td>{c.estado}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4">No hay créditos</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}