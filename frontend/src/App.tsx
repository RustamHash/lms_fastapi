import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './auth/AuthContext'
import { Layout } from './components/Layout'
import { RequireAuth } from './components/RequireAuth'
import { AppNoticeProvider } from './notifications/AppNoticeContext'
import { HomePage } from './pages/HomePage'
import { ReferencesPage } from './pages/ReferencesPage'
import { LoginPage } from './pages/LoginPage'
import { AddressDetailPage } from './pages/AddressDetailPage'
import { AddressInputAliasDetailPage } from './pages/AddressInputAliasDetailPage'
import { AddressInputAliasesPage } from './pages/AddressInputAliasesPage'
import { DeliveryZonesPage } from './pages/DeliveryZonesPage'
import { LegalEntitiesPage } from './pages/LegalEntitiesPage'
import { DepositorsPage } from './pages/DepositorsPage'
import { ClientsPage } from './pages/ClientsPage'
import { TradePointsPage } from './pages/TradePointsPage'
import { ContractsPage } from './pages/ContractsPage'
import { TariffsPage } from './pages/TariffsPage'
import { LegalEntityDetailPage } from './pages/LegalEntityDetailPage'
import { LegalEntityEditPage } from './pages/LegalEntityEditPage'
import { DepositorDetailPage } from './pages/DepositorDetailPage'
import { ClientDetailPage } from './pages/ClientDetailPage'
import { TradePointDetailPage } from './pages/TradePointDetailPage'
import { ContractDetailPage } from './pages/ContractDetailPage'
import { TariffDetailPage } from './pages/TariffDetailPage'
import { LegalEntityCreatePage } from './pages/LegalEntityCreatePage'
import { DepositorCreatePage } from './pages/DepositorCreatePage'
import { ClientCreatePage } from './pages/ClientCreatePage'
import { TradePointCreatePage } from './pages/TradePointCreatePage'
import { ContractCreatePage } from './pages/ContractCreatePage'
import { AddressesPage } from './pages/AddressesPage'
import { ProductsPage } from './pages/ProductsPage'
import { BatchesPage } from './pages/BatchesPage'
import { LpnsPage } from './pages/LpnsPage'
import { TasksPage } from './pages/TasksPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { DeliveryOrdersPage } from './pages/DeliveryOrdersPage'
import { DriversPage } from './pages/DriversPage'
import { VehiclesPage } from './pages/VehiclesPage'
import { RoutesPage } from './pages/RoutesPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { UsersPage } from './pages/UsersPage'
import { RolesPage } from './pages/RolesPage'
import { IntegrationProfilesPage } from './pages/IntegrationProfilesPage'
import { IntegrationLogsPage } from './pages/IntegrationLogsPage'
import { FilesPage } from './pages/FilesPage'
import './App.css'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppNoticeProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route element={<RequireAuth />}>
                <Route element={<Layout />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/references" element={<ReferencesPage />} />
                  
                  {/* Справочники */}
                  <Route path="/reference/addresses" element={<AddressesPage />} />
                  <Route path="/reference/addresses/:addressId" element={<AddressDetailPage />} />
                  <Route path="/reference/address-input-aliases" element={<AddressInputAliasesPage />} />
                  <Route path="/reference/address-input-aliases/:aliasId" element={<AddressInputAliasDetailPage />} />
                  <Route path="/reference/delivery-zones" element={<DeliveryZonesPage />} />
                  <Route path="/reference/legal-entities" element={<LegalEntitiesPage />} />
                  <Route path="/reference/legal-entities/:entityId" element={<LegalEntityDetailPage />} />
                  <Route path="/reference/legal-entities/:entityId/edit" element={<LegalEntityEditPage />} />
                  <Route path="/reference/legal-entities/new" element={<LegalEntityCreatePage />} />
                  <Route path="/reference/depositors" element={<DepositorsPage />} />
                  <Route path="/reference/depositors/:depositorId" element={<DepositorDetailPage />} />
                  <Route path="/reference/depositors/new" element={<DepositorCreatePage />} />
                  <Route path="/reference/clients" element={<ClientsPage />} />
                  <Route path="/reference/clients/:clientId" element={<ClientDetailPage />} />
                  <Route path="/reference/clients/new" element={<ClientCreatePage />} />
                  <Route path="/reference/trade-points" element={<TradePointsPage />} />
                  <Route path="/reference/trade-points/:tpId" element={<TradePointDetailPage />} />
                  <Route path="/reference/trade-points/new" element={<TradePointCreatePage />} />
                  <Route path="/reference/contracts" element={<ContractsPage />} />
                  <Route path="/reference/contracts/:contractId" element={<ContractDetailPage />} />
                  <Route path="/reference/contracts/new" element={<ContractCreatePage />} />
                  <Route path="/reference/tariffs" element={<TariffsPage />} />
                  <Route path="/reference/tariffs/:tariffId" element={<TariffDetailPage />} />
                  
                  {/* Склад */}
                  <Route path="/warehouse/products" element={<ProductsPage />} />
                  <Route path="/warehouse/batches" element={<BatchesPage />} />
                  <Route path="/warehouse/lpns" element={<LpnsPage />} />
                  <Route path="/warehouse/tasks" element={<TasksPage />} />
                  
                  {/* Документы */}
                  <Route path="/documents" element={<DocumentsPage />} />
                  
                  {/* Доставка */}
                  <Route path="/delivery/orders" element={<DeliveryOrdersPage />} />
                  <Route path="/delivery/drivers" element={<DriversPage />} />
                  <Route path="/delivery/vehicles" element={<VehiclesPage />} />
                  <Route path="/delivery/routes" element={<RoutesPage />} />
                  
                  {/* Система */}
                  <Route path="/notifications" element={<NotificationsPage />} />
                  <Route path="/users" element={<UsersPage />} />
                  <Route path="/roles" element={<RolesPage />} />
                  
                  {/* Интеграции */}
                  <Route path="/integrations/profiles" element={<IntegrationProfilesPage />} />
                  <Route path="/integrations/logs" element={<IntegrationLogsPage />} />
                  
                  {/* Файлы */}
                  <Route path="/files" element={<FilesPage />} />
                  
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
        </AppNoticeProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
