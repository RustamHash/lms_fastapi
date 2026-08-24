import { useAuth, hasPermission, hasModuleAccess, getPermissionMessage } from '../auth/AuthContext'

export function usePermissions(module: string) {
  const { user } = useAuth()
  
  return {
    canView: hasPermission(user, module, 'view'),
    canCreate: hasPermission(user, module, 'create'),
    canUpdate: hasPermission(user, module, 'update'),
    canDelete: hasPermission(user, module, 'delete'),
    hasAccess: hasModuleAccess(user, module),
    getMessage: (action: string) => getPermissionMessage(user, module, action),
  }
}
