import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function GastosPage() {
    const [gastos, setGastos] = useState([]);
    const navigate = useNavigate();

    const fetchGastos = async () => {
        try {
            const res = await fetch("http://localhost:8000/gastos/");
            const data = await res.json();

            if (data.success) {
                setGastos(data.data);
            }

        } catch (error) {
            console.error("Error cargando gastos", error);
        }
    };

    const handleEliminar = async (id) => {
        const confirmar = window.confirm("¿Eliminar este gasto?");

        if (!confirmar) return;

        try {
            const res = await fetch(`http://localhost:8000/gastos/${id}`, {
                method: "DELETE"
            });

            const data = await res.json();

            if (data.success) {
                fetchGastos(); // 🔥 recarga la tabla
            }

        } catch (error) {
            console.error("Error eliminando gasto", error);
        }
    };

    useEffect(() => {
        fetchGastos();
    }, []);

    return (
        <div className="card">
            <h2>💸 Gastos</h2>

            <button
                onClick={() => navigate("/gastos/nuevo")}
                style={{
                    marginBottom: "15px",
                    padding: "8px 12px",
                    background: "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    cursor: "pointer"
                }}
            >
                ➕ Nuevo Gasto
            </button>

            <table style={{ width: "100%", marginTop: "20px" }}>
                <thead>
                    <tr>
                        <th>Concepto</th>
                        <th>Monto</th>
                        <th>Fecha</th>
                        <th>Acciones</th>
                    </tr>
                </thead>

                <tbody>
                    {gastos.length > 0 ? (
                        gastos.map((g) => (
                            <tr key={g.id}>
                                <td>{g.concepto}</td>
                                <td>L {Number(g.monto).toLocaleString()}</td>
                                <td>{new Date(g.fecha).toLocaleDateString()}</td>
                                <td style={{ display: "flex", gap: "5px" }}>

                                    <button
                                        onClick={() => navigate(`/gastos/${g.id}/editar`)}
                                        style={{
                                            padding: "5px 10px",
                                            background: "#f59e0b",
                                            color: "white",
                                            border: "none",
                                            borderRadius: "5px",
                                            cursor: "pointer"
                                        }}
                                    >
                                        ✏️
                                    </button>

                                    <button
                                        onClick={() => handleEliminar(g.id)}
                                        style={{
                                            padding: "5px 10px",
                                            background: "#dc2626",
                                            color: "white",
                                            border: "none",
                                            borderRadius: "5px",
                                            cursor: "pointer"
                                        }}
                                    >
                                        🗑
                                    </button>

                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4">No hay gastos</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}