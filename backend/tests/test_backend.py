import os
import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from main import app, create_access_token, decode_token, requires_roles


def test_jwt_encode_decode():
    token = create_access_token({'usuario': 'user1', 'rol_app': 'ventas'})
    payload = decode_token(token)
    assert payload['usuario'] == 'user1'
    assert payload['rol_app'] == 'ventas'


def test_schema_contains_roles_and_procedures():
    schema_path = ROOT.parent / 'database' / 'schema.sql'
    content = schema_path.read_text(encoding='utf-8')

    assert 'CREATE ROLE rol_ventas' in content
    assert 'CREATE ROLE rol_inventario' in content
    assert 'CREATE ROLE rol_clientes' in content
    assert 'CREATE ROLE rol_reportes' in content
    assert 'CREATE OR REPLACE FUNCTION fn_registrar_venta' in content
    assert 'CREATE OR REPLACE FUNCTION fn_crear_cliente' in content
    assert 'CREATE OR REPLACE FUNCTION fn_crear_producto' in content
    assert 'GRANT EXECUTE ON FUNCTION fn_registrar_venta' in content


def test_requires_roles_blocks_wrong_role(monkeypatch):
    def fake_current_user():
        return {'usuario': 'user1', 'rol_app': 'clientes'}

    monkeypatch.setattr('main.get_current_user', fake_current_user)

    @requires_roles('ventas')
    def secret():
        return 'ok'

    resp = secret()
    assert isinstance(resp, tuple)
    assert resp[1] == 403
    assert 'permisos' in resp[0].json['error']


def test_login_endpoint_success(monkeypatch):
    class DummyResult:
        def first(self):
            return SimpleNamespace(id_empleado=1, usuario='user1', puesto='Ventas', rol_app='ventas')

    class DummySession:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def execute(self, query, params):
            return DummyResult()

    monkeypatch.setattr('main.SessionLocal', lambda: DummySession())

    client = app.test_client()
    response = client.post('/api/auth/login', json={'usuario': 'user1', 'contrasena': '1234'})
    assert response.status_code == 200
    assert response.json['user']['usuario'] == 'user1'
    assert 'access_token' in response.json
