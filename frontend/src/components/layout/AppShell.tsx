import { NavLink, Outlet } from 'react-router-dom'
import { navigationItems } from './navigation'
import './AppShell.css'

function AppShell() {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-brand">
          <div className="app-brand-mark">OM</div>
          <div>
            <div className="app-brand-name">OM Recycling</div>
            <div className="app-brand-subtitle">Asset Management</div>
          </div>
        </div>

        <nav className="app-navigation" aria-label="Main navigation">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `app-navigation-link${isActive ? ' active' : ''}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="app-sidebar-footer">
          <span>Asset Management System</span>
          <span>Development</span>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-header">
          <div>
            <div className="app-header-title">OM Recycling</div>
            <div className="app-header-subtitle">
              E-waste Asset Management
            </div>
          </div>

          <div className="app-header-status">
            <span className="status-indicator" />
            System Online
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppShell
