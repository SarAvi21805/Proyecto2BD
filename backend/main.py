import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )

# --- TRANSACCIÓN CON ROLLBACK ---
@app.route('/api/transaccion_venta', methods=['POST'])
def transaccion_venta():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('BEGIN;')
        id_p = int(data['id_producto'])
        cant = int(data['cantidad'])
        
        cur.execute('SELECT stock_actual, precio_venta FROM productos WHERE id_producto = %s', (id_p,))
        res = cur.fetchone()
        if not res: raise Exception("Producto no existe")
        if res[0] < cant: raise Exception(f"Stock insuficiente (Solo hay {res[0]})")

        total = float(res[1]) * cant
        cur.execute('INSERT INTO ventas (total_venta, id_cliente, id_empleado) VALUES (%s, 1, 1) RETURNING id_venta', (total,))
        id_v = cur.fetchone()[0]
        cur.execute('INSERT INTO detalle_ventas (cantidad_venta, precio_unitario_venta, subtotal, id_venta, id_producto) VALUES (%s, %s, %s, %s, %s)',
                    (cant, res[1], total, id_v, id_p))
        cur.execute('UPDATE productos SET stock_actual = stock_actual - %s WHERE id_producto = %s', (cant, id_p))
        
        conn.commit()
        return jsonify({"message": "✅ Venta realizada (COMMIT)"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close(); conn.close()

# --- CRUD PRODUCTOS ---
@app.route('/api/productos', methods=['GET', 'POST'])
def crud_productos():
    conn = get_db_connection(); cur = conn.cursor()
    if request.method == 'GET':
        cur.execute('SELECT id_producto, nombre_producto, stock_actual, precio_venta FROM productos ORDER BY id_producto DESC LIMIT 10;')
        prods = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"id": p[0], "nombre": p[1], "stock": p[2], "precio": p[3]} for p in prods])
    if request.method == 'POST':
        d = request.json
        try:
            cur.execute('INSERT INTO productos (nombre_producto, precio_costo, precio_venta, stock_actual, id_categoria, id_proveedor) VALUES (%s, %s, %s, %s, 1, 1)',
                        (d['nombre'], d['precio'], d['precio'], d['stock']))
            conn.commit()
            return jsonify({"message": "Producto guardado"}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            cur.close(); conn.close()

# --- CRUD CLIENTES ---
@app.route('/api/clientes', methods=['GET', 'POST'])
def crud_clientes():
    conn = get_db_connection(); cur = conn.cursor()
    if request.method == 'GET':
        cur.execute('SELECT id_cliente, nombre_cliente, nit_fiscal, correo FROM clientes ORDER BY id_cliente DESC LIMIT 10;')
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"id": r[0], "nombre": r[1], "nit": r[2], "correo": r[3]} for r in rows])
    if request.method == 'POST':
        d = request.json
        try:
            cur.execute('INSERT INTO clientes (nombre_cliente, nit_fiscal, correo) VALUES (%s, %s, %s)', (d['nombre'], d['nit'], d['correo']))
            conn.commit()
            return jsonify({"message": "Cliente creado"}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"error": "Error: " + str(e)}), 400
        finally:
            cur.close(); conn.close()

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def del_cli(id):
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute('DELETE FROM clientes WHERE id_cliente = %s', (id,))
        conn.commit()
        return jsonify({"message": "Cliente eliminado"}), 200
    except:
        conn.rollback()
        return jsonify({"error": "No se puede eliminar (tiene historial)"}), 400
    finally:
        cur.close(); conn.close()

# --- REPORTES (JOIN, SUBQUERY, GROUP BY, CTE, VIEW) ---
@app.route('/api/reporte/<tipo>')
def reportes(tipo):
    conn = get_db_connection(); cur = conn.cursor()
    queries = {
        'join': 'SELECT p.id_producto, p.nombre_producto, c.nombre_categoria, p.stock_actual FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria ORDER BY p.id_product ASC LIMIT 10',
        'subquery': 'SELECT nombre_cliente FROM clientes WHERE id_cliente IN (SELECT id_cliente FROM ventas WHERE total_venta > (SELECT AVG(total_venta) FROM ventas))',
        'group': 'SELECT puesto, COUNT(*) FROM empleados GROUP BY puesto',
        'cte': 'WITH v AS (SELECT id_producto, SUM(cantidad_venta) as t FROM detalle_ventas GROUP BY id_producto) SELECT p.nombre_producto, v.t FROM productos p JOIN v ON p.id_producto = v.id_producto ORDER BY v.t DESC LIMIT 5',
        'view': 'SELECT * FROM vista_stock_bajo'
    }
    try:
        if tipo == 'view': cur.execute('CREATE OR REPLACE VIEW vista_stock_bajo AS SELECT nombre_producto, stock_actual FROM productos WHERE stock_actual < 50; COMMIT;')
        cur.execute(queries[tipo])
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return jsonify([dict(zip(cols, row)) for row in rows])
    finally:
        cur.close(); conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)