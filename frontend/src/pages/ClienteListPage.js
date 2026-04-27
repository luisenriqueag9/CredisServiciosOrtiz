import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ClienteList from "../components/ClienteList";
import { getClientes } from "../services/clienteService";

export default function ClienteListWrapper() {
  const navigate = useNavigate();
  const [clientes, setClientes] = useState([]);

  useEffect(() => {
    getClientes().then(setClientes);
  }, []);


  return (
    <div className="card">
      <button onClick={() => navigate("/clientes")}>
        ← Volver
      </button>

      <h2>Lista de Clientes</h2>

      <ClienteList clientes={clientes} />
    </div>
  );
}