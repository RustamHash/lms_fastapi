import { Route } from 'react-router-dom'
import { GenericCreatePage } from '../components/GenericCreatePage'
import { GenericDetailFromConfig } from '../components/GenericDetailFromConfig'
import { FileCreatePage } from './FileCreatePage'
import { addressConfig } from '../features/addresses/config'
import { addressInputAliasConfig } from '../features/addresses/addressInputAliasConfig'
import { productsConfig } from '../features/products/config'
import { productGroupsConfig } from '../features/product-groups/config'
import { packagesConfig } from '../features/packages/config'
import { productLocationsConfig } from '../features/product-locations/config'
import { batchesConfig } from '../features/batches/config'
import { lpnsConfig } from '../features/lpns/config'
import { inboundOrdersConfig } from '../features/inbound-orders/config'
import { outboundOrdersConfig } from '../features/outbound-orders/config'
import { returnOrdersConfig } from '../features/return-orders/config'
import { tasksConfig } from '../features/tasks/config'
import { stockConfig } from '../features/stock/config'
import { usersConfig } from '../features/users/config'
import { rolesConfig } from '../features/roles/config'
import { tariffConfig } from '../features/tariffs/config'
import { tariffDocumentsConfig } from '../features/tariff-documents/config'
import { driversConfig } from '../features/drivers/config'
import { vehiclesConfig } from '../features/vehicles/config'
import { routesConfig } from '../features/routes/config'
import { carriersConfig } from '../features/carriers/config'
import { keepersConfig } from '../features/keepers/config'
import { documentsConfig } from '../features/documents/config'
import { deliveryOrdersConfig } from '../features/delivery-orders/config'
import { deviationsConfig } from '../features/deviations/config'
import { routeLinesConfig } from '../features/route-lines/config'
import { notificationsConfig } from '../features/notifications/config'
import { notificationRulesConfig } from '../features/notification-rules/config'
import { auditConfig } from '../features/audit/config'
import { zonesConfig } from '../features/topology-zones/config'
import { rowsConfig } from '../features/topology-rows/config'
import { locationsConfig } from '../features/topology-locations/config'

export function entityCrudRoutes() {
  return (
    <>
      <Route path="/reference/addresses/new" element={<GenericCreatePage config={addressConfig.list} />} />
      <Route path="/reference/address-input-aliases/new" element={<GenericCreatePage config={addressInputAliasConfig.list} />} />
      <Route path="/reference/products/new" element={<GenericCreatePage config={productsConfig} />} />
      <Route path="/reference/product-groups/new" element={<GenericCreatePage config={productGroupsConfig} />} />
      <Route path="/reference/product-groups/:id" element={<GenericDetailFromConfig config={productGroupsConfig} />} />
      <Route path="/reference/packages/new" element={<GenericCreatePage config={packagesConfig} />} />
      <Route path="/reference/packages/:id" element={<GenericDetailFromConfig config={packagesConfig} />} />
      <Route path="/reference/product-locations/new" element={<GenericCreatePage config={productLocationsConfig} />} />
      <Route path="/reference/product-locations/:id" element={<GenericDetailFromConfig config={productLocationsConfig} />} />
      <Route path="/reference/batches/new" element={<GenericCreatePage config={batchesConfig} />} />
      <Route path="/reference/lpns/new" element={<GenericCreatePage config={lpnsConfig} />} />
      <Route path="/reference/tariffs/new" element={<GenericCreatePage config={tariffConfig.list} />} />
      <Route path="/reference/tariff-documents/new" element={<GenericCreatePage config={tariffDocumentsConfig} />} />
      <Route path="/reference/drivers/new" element={<GenericCreatePage config={driversConfig} />} />
      <Route path="/reference/vehicles/new" element={<GenericCreatePage config={vehiclesConfig} />} />
      <Route path="/reference/routes/new" element={<GenericCreatePage config={routesConfig} />} />
      <Route path="/orders/inbound/new" element={<GenericCreatePage config={inboundOrdersConfig} />} />
      <Route path="/orders/outbound/new" element={<GenericCreatePage config={outboundOrdersConfig} />} />
      <Route path="/orders/return/new" element={<GenericCreatePage config={returnOrdersConfig} />} />
      <Route path="/tasks/new" element={<GenericCreatePage config={tasksConfig} />} />
      <Route path="/stock/new" element={<GenericCreatePage config={stockConfig} />} />
      <Route path="/users/new" element={<GenericCreatePage config={usersConfig} />} />
      <Route path="/roles/new" element={<GenericCreatePage config={rolesConfig} />} />
      <Route path="/carriers/new" element={<GenericCreatePage config={carriersConfig} />} />
      <Route path="/keepers/new" element={<GenericCreatePage config={keepersConfig} />} />
      <Route path="/documents/new" element={<GenericCreatePage config={documentsConfig} />} />
      <Route path="/delivery/orders/new" element={<GenericCreatePage config={deliveryOrdersConfig} />} />
      <Route path="/deviations/new" element={<GenericCreatePage config={deviationsConfig} />} />
      <Route path="/route-lines/new" element={<GenericCreatePage config={routeLinesConfig} />} />
      <Route path="/notifications/new" element={<GenericCreatePage config={notificationsConfig} />} />
      <Route path="/notifications/:id" element={<GenericDetailFromConfig config={notificationsConfig} />} />
      <Route path="/notification-rules/new" element={<GenericCreatePage config={notificationRulesConfig} />} />
      <Route path="/audit/new" element={<GenericCreatePage config={auditConfig} />} />
      <Route path="/audit/:id" element={<GenericDetailFromConfig config={auditConfig} />} />
      <Route path="/topology/zones/new" element={<GenericCreatePage config={zonesConfig} />} />
      <Route path="/topology/rows/new" element={<GenericCreatePage config={rowsConfig} />} />
      <Route path="/topology/locations/new" element={<GenericCreatePage config={locationsConfig} />} />
      <Route path="/files/new" element={<FileCreatePage />} />
    </>
  )
}
