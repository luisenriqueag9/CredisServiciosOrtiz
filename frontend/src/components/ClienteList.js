import React, { useState } from "react";
import { deleteCliente } from "../services/clienteService";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

function ClienteList({ clientes }) {
  const [busqueda, setBusqueda] = useState("");
  useEffect(() => {
    setLista(clientes);
  }, [clientes]);
  const [lista, setLista] = useState([]);
  const navigate = useNavigate();

  // 🔍 Filtrar
  const clientesFiltrados = lista.filter((cliente) => {
    const texto = busqueda.toLowerCase();

    return (
      cliente.nombre.toLowerCase().includes(texto) ||
      cliente.identidad.toLowerCase().includes(texto)
    );
  });

  // 🗑 Eliminar
  const handleDelete = async (id) => {
    const confirmar = window.confirm("¿Eliminar cliente?");

    if (!confirmar) return;

    const res = await deleteCliente(id);

    if (res) {
      setLista((prev) => prev.filter((c) => c.id !== id));
    }
  };

  return (
    <div>
      
      <input
        type="text"
        placeholder="Buscar por nombre o identidad..."
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
      />

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Identidad</th>
            <th>Teléfono</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          {clientesFiltrados.map((cliente) => (
            <tr
              key={cliente.id}
              onClick={() => navigate(`/clientes/${cliente.id}`)}
              style={{ cursor: "pointer" }}
            >
              <td>{cliente.id}</td>
              <td>{cliente.nombre}</td>
              <td>{cliente.identidad}</td>
              <td>{cliente.telefono}</td>

              <td>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/clientes/editar/${cliente.id}`);
                  }}
                >
                  ✏️
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(cliente.id);
                  }}
                >
                  🗑
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ClienteList;