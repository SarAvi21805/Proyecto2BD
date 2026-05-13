import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Home } from './pages/Home';
import { Productos } from './pages/Productos';
import { Clientes } from './pages/Clientes';
import { Ventas } from './pages/Ventas';
import { AuthProvider } from './context/AuthContext';
import { LayoutDashboard, Package, Users, ShoppingCart } from 'lucide-react';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          {/* Sidebar */}
          <nav style={{ width: '250px', background: '#1a1a1a', color: 'white', padding: '20px' }}>
            <h2>UVG Store</h2>
            <hr />
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={liStyle}><Link to="/" style={linkStyle}><LayoutDashboard size={18}/> Inicio</Link></li>
              <li style={liStyle}><Link to="/productos" style={linkStyle}><Package size={18}/> Productos</Link></li>
              <li style={liStyle}><Link to="/clientes" style={linkStyle}><Users size={18}/> Clientes</Link></li>
              <li style={liStyle}><Link to="/ventas" style={linkStyle}><ShoppingCart size={18}/> Ventas</Link></li>
            </ul>
          </nav>

          {/* Main Content */}
          <main style={{ flex: 1, padding: '30px', background: '#f9f9f9' }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/productos" element={<Productos />} />
              <Route path="/clientes" element={<Clientes />} />
              <Route path="/ventas" element={<Ventas />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

const liStyle = { marginBottom: '15px' };
const linkStyle = { color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' };

export default App;