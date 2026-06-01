import React from 'react';
import { ShieldAlert } from 'lucide-react';

export const NotAuthorized = () => (
  <div style={{ textAlign: 'center', paddingTop: '80px' }}>
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '14px', background: '#fef9c3', border: '1px solid #facc15', borderRadius: '16px', padding: '20px 24px' }}>
      <ShieldAlert size={28} color="#b45309" />
      <div>
        <h2 style={{ margin: 0 }}>Acceso denegado</h2>
        <p style={{ margin: '8px 0 0', color: '#92400e' }}>No tienes el rol necesario para ver esta sección.</p>
      </div>
    </div>
  </div>
);
