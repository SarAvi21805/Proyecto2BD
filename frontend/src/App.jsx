import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Productos } from './pages/Productos';
import { Clientes } from './pages/Clientes';
import { Ventas } from './pages/Ventas';
import { Login } from './pages/Login';
import { NotAuthorized } from './pages/NotAuthorized';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LayoutDashboard, Package, Users, ShoppingCart, LogOut } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Inicio', rol: ['ventas', 'inventario', 'clientes', 'reportes', 'gerente'], icon: <LayoutDashboard size={18} /> },
  { to: '/productos', label: 'Productos', rol: ['ventas', 'inventario', 'reportes', 'gerente'], icon: <Package size={18} /> },
  { to: '/clientes', label: 'Clientes', rol: ['clientes', 'ventas', 'reportes', 'gerente'], icon: <Users size={18} /> },
  { to: '/ventas', label: 'Ventas', rol: ['ventas', 'gerente'], icon: <ShoppingCart size={18} /> },
];

const PrivateRoute = ({ children, roles }) => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.rol_app)) return <NotAuthorized />;
  return children;
};

function AppContent() {
  const { user, logout } = useAuth();

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        {user ? (
          <nav style={{ width: '250px', background: '#111827', color: 'white', padding: '20px' }}>
            <h2>UVG Store</h2>
            <p style={{ color: '#9ca3af', marginBottom: '24px' }}>
              <strong>Usuario:</strong> {user.usuario}
              <br />
              <strong>Rol:</strong> {user.rol_app}
            </p>
            <hr style={{ borderColor: '#374151', marginBottom: '20px' }} />
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {navItems.map((item) =>
                item.rol.includes(user.rol_app) ? (
                  <li key={item.to} style={liStyle}>
                    <Link to={item.to} style={linkStyle}>{item.icon} {item.label}</Link>
                  </li>
                ) : null
              )}
            </ul>
            <button onClick={logout} style={logoutStyle}>
              <LogOut size={16} /> Cerrar sesión
            </button>
          </nav>
        ) : null}

        <main style={{ flex: 1, padding: '30px', background: '#f3f4f6' }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <PrivateRoute roles={['ventas', 'inventario', 'clientes', 'reportes', 'gerente']}>
                <Home />
              </PrivateRoute>
            } />
            <Route path="/productos" element={
              <PrivateRoute roles={['ventas', 'inventario', 'reportes', 'gerente']}>
                <Productos />
              </PrivateRoute>
            } />
            <Route path="/clientes" element={
              <PrivateRoute roles={['clientes', 'ventas', 'reportes', 'gerente']}>
                <Clientes />
              </PrivateRoute>
            } />
            <Route path="/ventas" element={
              <PrivateRoute roles={['ventas', 'gerente']}>
                <Ventas />
              </PrivateRoute>
            } />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

const liStyle = { marginBottom: '15px' };
const linkStyle = { color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' };
const logoutStyle = { marginTop: '20px', width: '100%', background: '#ef4444', border: 'none', color: 'white', padding: '12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' };

export default App;