import React, { useReducer, useState } from 'react';
import api from '../api';
import { ShoppingCart, Plus, Trash2, CheckCircle, AlertCircle } from 'lucide-react';

// Maneja el estado complejo del carrito
const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD': return [...state, action.payload];
    case 'REMOVE': return state.filter((_, i) => i !== action.payload);
    case 'CLEAR': return [];
    default: return state;
  }
};

export const Ventas = () => {
  const [cart, dispatch] = useReducer(cartReducer, []);
  const [item, setItem] = useState({ id: '', cant: '' });
  const [loading, setLoading] = useState(false);

  const handleConfirmSale = async () => {
      if (cart.length === 0) return;
      setLoading(true);
      try {
        // Enviamos el primer producto del carrito a la transacción de la fase de BD
        const saleData = {
          id_producto: cart[0].id,
          cantidad: cart[0].cant
        };

        const response = await api.post('/transaccion_venta', saleData);
        
        alert("✅ " + response.data.message);
        dispatch({ type: 'CLEAR' }); // Limpieza del carrito
      } catch (error) {
        alert("❌ Error: " + (error.response?.data?.error || "Fallo en la transacción"));
      } finally {
        setLoading(false);
      }
    };

  return (
    <div style={{ maxWidth: '800px' }}>
      <h1 style={{ color: '#333' }}>🛒 Punto de Venta 🛒</h1>
      
      <div style={cardStyle}>
        <h3 style={{ color: '#007bff', marginTop: 0 }}>Agregar al Carrito</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input type="number" placeholder="ID Producto" value={item.id} 
            onChange={e => setItem({...item, id: e.target.value})} style={inputStyle} />
          <input type="number" placeholder="Cantidad" value={item.cant} 
            onChange={e => setItem({...item, cant: e.target.value})} style={inputStyle} />
          <button onClick={() => { dispatch({type:'ADD', payload:item}); setItem({id:'', cant:''}); }} 
            style={btnAddStyle}> <Plus size={18}/> Añadir </button>
        </div>
      </div>

      <div style={cardStyle}>
        <h3 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px' }}>
          Resumen de Compra ({cart.length} productos)
        </h3>
        {cart.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center' }}>El carrito está vacío</p>
        ) : (
          <>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {cart.map((c, i) => (
                <li key={i} style={itemStyle}>
                  <span><b>Producto #{c.id}</b> — Cantidad: {c.cant}</span>
                  <button onClick={() => dispatch({type:'REMOVE', payload:i})} style={btnDelStyle}>
                    <Trash2 size={18}/>
                  </button>
                </li>
              ))}
            </ul>
            <button 
              onClick={handleConfirmSale} 
              disabled={loading}
              style={{ ...btnConfirmStyle, opacity: loading ? 0.5 : 1 }}
            >
              {loading ? 'Procesando...' : <><CheckCircle size={20}/> Confirmar Venta </>}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

const agregarAlCarrito = () => {
  // Validación de datos a ingresar en los campos antes del carrito
  if (!item.id || !item.cant || isNaN(item.id) || isNaN(item.cant)) {
    return alert("Por favor ingresa IDs y cantidades numéricas válidas");
  }
  if (parseInt(item.cant) <= 0) {
    return alert("La cantidad debe ser mayor a cero");
  }

  dispatch({type:'ADD', payload:item}); 
  setItem({id:'', cant:''}); 
};

// Estilos
const cardStyle = { background: 'white', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', marginBottom: '25px' };
const inputStyle = { padding: '12px', border: '1px solid #ddd', borderRadius: '8px', flex: 1 };
const btnAddStyle = { display: 'flex', alignItems: 'center', gap: '5px', padding: '0 20px', background: '#28a745', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' };
const itemStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', borderBottom: '1px solid #f0f0f0' };
const btnDelStyle = { background: 'none', border: 'none', color: '#dc3545', cursor: 'pointer' };
const btnConfirmStyle = { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', width: '100%', padding: '15px', background: '#007bff', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold', marginTop: '20px', fontSize: '1rem' };