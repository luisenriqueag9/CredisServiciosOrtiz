import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "../components/Navbar";
import PagoForm from "../modules/creditos/components/PagoForm";
import CreditosPage from "../modules/creditos/pages/CreditosPage";

// ✅ CLIENTES (nuevo path)
import ClientesPage, {
  ClienteFormWrapper,
  ClienteEditWrapper,
} from "../modules/clientes/pages/ClientesPage";

import ClienteDetailWrapper from "../modules/clientes/pages/ClienteDetailPage";
import ClienteListWrapper from "../modules/clientes/pages/ClienteListPage";

// ✅ CREDITOS (nuevo path)
import CreditoFormWrapper from "../modules/creditos/pages/CreditoFormPage";
import CreditoDetailPage from "../modules/creditos/pages/CreditoDetailPage";


function AppRoutes() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar />

        <div className="content">
          <Routes>
            <Route path="/" element={<ClientesPage />} />

            {/* CLIENTES */}
            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/clientes/nuevo" element={<ClienteFormWrapper />} />
            <Route path="/clientes/lista" element={<ClienteListWrapper />} />
            <Route path="/clientes/editar/:id" element={<ClienteEditWrapper />} />
            <Route path="/clientes/:id" element={<ClienteDetailWrapper />} />

            {/* CREDITOS */}
            <Route path="/creditos/nuevo/:cliente_id" element={<CreditoFormWrapper />} />
            <Route path="/creditos/:id" element={<CreditoDetailPage />} />
            <Route path="/pagos/nuevo/:credito_id" element={<PagoForm />} />
            <Route path="/creditos" element={<CreditosPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default AppRoutes;