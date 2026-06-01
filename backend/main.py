import os
import datetime
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import jwt

from models import Cliente, Producto, Categoria

load_dotenv()
app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv('JWT_SECRET', 'secretjwt')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 120

DB_ROLE_MAP = {
    'ventas': 'rol_ventas',
    'inventario': 'rol_inventario',
    'clientes': 'rol_clientes',
    'reportes': 'rol_reportes',
    'gerente': 'rol_gerente',
}


def get_database_url():
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

engine = create_engine(get_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def map_db_error(error):
    message = str(error)
    if hasattr(error, 'orig'):
        message = str(error.orig)
    return message


def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload.update({'exp': expire})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception('Token expirado')
    except jwt.InvalidTokenError:
        raise Exception('Token inválido')


def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise Exception('No autorizado')

    token = auth_header.split(' ', 1)[1].strip()
    payload = decode_token(token)
    if 'usuario' not in payload or 'rol_app' not in payload:
        raise Exception('Token mal formado')
    return payload


def set_db_role(executor, role_name):
    db_role = DB_ROLE_MAP.get(role_name)
    if not db_role:
        raise Exception('Rol de aplicación no mapeado a DB')
    executor.execute(text(f'SET ROLE {db_role}'))


def requires_roles(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                user = get_current_user()
            except Exception as error:
                return jsonify({'error': str(error)}), 401

            if allowed_roles and user.get('rol_app') not in allowed_roles:
                return jsonify({'error': 'No tiene permisos para ejecutar esta acción'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('usuario')
    password = data.get('contrasena')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña son obligatorios'}), 400

    with SessionLocal() as session:
        result = session.execute(
            text(
                'SELECT id_empleado, usuario, puesto, rol_app FROM empleados '
                'WHERE usuario = :usuario AND contrasena = :contrasena'
            ),
            {'usuario': username, 'contrasena': password},
        )
        row = result.first()

        if not row:
            return jsonify({'error': 'Credenciales incorrectas'}), 401

        user_data = {
            'id_empleado': row.id_empleado,
            'usuario': row.usuario,
            'puesto': row.puesto,
            'rol_app': row.rol_app,
        }
        token = create_access_token(user_data)
        return jsonify({'message': 'Inicio de sesión exitoso', 'access_token': token, 'user': user_data})


@app.route('/api/auth/me')
def profile():
    try:
        user = get_current_user()
        return jsonify({'user': user})
    except Exception as error:
        return jsonify({'error': str(error)}), 401


# --- TRANSACCIÓN CON ROLLBACK ---
@app.route('/api/transaccion_venta', methods=['POST'])
@requires_roles('ventas', 'gerente')
def transaccion_venta():
    user = get_current_user()
    data = request.json or {}
    id_p = int(data.get('id_producto', 0))
    cant = int(data.get('cantidad', 0))
    id_cliente = int(data.get('id_cliente', 1))

    try:
        with engine.connect() as conn:
            db_role = DB_ROLE_MAP.get(user.get('rol_app'))
            if not db_role:
                raise Exception('Rol de aplicación no mapeado a DB')

            with conn.begin():
                conn.execute(text(f'SET ROLE {db_role}'))
                conn.execute(
                    text('CALL sp_registrar_venta_proc(:id_cliente, :id_empleado, :id_producto, :cantidad)'),
                    {
                        'id_cliente': id_cliente,
                        'id_empleado': user.get('id_empleado'),
                        'id_producto': id_p,
                        'cantidad': cant,
                    },
                )
                result = conn.execute(
                    text("SELECT currval(pg_get_serial_sequence('ventas','id_venta'))")
                )
                id_venta = result.scalar_one()
                conn.execute(text('RESET ROLE'))

        return jsonify({'message': '✅ Venta realizada (COMMIT) vía procedimiento', 'id_venta': id_venta}), 201
    except Exception as error:
        return jsonify({'error': str(error)}), 400


# --- CRUD PRODUCTOS ---
@app.route('/api/productos', methods=['GET', 'POST'])
@requires_roles('ventas', 'inventario', 'reportes', 'gerente')
def crud_productos():
    user = get_current_user()
    if request.method == 'GET':
        with SessionLocal() as session:
            set_db_role(session, user.get('rol_app'))
            rows = (
                session.query(
                    Producto.id_producto,
                    Producto.nombre_producto,
                    Producto.stock_actual,
                    Producto.precio_venta,
                    Categoria.nombre_categoria,
                )
                .join(Categoria, Producto.id_categoria == Categoria.id_categoria)
                .order_by(Producto.id_producto.desc())
                .limit(10)
                .all()
            )

            return jsonify(
                [
                    {
                        'id': row.id_producto,
                        'nombre': row.nombre_producto,
                        'stock': row.stock_actual,
                        'precio': float(row.precio_venta),
                        'categoria': row.nombre_categoria,
                    }
                    for row in rows
                ]
            )

    if user.get('rol_app') not in ('inventario', 'gerente'):
        return jsonify({'error': 'No tiene permisos para crear productos'}), 403

    data = request.json or {}
    with SessionLocal() as session:
        try:
            set_db_role(session, user.get('rol_app'))
            with session.begin():
                session.execute(
                    text(
                        'SELECT fn_crear_producto(:nombre, :precio_costo, :precio_venta, :stock, :id_categoria, :id_proveedor)'
                    ),
                    {
                        'nombre': data.get('nombre'),
                        'precio_costo': float(data.get('precio', 0)),
                        'precio_venta': float(data.get('precio', 0)),
                        'stock': int(data.get('stock', 0)),
                        'id_categoria': 1,
                        'id_proveedor': 1,
                    },
                )
            return jsonify({'message': 'Producto guardado'}), 201
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400


# --- CRUD CLIENTES ---
@app.route('/api/clientes', methods=['GET', 'POST'])
@requires_roles('clientes', 'ventas', 'reportes', 'gerente')
def crud_clientes():
    user = get_current_user()

    if request.method == 'GET':
        with SessionLocal() as session:
            set_db_role(session, user.get('rol_app'))
            rows = (
                session.query(Cliente)
                .order_by(Cliente.id_cliente.desc())
                .limit(10)
                .all()
            )
            return jsonify(
                [
                    {
                        'id': cliente.id_cliente,
                        'nombre': cliente.nombre_cliente,
                        'nit': cliente.nit_fiscal,
                        'correo': cliente.correo,
                    }
                    for cliente in rows
                ]
            )

    if user.get('rol_app') not in ('clientes', 'ventas', 'gerente'):
        return jsonify({'error': 'No tiene permisos para registrar clientes'}), 403

    data = request.json or {}
    with SessionLocal() as session:
        try:
            set_db_role(session, user.get('rol_app'))
            with session.begin():
                session.execute(
                    text('SELECT fn_crear_cliente(:nombre, :nit, :correo)'),
                    {
                        'nombre': data.get('nombre'),
                        'nit': data.get('nit'),
                        'correo': data.get('correo'),
                    },
                )
            return jsonify({'message': 'Cliente creado'}), 201
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400


@app.route('/api/clientes/<int:id>', methods=['DELETE'])
@requires_roles('clientes', 'gerente')
def del_cli(id):
    user = get_current_user()
    with SessionLocal() as session:
        try:
            set_db_role(session, user.get('rol_app'))
            cliente = session.get(Cliente, id)
            if not cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404

            session.delete(cliente)
            session.commit()
            return jsonify({'message': 'Cliente eliminado'}), 200
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400
        except Exception as error:
            return jsonify({'error': str(error)}), 400


@app.route('/api/clientes/info/<int:id>')
@requires_roles('clientes', 'ventas', 'reportes', 'gerente')
def cliente_info(id):
    user = get_current_user()
    with SessionLocal() as session:
        try:
            set_db_role(session, user.get('rol_app'))
            result = session.execute(
                text('SELECT * FROM fn_obtener_cliente_info(:id)'),
                {'id': id},
            )
            row = result.first()
            if not row:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            return jsonify({'id': id, 'nombre': row.nombre, 'nit': row.nit}), 200
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400
        except Exception as error:
            return jsonify({'error': str(error)}), 400


# --- REPORTES (JOIN, SUBQUERY, GROUP BY, CTE, VIEW) ---
@app.route('/api/reporte/<tipo>')
@requires_roles('reportes', 'inventario', 'ventas', 'gerente')
def reportes(tipo):
    queries = {
        'join': 'SELECT p.id_producto, p.nombre_producto, c.nombre_categoria, p.stock_actual FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria ORDER BY p.id_producto ASC LIMIT 10',
        'subquery': 'SELECT nombre_cliente FROM clientes WHERE id_cliente IN (SELECT id_cliente FROM ventas WHERE total_venta > (SELECT AVG(total_venta) FROM ventas))',
        'group': 'SELECT puesto, COUNT(*) FROM empleados GROUP BY puesto',
        'cte': 'WITH v AS (SELECT id_producto, SUM(cantidad_venta) as t FROM detalle_ventas GROUP BY id_producto) SELECT p.nombre_producto, v.t FROM productos p JOIN v ON p.id_producto = v.id_producto ORDER BY v.t DESC LIMIT 5',
        'view': 'SELECT * FROM vista_stock_bajo',
        'stock': 'SELECT * FROM fn_reporte_stock_bajo()'
    }

    with SessionLocal() as session:
        try:
            set_db_role(session, get_current_user().get('rol_app'))
            if tipo == 'view':
                with session.begin():
                    session.execute(
                        text('CREATE OR REPLACE VIEW vista_stock_bajo AS SELECT nombre_producto, stock_actual FROM productos WHERE stock_actual < 50')
                    )

            result = session.execute(text(queries[tipo]))
            rows = result.fetchall()
            cols = result.keys()
            return jsonify([dict(zip(cols, row)) for row in rows])
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400
        except KeyError:
            return jsonify({'error': 'Tipo de reporte desconocido'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)