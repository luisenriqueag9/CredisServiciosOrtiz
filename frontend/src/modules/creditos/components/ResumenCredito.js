export default function ResumenCredito({ resumen }) {

    const total =
        (resumen?.pagos?.total || 0) +
        (resumen?.credito?.saldo_actual || 0);

    const porcentaje =
        total > 0
            ? ((resumen.pagos.total / total) * 100).toFixed(1)
            : 0;

    return (
        <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "16px",
            marginTop: "20px"
        }}>

            <Card title="Saldo actual" color="#2563eb" value={resumen.credito.saldo_actual} />
            <Card title="Total pagado" color="#10b981" value={resumen.pagos.total} />
            <Card title="Pendiente" color="#f59e0b" value={resumen.credito.saldo_actual} />
            <Card title="% pagado" color="#6366f1" value={`${porcentaje}%`} />

        </div>
    );
}


// 🔹 lo dejamos interno por ahora
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