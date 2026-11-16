import { createBrowserRouter, Navigate } from 'react-router'
import { LoginPage, RegisterPage, RequireAuth } from '@/features/auth'
import { MonitorCreatePage, MonitorDetailPage, MonitorListPage } from '@/features/monitors'
import { paths, routePatterns } from '@/shared/config/paths'
import { AppLayout } from './AppLayout'
import { NotFoundPage } from './NotFoundPage'
import { RouteErrorPage } from './RouteErrorPage'

export const router = createBrowserRouter([
  { path: paths.login, element: <LoginPage />, errorElement: <RouteErrorPage /> },
  { path: paths.register, element: <RegisterPage />, errorElement: <RouteErrorPage /> },
  {
    // Everything below needs a logged-in client.
    element: <RequireAuth />,
    errorElement: <RouteErrorPage />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to={paths.monitors} replace /> },
          { path: paths.monitors, element: <MonitorListPage /> },
          { path: paths.newMonitor, element: <MonitorCreatePage /> },
          { path: routePatterns.monitor, element: <MonitorDetailPage /> },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
])
