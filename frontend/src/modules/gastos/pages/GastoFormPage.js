import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function GastoFormPage() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        concepto: "",
        monto: "",
        fecha: "",
        descripcion: ""
    });

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch("http://localhost:8000/gastos/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(form)
            });

            const data = await res.json();

            if (data.success) {
                alert("Gasto registrado");
                navigate("/gastos");
            }

        } catch (error) {
            console.error("Error guardando gasto", error);
        }
    };

    return (
        <div className="card">
            <h2>➕ Nuevo Gasto</h2>

            <form onSubmit={handleSubmit} style={{ marginTop: "20px" }}>

                <input
                    type="text"
                    name="concepto"
                    placeholder="Concepto"
                    value={form.concepto}
                    onChange={handleChange}
                    required
                />

                <input
                    type="number"
                    name="monto"
                    placeholder="Monto"
                    value={form.monto}
                    onChange={handleChange}
                    required
                />

                <input
                    type="date"
                    name="fecha"
                    value={form.fecha}
                    onChange={handleChange}
                    required
                />

                <textarea
                    name="descripcion"
                    placeholder="Descripción"
                    value={form.descripcion}
                    onChange={handleChange}
                />

                <button type="submit">Guardar</button>
            </form>
        </div>
    );
}