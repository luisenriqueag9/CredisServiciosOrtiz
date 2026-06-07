import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function GastoEditPage() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [form, setForm] = useState({
        concepto: "",
        monto: "",
        fecha: "",
        descripcion: ""
    });

    const fetchGasto = async () => {
        try {
            const res = await fetch(`http://localhost:8000/gastos/${id}`);
            const data = await res.json();

            if (data.success) {
                setForm(data.data);
            }

        } catch (error) {
            console.error("Error cargando gasto", error);
        }
    };

    useEffect(() => {
        fetchGasto();
    }, []);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`http://localhost:8000/gastos/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(form)
            });

            const data = await res.json();

            if (data.success) {
                alert("Gasto actualizado");
                navigate("/gastos");
            }

        } catch (error) {
            console.error("Error actualizando gasto", error);
        }
    };

    return (
        <div className="card">
            <h2>✏️ Editar Gasto</h2>

            <form onSubmit={handleSubmit} style={{ marginTop: "20px" }}>

                <input
                    type="text"
                    name="concepto"
                    value={form.concepto}
                    onChange={handleChange}
                />

                <input
                    type="number"
                    name="monto"
                    value={form.monto}
                    onChange={handleChange}
                />

                <input
                    type="date"
                    name="fecha"
                    value={form.fecha}
                    onChange={handleChange}
                />

                <textarea
                    name="descripcion"
                    value={form.descripcion || ""}
                    onChange={handleChange}
                />

                <button type="submit">Actualizar</button>
            </form>
        </div>
    );
}