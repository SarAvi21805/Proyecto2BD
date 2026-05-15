import React, { useState } from 'react';
import api from '../api';
import { UserPlus, AlertTriangle, CheckCircle } from 'lucide-react';

export const Clientes = () => {
  // Estado controlado
  const [formData, setFormData] = useState({
    nombre: '',
    nit: '',
    correo: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Manejador de cambio
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError(''); // Limpiar error mientras escribe
  };

  // Validación del lado del cliente
  const validar = () => {
    if (!formData.nombre || !formData.nit || !formData.correo) return "Todos los campos son obligatorios";
    if (formData.nit.length < 4) return "El NIT es demasiado corto";
    if (!formData.correo.includes('@')) return "Correo electrónico no válido";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errorValidacion = validar();
    if (errorValidacion) return setError(errorValidacion);

    try {
      await api.post('/clientes', {
        nombre: formData.nombre,
        nit: formData.nit,
        correo: formData.correo
      });
      setSuccess(true);
      setFormData({ nombre: '', nit: '', correo: '' }); // Limpiar formulario
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError("Error: El NIT ya podría existir en el sistema.");
    }
  };

  return (
    <div style={{ maxWidth: '500px' }}>
      <h1>👥 Registro de Clientes</h1>
      <div style={cardStyle}>
        <form onSubmit={handleSubmit}>
          <div style={inputGroup}>
            <label>Nombre Completo:</label>
            <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} style={inputStyle} placeholder="Ej. Juan Perez" />
          </div>

          <div style={inputGroup}>
            <label>NIT / ID Fiscal:</label>
            <input type="text" name="nit" value={formData.nit} onChange={handleChange} style={inputStyle} placeholder="Ej. 123456-K" />
          </div>

          <div style={inputGroup}>
            <label>Correo:</label>
            <input type="email" name="correo" value={formData.correo} onChange={handleChange} style={inputStyle} placeholder="ejemplo@correo.com" />
          </div>

          {error && <div style={errorBox}><AlertTriangle size={16}/> {error}</div>}
          {success && <div style={successBox}><CheckCircle size={16}/> ¡Cliente guardado con éxito!</div>}

          <button type="submit" style={btnStyle}>
            <UserPlus size={18} /> Registrar Cliente
          </button>
        </form>
      </div>
    </div>
  );
};

// Estilos
const cardStyle = { background: 'white', padding: '30px', borderRadius: '15px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' };
const inputGroup = { marginBottom: '15px', display: 'flex', flexDirection: 'column', gap: '5px' };
const inputStyle = { padding: '12px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem' };
const btnStyle = { width: '100%', padding: '12px', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' };
const errorBox = { padding: '10px', background: '#fff0f0', color: '#d93025', borderRadius: '5px', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' };
const successBox = { padding: '10px', background: '#e6fffa', color: '#00875a', borderRadius: '5px', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' };