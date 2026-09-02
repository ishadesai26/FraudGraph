import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import CustomerDetailPage from './pages/CustomerDetailPage';
import FraudRingsPage from './pages/FraudRingsPage';
import FraudRingDetailPage from './pages/FraudRingDetailPage';
import TransactionDetailPage from './pages/TransactionDetailPage';
import AgentInvestigationPage from './pages/AgentInvestigationPage';
import SimulationPage from './pages/SimulationPage';

export function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 max-w-7xl mx-auto w-full overflow-y-auto">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/customers" element={<CustomersPage />} />
              <Route path="/customers/:customerId" element={<CustomerDetailPage />} />
              <Route path="/fraud-rings" element={<FraudRingsPage />} />
              <Route path="/fraud-rings/:ringId" element={<FraudRingDetailPage />} />
              <Route path="/transactions/:transactionId" element={<TransactionDetailPage />} />
              <Route path="/agents" element={<AgentInvestigationPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
