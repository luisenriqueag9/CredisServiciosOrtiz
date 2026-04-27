import React, { useState, useEffect } from "react";
import { createCliente } from "../services/clienteService";

function ClienteForm({ onClienteCreado, clienteInicial }) {
  const [form, setForm] = useState({
    nombre: "",
    identidad: "",
    telefono: "",
    direccion: "",
    sucursal_id: 1,
  });

  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (clienteInicial) {
      setForm(clienteInicial);
    }
  }, [clienteInicial]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "identidad" || name === "telefono") {
      if (!/^\d*$/.test(value)) return;
    }

    setForm({
      ...form,
      [name]: value,
    });
  };

  const validar = () => {
    if (!form.nombre.trim()) return "El nombre es obligatorio";

    if (!form.identidad.trim()) return "La identidad es obligatoria";
    if (!/^\d+$/.test(form.identidad)) return "Solo números en identidad";
    if (form.identidad.length !== 13) return "Identidad debe tener 13 dígitos";

    if (!form.telefono.trim()) return "El teléfono es obligatorio";
    if (!/^\d+$/.test(form.telefono)) return "Solo números en teléfono";
    if (form.telefono.length !== 8) return "Teléfono debe tener 8 dígitos";

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError(null);
    setMensaje(null);

    const errorValidacion = validar();
    if (errorValidacion) {
      setError(errorValidacion);
      return;
    }

    try {
      setLoading(true);

      let data;

      if (clienteInicial) {
        data = await onClienteCreado(form);
        setMensaje("Cliente actualizado");
      } else {
        data = await createCliente(form);
        if (data) onClienteCreado(data);
        setMensaje("Cliente creado");

        setForm({
          nombre: "",
          identidad: "",
          telefono: "",
          direccion: "",
          sucursal_id: 1,
        });
      }
    } catch {
      setError("Error al guardar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {mensaje && <div style={{ color: "green" }}>{mensaje}</div>}

      <form onSubmit={handleSubmit}>
        <input name="nombre" value={form.nombre} onChange={handleChange} placeholder="Nombre" />
        <input name="identidad" value={form.identidad} onChange={handleChange} maxLength={13} placeholder="Identidad" />
        <input name="telefono" value={form.telefono} onChange={handleChange} maxLength={8} placeholder="Teléfono" />
        <input name="direccion" value={form.direccion} onChange={handleChange} placeholder="Dirección" />

        <button type="submit" disabled={loading}>
          {loading ? "Guardando..." : "Guardar"}
        </button>
      </form>
    </div>
  );
}

export default ClienteForm;