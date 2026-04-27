import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "../components/Navbar";


// Importa TODO desde ClientesPage
import ClientesPage, {
  ClienteFormWrapper,
  ClienteEditWrapper,
} from "../pages/ClientesPage";

import CreditoFormWrapper from "../pages/CreditoFormPage";
import ClienteDetailWrapper from "../pages/ClienteDetailPage";
import ClienteListWrapper from "../pages/ClienteListPage";


function AppRoutes() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar />

        <div className="content">
          <Routes>
            <Route path="/" element={<ClientesPage />} />

            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/clientes/nuevo" element={<ClienteFormWrapper />} />
            <Route path="/clientes/lista" element={<ClienteListWrapper />} />
            <Route path="/clientes/editar/:id" element={<ClienteEditWrapper />} />
            <Route path="/clientes/:id" element={<ClienteDetailWrapper />} />
            <Route path="/creditos/nuevo/:cliente_id" element={<CreditoFormWrapper />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default AppRoutes;