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

  // Color azul del botón "Volver" según tu imagen
  const azulCorporativo = "#0ea5e9"; 

  useEffect(() => {
    if (clienteInicial) {
      setForm(clienteInicial);
    }
  }, [clienteInicial]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const validar = () => {
    if (!form.nombre.trim()) return "El nombre es obligatorio";
    const identidadLimpia = form.identidad.replace(/-/g, "");
    if (identidadLimpia.length !== 13) return "Identidad debe tener 13 dígitos";
    const telLimpio = form.telefono.replace(/-/g, "");
    if (telLimpio.length !== 8) return "Teléfono debe tener 8 dígitos";
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
      const dataEnviar = { ...form, identidad: form.identidad.replace(/-/g, "") };
      let data;
      if (clienteInicial) {
        data = await onClienteCreado(dataEnviar);
        setMensaje("Cliente actualizado");
      } else {
        data = await createCliente(dataEnviar);
        if (data) onClienteCreado(data);
        setMensaje("Cliente registrado");
        setForm({ nombre: "", identidad: "", telefono: "", direccion: "", sucursal_id: 1 });
      }
    } catch {
      setError("Error al guardar");
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // ESTILOS AJUSTADOS A TU CARD
  // =========================
  const containerStyle = {
    fontFamily: "'Inter', system-ui, sans-serif",
    width: "100%", // Ahora ocupa todo el ancho disponible de la card
    padding: "0px", // Quitamos padding extra para que no choque
  };

  const inputStyle = {
    padding: "14px 16px",
    borderRadius: "10px",
    border: "1px solid #e2e8f0",
    fontSize: "15px",
    width: "100%",
    boxSizing: "border-box",
    outline: "none",
    backgroundColor: "#f8fafc",
    transition: "all 0.2s"
  };

  const buttonStyle = {
    padding: "16px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: loading ? "#94a3b8" : azulCorporativo, // Azul de tu imagen
    color: "white",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: loading ? "not-allowed" : "pointer",
    width: "100%",
    marginTop: "10px",
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
  };

  return (
    <div style={containerStyle}>
      {error && <div style={{ color: "#ef4444", marginBottom: "15px", fontWeight: "500" }}>{error}</div>}
      {mensaje && <div style={{ color: "#10b981", marginBottom: "15px", fontWeight: "500" }}>{mensaje}</div>}

      <form onSubmit={handleSubmit}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 320px", // Nombre grande, ID fijo
            gap: "20px",
            marginBottom: "20px"
          }}
        >
          {/* NOMBRE - Tamaño de fuente un poco mayor */}
          <input
            name="nombre"
            value={form.nombre}
            onChange={handleChange}
            placeholder="Nombre completo del cliente"
            style={{ ...inputStyle, fontSize: "16px" }} 
          />

          {/* IDENTIDAD - Ajustada al formato */}
          <input
            type="text"
            name="identidad"
            value={form.identidad}
            maxLength={15}
            onChange={(e) => {
              let value = e.target.value.replace(/\D/g, "");
              if (value.length > 13) return;
              if (value.length > 4) value = value.slice(0, 4) + "-" + value.slice(4);
              if (value.length > 9) value = value.slice(0, 9) + "-" + value.slice(9);
              setForm({ ...form, identidad: value });
            }}
            placeholder="ID: 0000-0000-00000"
            style={{ ...inputStyle, textAlign: "center", letterSpacing: "1px" }}
          />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 320px", // Dirección grande, Celular fijo
            gap: "20px",
            marginBottom: "25px"
          }}
        >
          {/* DIRECCIÓN */}
          <textarea
            name="direccion"
            value={form.direccion}
            onChange={handleChange}
            placeholder="Dirección exacta de residencia"
            style={{
              ...inputStyle,
              height: "50px",
              fontSize: "16px",
              resize: "none",
              fontFamily: "inherit"
            }}
          />

          {/* TELÉFONO */}
          <input
            type="text"
            name="telefono"
            value={form.telefono}
            maxLength={9}
            onChange={(e) => {
              let value = e.target.value.replace(/\D/g, "");
              if (value.length > 8) return;
              if (value.length > 4) value = value.slice(0, 4) + "-" + value.slice(4);
              setForm({ ...form, telefono: value });
            }}
            placeholder="Tel: 0000-0000"
            style={{ ...inputStyle, textAlign: "center", letterSpacing: "1px" }}
          />
        </div>

        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? "Guardando..." : clienteInicial ? "ACTUALIZAR CLIENTE" : "REGISTRAR CLIENTE"}
        </button>
      </form>
    </div>
  );
}

export default ClienteForm;