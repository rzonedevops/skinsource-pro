import { useState } from 'react'

const NAV_ITEMS = [
  { id: 'dashboard', name: 'Dashboard' },
  { id: 'ingredients', name: 'Ingredients' },
  { id: 'suppliers', name: 'Suppliers' },
  { id: 'procurement', name: 'Procurement' },
]

function Layout({ children, currentPage, onPageChange }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="app-shell">
      <aside className="app-sidebar" style={{ width: open ? 220 : 76 }}>
        <div className="app-sidebar__brand">
          <img src="/assets/logo-regima-blue.jpg" alt="RégimA" />
          {open && <span>RégimA Zone</span>}
        </div>
        <button onClick={() => setOpen((prev) => !prev)} className="app-nav-btn" style={{ marginBottom: 10 }}>
          {open ? 'Close' : 'Menu'}
        </button>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            className={`app-nav-btn${currentPage === item.id ? ' is-active' : ''}`}
            style={{ marginBottom: 8 }}
            title={item.name}
          >
            {open ? item.name : item.name.slice(0, 1)}
          </button>
        ))}
      </aside>
      <main style={{ flex: 1, padding: '1rem 1.25rem' }}>
        <header style={{ marginBottom: '1rem' }}>
          <div className="rz-section__label">RégimA Zone</div>
          <h1 className="app-header__title">SkinSource Pro · {currentPage}</h1>
        </header>
        {children}
      </main>
    </div>
  )
}

export default Layout
