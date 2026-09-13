import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { navigationItems } from './navigation'
import './AppShell.css'

function AppShell() {
  const [mobileNavigationOpen, setMobileNavigationOpen] =
    useState(false)

  function closeMobileNavigation() {
    setMobileNavigationOpen(false)
  }

  return (
    <div className="app-shell">
      {mobileNavigationOpen && (
        <button
          type="button"
          className="app-mobile-overlay"
          aria-label="Close navigation"
          onClick={closeMobileNavigation}
        />
      )}

      <aside
        className={`app-sidebar${
          mobileNavigationOpen
            ? ' app-sidebar-mobile-open'
            : ''
        }`}
      >
        <div className="app-brand">
          <div className="app-brand-mark">
            OM
          </div>

          <div className="app-brand-text">
            <div className="app-brand-name">
              OM Recycling
            </div>

            <div className="app-brand-subtitle">
              Asset Management
            </div>
          </div>

          <button
            type="button"
            className="app-mobile-close"
            aria-label="Close navigation"
            onClick={closeMobileNavigation}
          >
            ×
          </button>
        </div>

        <nav
          className="app-navigation"
          aria-label="Main navigation"
        >
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `app-navigation-link${
                  isActive ? ' active' : ''
                }`
              }
              onClick={closeMobileNavigation}
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
          <div className="app-header-left">
            <button
              type="button"
              className="app-mobile-menu"
              aria-label="Open navigation"
              aria-expanded={
                mobileNavigationOpen
              }
              onClick={() =>
                setMobileNavigationOpen(true)
              }
            >
              <span />
              <span />
              <span />
            </button>

            <div>
              <div className="app-header-title">
                OM Recycling
              </div>

              <div className="app-header-subtitle">
                E-waste Asset Management
              </div>
            </div>
          </div>

          <div className="app-header-status">
            <span className="status-indicator" />
            <span>System Online</span>
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