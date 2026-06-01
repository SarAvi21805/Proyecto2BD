import { useAuth } from '../context/AuthContext';

export const Home = () => {
  const { user } = useAuth();
  return (
    <div>
      <h1>🏠 Inicio</h1>
      <p>Bienvenido al sistema de gestión de Tienda UVG.</p>
      {user && (
        <div style={{ marginTop: '20px', padding: '18px', background: 'white', borderRadius: '14px', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)' }}>
          <h2 style={{ marginTop: 0 }}>Usuario conectado</h2>
          <p><strong>Empleado:</strong> {user.usuario}</p>
          <p><strong>Rol:</strong> {user.rol_app}</p>
          <p style={{ color: '#4b5563' }}>Usa el menú izquierdo para navegar a las funciones autorizadas a tu rol.</p>
        </div>
      )}
    </div>
  );
};