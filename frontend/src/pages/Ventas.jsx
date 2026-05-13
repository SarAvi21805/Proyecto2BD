import React, { useReducer, useState } from 'react';
import { ShoppingCart, Plus, Trash2, CheckCircle } from 'lucide-react';

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

  return (
    <div style={{ maxWidth: '600px' }}>
      <h1>🛒 Punto de Venta 🛒</h1>
      
      <div className="card">
        <h3>Agregar al Carrito</h3>
        <input type="number" placeholder="ID Producto" value={item.id} onChange={e => setItem({...item, id: e.target.value})} className="input-style" />
        <input type="number" placeholder="Cantidad" value={item.cant} onChange={e => setItem({...item, cant: e.target.value})} className="input-style" />
        <button onClick={() => { dispatch({type:'ADD', payload:item}); setItem({id:'', cant:''}); }} className="btn-add">
          <Plus size={16}/> Añadir
        </button>
      </div>

      <div className="card">
        <h3>Resumen ({cart.length})</h3>
        {cart.length === 0 ? <p>Carrito vacío</p> : (
          <ul>
            {cart.map((c, i) => (
              <li key={i} className="cart-item">
                Producto #{c.id} - Cant: {c.cant}
                <Trash2 size={16} onClick={() => dispatch({type:'REMOVE', payload:i})} style={{cursor:'pointer', color:'red'}}/>
              </li>
            ))}
          </ul>
        )}
        {cart.length > 0 && <button className="btn-confirm" onClick={() => alert("Venta confirmada")}>Confirmar Venta</button>}
      </div>
    </div>
  );
};