import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from models import Cliente, Producto, Categoria

load_dotenv()
app = Flask(__name__)
CORS(app)


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


# --- TRANSACCIÓN CON ROLLBACK ---
@app.route('/api/transaccion_venta', methods=['POST'])
def transaccion_venta():
    data = request.json or {}
    id_p = int(data.get('id_producto', 0))
    cant = int(data.get('cantidad', 0))

    with SessionLocal() as session:
        try:
            with session.begin():
                result = session.execute(
                    text(
                        'SELECT fn_registrar_venta(:id_cliente, :id_empleado, :id_producto, :cantidad)'
                    ),
                    {
                        'id_cliente': 1,
                        'id_empleado': 1,
                        'id_producto': id_p,
                        'cantidad': cant,
                    },
                )
                id_venta = result.scalar_one()

            return jsonify({'message': '✅ Venta realizada (COMMIT)', 'id_venta': id_venta}), 201
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400


# --- CRUD PRODUCTOS ---
@app.route('/api/productos', methods=['GET', 'POST'])
def crud_productos():
    if request.method == 'GET':
        with SessionLocal() as session:
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

    data = request.json or {}
    with SessionLocal() as session:
        try:
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
def crud_clientes():
    if request.method == 'GET':
        with SessionLocal() as session:
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

    data = request.json or {}
    with SessionLocal() as session:
        try:
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
def del_cli(id):
    with SessionLocal() as session:
        try:
            with session.begin():
                result = session.execute(
                    text('DELETE FROM clientes WHERE id_cliente = :id'),
                    {'id': id},
                )
                if result.rowcount == 0:
                    raise Exception('Cliente no encontrado')
            return jsonify({'message': 'Cliente eliminado'}), 200
        except SQLAlchemyError as error:
            return jsonify({'error': map_db_error(error)}), 400
        except Exception as error:
            return jsonify({'error': str(error)}), 400


# --- REPORTES (JOIN, SUBQUERY, GROUP BY, CTE, VIEW) ---
@app.route('/api/reporte/<tipo>')
def reportes(tipo):
    queries = {
        'join': 'SELECT p.id_producto, p.nombre_producto, c.nombre_categoria, p.stock_actual FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria ORDER BY p.id_producto ASC LIMIT 10',
        'subquery': 'SELECT nombre_cliente FROM clientes WHERE id_cliente IN (SELECT id_cliente FROM ventas WHERE total_venta > (SELECT AVG(total_venta) FROM ventas))',
        'group': 'SELECT puesto, COUNT(*) FROM empleados GROUP BY puesto',
        'cte': 'WITH v AS (SELECT id_producto, SUM(cantidad_venta) as t FROM detalle_ventas GROUP BY id_producto) SELECT p.nombre_producto, v.t FROM productos p JOIN v ON p.id_producto = v.id_producto ORDER BY v.t DESC LIMIT 5',
        'view': 'SELECT * FROM vista_stock_bajo'
    }

    with SessionLocal() as session:
        try:
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