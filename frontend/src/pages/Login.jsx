import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, AlertCircle } from 'lucide-react';

export const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ usuario: '', contrasena: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.usuario || !form.contrasena) {
      setError('Usuario y contraseña son obligatorios');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/auth/login', form);
      login(response.data.user, response.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Error de inicio de sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '420px', margin: '0 auto', paddingTop: '100px' }}>
      <div style={{ background: 'white', borderRadius: '18px', padding: '35px', boxShadow: '0 18px 60px rgba(15, 23, 42, 0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <ShieldCheck size={32} color="#3b82f6" />
          <div>
            <h1 style={{ margin: 0 }}>Acceso de empleado</h1>
            <p style={{ margin: 0, color: '#6b7280' }}>Usa tu usuario para comenzar.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <label style={labelStyle}>Usuario</label>
          <input
            name="usuario"
            value={form.usuario}
            onChange={handleChange}
            placeholder="user1"
            style={inputStyle}
          />

          <label style={labelStyle}>Contraseña</label>
          <input
            type="password"
            name="contrasena"
            value={form.contrasena}
            onChange={handleChange}
            placeholder="1234"
            style={inputStyle}
          />

          {error && <div style={errorStyle}><AlertCircle size={16} /> {error}</div>}

          <button type="submit" style={buttonStyle} disabled={loading}>
            {loading ? 'Validando...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </div>
  );
};

const labelStyle = { display: 'block', marginBottom: '8px', color: '#374151', fontWeight: '600' };
const inputStyle = { width: '100%', padding: '12px 14px', borderRadius: '10px', border: '1px solid #d1d5db', marginBottom: '18px', fontSize: '1rem' };
const buttonStyle = { width: '100%', padding: '14px', borderRadius: '12px', background: '#2563eb', color: 'white', border: 'none', cursor: 'pointer', fontWeight: '700' };
const errorStyle = { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px', padding: '12px', background: '#fee2e2', color: '#b91c1c', borderRadius: '10px' };
