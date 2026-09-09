import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import './components/ui/ui.css'

import AppShell from './components/layout/AppShell'
import AssetDetailPage from './pages/AssetDetailPage'
import AssetsPage from './pages/AssetsPage'
import CollectionsPage from './pages/CollectionsPage'
import DashboardPage from './pages/DashboardPage'
import DispositionPage from './pages/DispositionPage'
import ProcessingPage from './pages/ProcessingPage'
import ReportsPage from './pages/ReportsPage'
import SanitizationPage from './pages/SanitizationPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/collections"
            element={<CollectionsPage />}
          />

          <Route
            path="/assets"
            element={<AssetsPage />}
          />

          <Route
            path="/assets/:assetId/*"
            element={<AssetDetailPage />}
          />

          <Route
            path="/processing"
            element={<ProcessingPage />}
          />

          <Route
            path="/sanitization"
            element={<SanitizationPage />}
          />

          <Route
            path="/disposition"
            element={<DispositionPage />}
          />

          <Route
            path="/reports"
            element={<ReportsPage />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App