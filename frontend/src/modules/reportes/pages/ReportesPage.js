import { useEffect, useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    ResponsiveContainer
} from "recharts";

export default function ReportesPage() {
    const [resumen, setResumen] = useState(null);
    const [grafico, setGrafico] = useState([]);

    const fetchGrafico = async () => {
        try {
            const res = await fetch("http://localhost:8000/reportes/mensual");
            const data = await res.json();

            if (data.success) {
                setGrafico(data.data);
            }

        } catch (error) {
            console.error("Error cargando gráfico", error);
        }
    };

    const fetchResumen = async () => {
        try {
            const res = await fetch("http://localhost:8000/reportes/resumen");
            const data = await res.json();

            if (data.success) {
                setResumen(data.data);
            }

        } catch (error) {
            console.error("Error cargando reportes", error);
        }
    };

    useEffect(() => {
        fetchResumen();
        fetchGrafico();
    }, []);

    return (
        <div className="card">
            <h2>📊 Reportes</h2>

            {!resumen ? (
                <p>Cargando...</p>
            ) : (
                <div style={{
                    display: "flex",
                    gap: "20px",
                    marginTop: "20px",
                    flexWrap: "wrap",
                    justifyContent: "space-between"
                }}>

                    <div style={{
                        background: "#16a34a",
                        color: "white",
                        padding: "20px",
                        borderRadius: "10px",
                        minWidth: "200px"
                    }}>
                        💰 Ingresos totales
                        <h3>L {Number(resumen?.total_ingresos || 0).toLocaleString()}</h3>
                    </div>

                    <div style={{
                        background: "#2563eb",
                        color: "white",
                        padding: "20px",
                        borderRadius: "10px",
                        minWidth: "200px"
                    }}>
                        📉 Capital recuperado
                        <h3>L {Number(resumen?.total_capital || 0).toLocaleString()}</h3>
                    </div>

                    <div style={{
                        background: "#f59e0b",
                        color: "white",
                        padding: "20px",
                        borderRadius: "10px",
                        minWidth: "200px"
                    }}>
                        📈 Intereses ganados
                        <h3>L {Number(resumen?.total_intereses || 0).toLocaleString()}</h3>
                    </div>

                    <div style={{
                        background: "#dc2626",
                        color: "white",
                        padding: "20px",
                        borderRadius: "10px",
                        minWidth: "200px"
                    }}>
                        💸 Gastos
                        <h3>L {Number(resumen?.total_gastos || 0).toLocaleString()}</h3>
                    </div>

                    <div style={{
                        background: "#059669",
                        color: "white",
                        padding: "20px",
                        borderRadius: "10px",
                        minWidth: "200px"
                    }}>
                        🟢 Utilidad
                        <h3>L {Number(resumen?.utilidad || 0).toLocaleString()}</h3>
                    </div>

                </div>
            )}

            <div style={{ marginTop: "40px" }}>
                <h3>📊 Ingresos por mes</h3>

                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={grafico}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="mes" />
                        <YAxis />
                        <Tooltip />
                        <Line
                            type="monotone"
                            dataKey="total"
                            stroke="#2563eb"
                            strokeWidth={3}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}