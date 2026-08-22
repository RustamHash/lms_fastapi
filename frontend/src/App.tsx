import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './auth/AuthContext'
import { Layout } from './components/Layout'
import { RequireAuth } from './components/RequireAuth'
import { AppNoticeProvider } from './notifications/AppNoticeContext'
const HomePage = lazy(() => import('./pages/HomePage').then(m => ({ default: m.HomePage })))
const ReferencesPage = lazy(() => import('./pages/ReferencesPage').then(m => ({ default: m.ReferencesPage })))
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })))
const AddressDetailPage = lazy(() => import('./pages/AddressDetailPage').then(m => ({ default: m.AddressDetailPage })))
const AddressInputAliasDetailPage = lazy(() => import('./pages/AddressInputAliasDetailPage').then(m => ({ default: m.AddressInputAliasDetailPage })))
const AddressInputAliasesPage = lazy(() => import('./pages/AddressInputAliasesPage').then(m => ({ default: m.AddressInputAliasesPage })))
const DeliveryZonesPage = lazy(() => import('./pages/DeliveryZonesPage').then(m => ({ default: m.DeliveryZonesPage })))
const LegalEntitiesPage = lazy(() => import('./pages/LegalEntitiesPage').then(m => ({ default: m.LegalEntitiesPage })))
const DepositorsPage = lazy(() => import('./pages/DepositorsPage').then(m => ({ default: m.DepositorsPage })))
const ClientsPage = lazy(() => import('./pages/ClientsPage').then(m => ({ default: m.ClientsPage })))
const TradePointsPage = lazy(() => import('./pages/TradePointsPage').then(m => ({ default: m.TradePointsPage })))
const ContractsPage = lazy(() => import('./pages/ContractsPage').then(m => ({ default: m.ContractsPage })))
const TariffsPage = lazy(() => import('./pages/TariffsPage').then(m => ({ default: m.TariffsPage })))
const LegalEntityDetailPage = lazy(() => import('./pages/LegalEntityDetailPage').then(m => ({ default: m.LegalEntityDetailPage })))
const LegalEntityEditPage = lazy(() => import('./pages/LegalEntityEditPage').then(m => ({ default: m.LegalEntityEditPage })))
const DepositorDetailPage = lazy(() => import('./pages/DepositorDetailPage').then(m => ({ default: m.DepositorDetailPage })))
const ClientDetailPage = lazy(() => import('./pages/ClientDetailPage').then(m => ({ default: m.ClientDetailPage })))
const TradePointDetailPage = lazy(() => import('./pages/TradePointDetailPage').then(m => ({ default: m.TradePointDetailPage })))
const ContractDetailPage = lazy(() => import('./pages/ContractDetailPage').then(m => ({ default: m.ContractDetailPage })))
const TariffDetailPage = lazy(() => import('./pages/TariffDetailPage').then(m => ({ default: m.TariffDetailPage })))
const LegalEntityCreatePage = lazy(() => import('./pages/LegalEntityCreatePage').then(m => ({ default: m.LegalEntityCreatePage })))
const DepositorCreatePage = lazy(() => import('./pages/DepositorCreatePage').then(m => ({ default: m.DepositorCreatePage })))
const ClientCreatePage = lazy(() => import('./pages/ClientCreatePage').then(m => ({ default: m.ClientCreatePage })))
const TradePointCreatePage = lazy(() => import('./pages/TradePointCreatePage').then(m => ({ default: m.TradePointCreatePage })))
const ContractCreatePage = lazy(() => import('./pages/ContractCreatePage').then(m => ({ default: m.ContractCreatePage })))
const AddressesPage = lazy(() => import('./pages/AddressesPage').then(m => ({ default: m.AddressesPage })))
const ProductsPage = lazy(() => import('./pages/ProductsPage').then(m => ({ default: m.ProductsPage })))
const BatchesPage = lazy(() => import('./pages/BatchesPage').then(m => ({ default: m.BatchesPage })))
const LpnsPage = lazy(() => import('./pages/LpnsPage').then(m => ({ default: m.LpnsPage })))
const OrdersHubPage = lazy(() => import('./pages/OrdersHubPage').then(m => ({ default: m.OrdersHubPage })))
const InboundOrdersPage = lazy(() => import('./pages/InboundOrdersPage').then(m => ({ default: m.InboundOrdersPage })))
const OutboundOrdersPage = lazy(() => import('./pages/OutboundOrdersPage').then(m => ({ default: m.OutboundOrdersPage })))
const ReturnOrdersPage = lazy(() => import('./pages/ReturnOrdersPage').then(m => ({ default: m.ReturnOrdersPage })))
const TasksPage = lazy(() => import('./pages/TasksPage').then(m => ({ default: m.TasksPage })))
const DocumentsPage = lazy(() => import('./pages/DocumentsPage').then(m => ({ default: m.DocumentsPage })))
const DeliveryOrdersPage = lazy(() => import('./pages/DeliveryOrdersPage').then(m => ({ default: m.DeliveryOrdersPage })))
const DriversPage = lazy(() => import('./pages/DriversPage').then(m => ({ default: m.DriversPage })))
const VehiclesPage = lazy(() => import('./pages/VehiclesPage').then(m => ({ default: m.VehiclesPage })))
const RoutesPage = lazy(() => import('./pages/RoutesPage').then(m => ({ default: m.RoutesPage })))
const NotificationsPage = lazy(() => import('./pages/NotificationsPage').then(m => ({ default: m.NotificationsPage })))
const UsersPage = lazy(() => import('./pages/UsersPage').then(m => ({ default: m.UsersPage })))
const RolesPage = lazy(() => import('./pages/RolesPage').then(m => ({ default: m.RolesPage })))
const IntegrationProfilesPage = lazy(() => import('./pages/IntegrationProfilesPage').then(m => ({ default: m.IntegrationProfilesPage })))
const IntegrationLogsPage = lazy(() => import('./pages/IntegrationLogsPage').then(m => ({ default: m.IntegrationLogsPage })))
const FilesPage = lazy(() => import('./pages/FilesPage').then(m => ({ default: m.FilesPage })))
const DocumentsHubPage = lazy(() => import('./pages/DocumentsHubPage').then(m => ({ default: m.DocumentsHubPage })))
const FilesHubPage = lazy(() => import('./pages/FilesHubPage').then(m => ({ default: m.FilesHubPage })))
const AuditPage = lazy(() => import('./pages/AuditPage').then(m => ({ default: m.AuditPage })))
const NotificationRulesPage = lazy(() => import('./pages/NotificationRulesPage').then(m => ({ default: m.NotificationRulesPage })))
const TariffDocumentsPage = lazy(() => import('./pages/TariffDocumentsPage').then(m => ({ default: m.TariffDocumentsPage })))
const NotificationRuleDetailPage = lazy(() => import('./pages/NotificationRuleDetailPage').then(m => ({ default: m.NotificationRuleDetailPage })))
const TariffDocumentDetailPage = lazy(() => import('./pages/TariffDocumentDetailPage').then(m => ({ default: m.TariffDocumentDetailPage })))
const CarriersPage = lazy(() => import('./pages/CarriersPage').then(m => ({ default: m.CarriersPage })))
const KeepersPage = lazy(() => import('./pages/KeepersPage').then(m => ({ default: m.KeepersPage })))
const DeviationsPage = lazy(() => import('./pages/DeviationsPage').then(m => ({ default: m.DeviationsPage })))
const RouteLinesPage = lazy(() => import('./pages/RouteLinesPage').then(m => ({ default: m.RouteLinesPage })))
const StockPage = lazy(() => import('./pages/StockPage').then(m => ({ default: m.StockPage })))
const TopologyWarehousesPage = lazy(() => import('./pages/TopologyWarehousesPage').then(m => ({ default: m.TopologyWarehousesPage })))
const TopologyVirtualWarehousesPage = lazy(() => import('./pages/TopologyVirtualWarehousesPage').then(m => ({ default: m.TopologyVirtualWarehousesPage })))
const TopologyZonesPage = lazy(() => import('./pages/TopologyZonesPage').then(m => ({ default: m.TopologyZonesPage })))
const TopologyRowsPage = lazy(() => import('./pages/TopologyRowsPage').then(m => ({ default: m.TopologyRowsPage })))
const TopologyLocationsPage = lazy(() => import('./pages/TopologyLocationsPage').then(m => ({ default: m.TopologyLocationsPage })))

const BatchDetailPage = lazy(() => import('./pages/BatchDetailPage').then(m => ({ default: m.BatchDetailPage })))
const CarrierDetailPage = lazy(() => import('./pages/CarrierDetailPage').then(m => ({ default: m.CarrierDetailPage })))
const DeliveryOrderDetailPage = lazy(() => import('./pages/DeliveryOrderDetailPage').then(m => ({ default: m.DeliveryOrderDetailPage })))
const DeliveryZoneDetailPage = lazy(() => import('./pages/DeliveryZoneDetailPage').then(m => ({ default: m.DeliveryZoneDetailPage })))
const DeliveryZoneCreatePage = lazy(() => import('./pages/DeliveryZoneCreatePage').then(m => ({ default: m.DeliveryZoneCreatePage })))
const DeviationDetailPage = lazy(() => import('./pages/DeviationDetailPage').then(m => ({ default: m.DeviationDetailPage })))
const DocumentDetailPage = lazy(() => import('./pages/DocumentDetailPage').then(m => ({ default: m.DocumentDetailPage })))
const DriverDetailPage = lazy(() => import('./pages/DriverDetailPage').then(m => ({ default: m.DriverDetailPage })))
const FileDetailPage = lazy(() => import('./pages/FileDetailPage').then(m => ({ default: m.FileDetailPage })))
const InboundOrderDetailPage = lazy(() => import('./pages/InboundOrderDetailPage').then(m => ({ default: m.InboundOrderDetailPage })))
const IntegrationLogDetailPage = lazy(() => import('./pages/IntegrationLogDetailPage').then(m => ({ default: m.IntegrationLogDetailPage })))
const IntegrationProfileDetailPage = lazy(() => import('./pages/IntegrationProfileDetailPage').then(m => ({ default: m.IntegrationProfileDetailPage })))
const KeeperDetailPage = lazy(() => import('./pages/KeeperDetailPage').then(m => ({ default: m.KeeperDetailPage })))
const LpnDetailPage = lazy(() => import('./pages/LpnDetailPage').then(m => ({ default: m.LpnDetailPage })))
const OutboundOrderDetailPage = lazy(() => import('./pages/OutboundOrderDetailPage').then(m => ({ default: m.OutboundOrderDetailPage })))
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage').then(m => ({ default: m.ProductDetailPage })))
const ReturnOrderDetailPage = lazy(() => import('./pages/ReturnOrderDetailPage').then(m => ({ default: m.ReturnOrderDetailPage })))
const RoleDetailPage = lazy(() => import('./pages/RoleDetailPage').then(m => ({ default: m.RoleDetailPage })))
const RouteLineDetailPage = lazy(() => import('./pages/RouteLineDetailPage').then(m => ({ default: m.RouteLineDetailPage })))
const RouteDetailPage = lazy(() => import('./pages/RouteDetailPage').then(m => ({ default: m.RouteDetailPage })))
const StockDetailPage = lazy(() => import('./pages/StockDetailPage').then(m => ({ default: m.StockDetailPage })))
const TaskDetailPage = lazy(() => import('./pages/TaskDetailPage').then(m => ({ default: m.TaskDetailPage })))
const TopologyLocationDetailPage = lazy(() => import('./pages/TopologyLocationDetailPage').then(m => ({ default: m.TopologyLocationDetailPage })))
const TopologyRowDetailPage = lazy(() => import('./pages/TopologyRowDetailPage').then(m => ({ default: m.TopologyRowDetailPage })))
const TopologyVirtualWarehouseDetailPage = lazy(() => import('./pages/TopologyVirtualWarehouseDetailPage').then(m => ({ default: m.TopologyVirtualWarehouseDetailPage })))
const TopologyWarehouseDetailPage = lazy(() => import('./pages/TopologyWarehouseDetailPage').then(m => ({ default: m.TopologyWarehouseDetailPage })))
const TopologyZoneDetailPage = lazy(() => import('./pages/TopologyZoneDetailPage').then(m => ({ default: m.TopologyZoneDetailPage })))
const UserDetailPage = lazy(() => import('./pages/UserDetailPage').then(m => ({ default: m.UserDetailPage })))

const TopologyHubPage = lazy(() => import('./pages/TopologyHubPage').then(m => ({ default: m.TopologyHubPage })))
const ReportsHubPage = lazy(() => import('./pages/ReportsHubPage').then(m => ({ default: m.ReportsHubPage })))
const SystemHubPage = lazy(() => import('./pages/SystemHubPage').then(m => ({ default: m.SystemHubPage })))
const IntegrationsHubPage = lazy(() => import('./pages/IntegrationsHubPage').then(m => ({ default: m.IntegrationsHubPage })))
const DeliveryHubPage = lazy(() => import('./pages/DeliveryHubPage').then(m => ({ default: m.DeliveryHubPage })))


const ProductGroupsPage = lazy(() => import('./pages/ProductGroupsPage').then(m => ({ default: m.ProductGroupsPage })))
const PackagesPage = lazy(() => import('./pages/PackagesPage').then(m => ({ default: m.PackagesPage })))
const ProductLocationsPage = lazy(() => import('./pages/ProductLocationsPage').then(m => ({ default: m.ProductLocationsPage })))

const VehicleDetailPage = lazy(() => import('./pages/VehicleDetailPage').then(m => ({ default: m.VehicleDetailPage })))


import './App.css'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppNoticeProvider>
          <BrowserRouter>
            <Suspense fallback={<div className="app-main"><p className="app-card">Загрузка...</p></div>}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route element={<RequireAuth />}>
                <Route element={<Layout />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/references" element={<ReferencesPage />} />
                  <Route path="/orders" element={<OrdersHubPage />} />
                  <Route path="/orders/inbound" element={<InboundOrdersPage />} />
                  <Route path="/orders/outbound" element={<OutboundOrdersPage />} />
                  <Route path="/orders/return" element={<ReturnOrdersPage />} />
                  
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
                  <Route path="/reference/tariff-documents" element={<TariffDocumentsPage />} />
                  <Route path="/reference/tariff-documents/:docId" element={<TariffDocumentDetailPage />} />
                  
                  {/* Склад */}
                  <Route path="/reference/products" element={<ProductsPage />} />
                  <Route path="/reference/product-groups" element={<ProductGroupsPage />} />
                  <Route path="/reference/packages" element={<PackagesPage />} />
                  <Route path="/reference/product-locations" element={<ProductLocationsPage />} />

                  <Route path="/reference/batches" element={<BatchesPage />} />
                  <Route path="/reference/lpns" element={<LpnsPage />} />
                  <Route path="/tasks" element={<TasksPage />} />
                  
                  {/* Документы */}
                  <Route path="/documents" element={<DocumentsPage />} />
                  
                  {/* Доставка */}
                  <Route path="/delivery/orders" element={<DeliveryOrdersPage />} />
                  <Route path="/reference/drivers" element={<DriversPage />} />
                  <Route path="/reference/vehicles" element={<VehiclesPage />} />
                  <Route path="/reference/routes" element={<RoutesPage />} />
                  
                  {/* Система */}
                  <Route path="/audit" element={<AuditPage />} />
                  <Route path="/notification-rules" element={<NotificationRulesPage />} />
                  <Route path="/notification-rules/:ruleId" element={<NotificationRuleDetailPage />} />
                  <Route path="/notifications" element={<NotificationsPage />} />
                  <Route path="/users" element={<UsersPage />} />
                  <Route path="/roles" element={<RolesPage />} />
                  
                  {/* Интеграции */}
                  <Route path="/integrations/profiles" element={<IntegrationProfilesPage />} />
                  <Route path="/integrations/logs" element={<IntegrationLogsPage />} />
                  
                  {/* Перевозчики и хранители */}
                  <Route path="/carriers" element={<CarriersPage />} />
                  <Route path="/keepers" element={<KeepersPage />} />
                  
                  {/* Доставка */}
                  <Route path="/deviations" element={<DeviationsPage />} />
                  <Route path="/route-lines" element={<RouteLinesPage />} />
                  
                  {/* Склад */}
                  <Route path="/stock" element={<StockPage />} />
                  
                  {/* Топология */}
                  <Route path="/topology/warehouses" element={<TopologyWarehousesPage />} />
                  <Route path="/topology/virtual-warehouses" element={<TopologyVirtualWarehousesPage />} />
                  <Route path="/topology/zones" element={<TopologyZonesPage />} />
                  <Route path="/topology/rows" element={<TopologyRowsPage />} />
                  <Route path="/topology/locations" element={<TopologyLocationsPage />} />
                  
                  {/* Файлы */}
                  <Route path="/documents-hub" element={<DocumentsHubPage />} />
                  <Route path="/files-hub" element={<FilesHubPage />} />
                  <Route path="/files" element={<FilesPage />} />
                  
                                    <Route path="/reference/batches/:id" element={<BatchDetailPage />} />
                  <Route path="/carriers/:id" element={<CarrierDetailPage />} />
                  <Route path="/delivery/orders/:id" element={<DeliveryOrderDetailPage />} />
                  <Route path="/reference/delivery-zones/new" element={<DeliveryZoneCreatePage />} />
                  <Route path="/reference/delivery-zones/:id" element={<DeliveryZoneDetailPage />} />
                  <Route path="/deviations/:id" element={<DeviationDetailPage />} />
                  <Route path="/documents/:id" element={<DocumentDetailPage />} />
                  <Route path="/reference/drivers/:id" element={<DriverDetailPage />} />
                  <Route path="/files/:id" element={<FileDetailPage />} />
                  <Route path="/orders/inbound/:id" element={<InboundOrderDetailPage />} />
                  <Route path="/integrations/logs/:id" element={<IntegrationLogDetailPage />} />
                  <Route path="/integrations/profiles/:id" element={<IntegrationProfileDetailPage />} />
                  <Route path="/keepers/:id" element={<KeeperDetailPage />} />
                  <Route path="/reference/lpns/:id" element={<LpnDetailPage />} />
                  <Route path="/orders/outbound/:id" element={<OutboundOrderDetailPage />} />
                  <Route path="/reference/products/:id" element={<ProductDetailPage />} />
                  <Route path="/orders/return/:id" element={<ReturnOrderDetailPage />} />
                  <Route path="/roles/:id" element={<RoleDetailPage />} />
                  <Route path="/route-lines/:id" element={<RouteLineDetailPage />} />
                  <Route path="/reference/routes/:id" element={<RouteDetailPage />} />
                  <Route path="/stock/:id" element={<StockDetailPage />} />
                  <Route path="/tasks/:id" element={<TaskDetailPage />} />
                  <Route path="/topology/locations/:id" element={<TopologyLocationDetailPage />} />
                  <Route path="/topology/rows/:id" element={<TopologyRowDetailPage />} />
                  <Route path="/topology/virtual-warehouses/:id" element={<TopologyVirtualWarehouseDetailPage />} />
                  <Route path="/topology/warehouses/:id" element={<TopologyWarehouseDetailPage />} />
                  <Route path="/topology/zones/:id" element={<TopologyZoneDetailPage />} />
                  <Route path="/users/:id" element={<UserDetailPage />} />
                  <Route path="/reference/vehicles/:id" element={<VehicleDetailPage />} />
                  
                  

                  <Route path="/topology" element={<TopologyHubPage />} />
                  <Route path="/reports" element={<ReportsHubPage />} />
                  <Route path="/system" element={<SystemHubPage />} />
                  <Route path="/integrations" element={<IntegrationsHubPage />} />
                  <Route path="/delivery" element={<DeliveryHubPage />} />

                  <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
              </Route>
            </Routes>
            </Suspense>
          </BrowserRouter>
        </AppNoticeProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
