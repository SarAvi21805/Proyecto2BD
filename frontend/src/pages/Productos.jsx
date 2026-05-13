import React, { useState, useEffect } from 'react';
import api from '../api';
import { Package, RefreshCw, AlertCircle } from 'lucide-react';

export const Productos = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProductos = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reporte/join');
      setProductos(response.data);
      setError(null);
    } catch (err) {
      setError('No se pudieron cargar los productos. ¿Está el backend encendido?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  if (loading) return <div style={msgStyle}><RefreshCw className="spin" /> Cargando inventario...</div>;
  if (error) return <div style={{...msgStyle, color: 'red'}}><AlertCircle /> {error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          📦 Inventario de Productos 📦
        </h1>
        <button onClick={fetchProductos} style={btnStyle}>
          <RefreshCw size={16} /> Actualizar
        </button>
      </div>

      <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={tableStyle}>
          <thead>
            <tr style={{ background: '#f8f9fa' }}>
              <th style={thStyle}>Producto</th>
              <th style={thStyle}>Categoría</th>
              <th style={thStyle}>Stock</th>
            </tr>
          </thead>
          <tbody>
            {productos.map((p, index) => (
              <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                <td>{p.nombre_producto}</td>
                <td>{p.nombre_categoria}</td>
                <td style={{ fontWeight: 'bold', color: p.stock_actual < 50 ? '#dc3545' : '#28a745' }}>
                  {p.stock_actual}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Estilos
const tableStyle = { width: '100%', borderCollapse: 'collapse' };
const thStyle = { padding: '15px', textAlign: 'left', borderBottom: '2px solid #dee2e6', color: '#495057' };
const tdStyle = { padding: '12px 15px', color: '#212529' };
const msgStyle = { display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', marginTop: '50px', fontSize: '1.2rem' };
const btnStyle = { 
  display: 'flex', alignItems: 'center', gap: '8px',
  padding: '10px 20px', background: '#007bff', color: 'white', 
  border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: '600' 
};