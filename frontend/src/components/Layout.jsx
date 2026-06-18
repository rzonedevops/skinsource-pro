import { useState } from 'react'

const NAV_ITEMS = [
  { id: 'dashboard', name: 'Dashboard' },
  { id: 'ingredients', name: 'Ingredients' },
  { id: 'suppliers', name: 'Suppliers' },
  { id: 'procurement', name: 'Procurement' },
]

const buttonStyle = {
  width: '100%',
  textAlign: 'left',
  border: '1px solid #e5e7eb',
  background: '#fff',
  borderRadius: 8,
  padding: '0.6rem 0.8rem',
  cursor: 'pointer',
}

function Layout({ children, currentPage, onPageChange }) {
  const [open, setOpen] = useState(false)

  return (
    <div style={{ minHeight: '100vh', display: 'flex' }}>
      <aside style={{ width: open ? 220 : 76, background: '#ffffff', borderRight: '1px solid #e5e7eb', padding: 12, transition: 'all .2s ease' }}>
        <button onClick={() => setOpen((prev) => !prev)} style={{ ...buttonStyle, marginBottom: 10 }}>{open ? 'Close' : 'Menu'}</button>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            style={{
              ...buttonStyle,
              marginBottom: 8,
              background: currentPage === item.id ? '#dcfce7' : '#fff',
              fontWeight: currentPage === item.id ? 600 : 400,
            }}
            title={item.name}
          >
            {open ? item.name : item.name.slice(0, 1)}
          </button>
        ))}
      </aside>
      <main style={{ flex: 1, padding: '1rem 1.25rem' }}>
        <header style={{ marginBottom: '1rem' }}>
          <h1 style={{ margin: 0, textTransform: 'capitalize' }}>SkinSource Pro · {currentPage}</h1>
        </header>
        {children}
      </main>
    </div>
  )
}

export default Layout
