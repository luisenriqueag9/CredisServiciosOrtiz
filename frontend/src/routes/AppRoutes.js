import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";

import PagoForm from "../modules/creditos/components/PagoForm";
import CreditosPage from "../modules/creditos/pages/CreditosPage";
import CreditoFormWrapper from "../modules/creditos/pages/CreditoFormPage";
import CreditoDetailPage from "../modules/creditos/pages/CreditoDetailPage";
import PagosClientePage from "../modules/pagos/pages/PagosClientePage";
import ReportesPage from "../modules/reportes/pages/ReportesPage";
import GastosPage from "../modules/gastos/pages/GastosPage";
import GastoFormPage from "../modules/gastos/pages/GastoFormPage";
import GastoEditPage from "../modules/gastos/pages/GastoEditPage";


import ClientesPage, {
  ClienteFormWrapper,
  ClienteEditWrapper,
} from "../modules/clientes/pages/ClientesPage";

import ClienteDetailWrapper from "../modules/clientes/pages/ClienteDetailPage";
import ClienteListWrapper from "../modules/clientes/pages/ClienteListPage";


import PagosPage from "../modules/pagos/pages/PagosPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        <Route element={<DashboardLayout />}>

          <Route path="/" element={<ClientesPage />} />

          {/* CLIENTES */}
          <Route path="/clientes" element={<ClientesPage />} />
          <Route path="/clientes/nuevo" element={<ClienteFormWrapper />} />
          <Route path="/clientes/lista" element={<ClienteListWrapper />} />
          <Route path="/clientes/editar/:id" element={<ClienteEditWrapper />} />
          <Route path="/clientes/:id" element={<ClienteDetailWrapper />} />

          {/* CREDITOS */}
          <Route path="/creditos" element={<CreditosPage />} />
          <Route path="/creditos/nuevo/:cliente_id" element={<CreditoFormWrapper />} />
          <Route path="/creditos/:id" element={<CreditoDetailPage />} />

          {/* PAGOS */}
          <Route path="/pagos" element={<PagosPage />} />
          <Route path="/pagos/nuevo/:credito_id" element={<PagoForm />} />
          <Route path="/clientes/:id/pagos" element={<PagosClientePage />} />

          {/* REPORTES */}
          <Route path="/reportes" element={<ReportesPage />} />

          {/* GASTOS */}
          <Route path="/gastos" element={<GastosPage />} />
          <Route path="/gastos/nuevo" element={<GastoFormPage />} />
          <Route path="/gastos/:id/editar" element={<GastoEditPage />} />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;