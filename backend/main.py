import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno
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

# ESTA ES LA RUTA QUE FALTABA (Para que el puerto 5000 no de 404)
@app.route('/')
def home():
    return jsonify({"mensaje": "API de Tienda UVG funcionando correctamente"}), 200

# 1. CONSULTA CON JOIN
@app.route('/api/reporte/join', methods=['GET'])
def reporte_join():
    conn = get_db_connection()
    cur = conn.cursor()
    query = '''
        SELECT p.nombre_producto, c.nombre_categoria, prov.nombre_empresa, p.stock_actual
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN proveedores prov ON p.id_proveedor = prov.id_proveedor
        LIMIT 10;
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"Producto": r[0], "Categoría": r[1], "Proveedor": r[2], "Stock": r[3]} for r in rows])

# 2. CONSULTA CON SUBQUERY
@app.route('/api/reporte/subquery', methods=['GET'])
def reporte_subquery():
    conn = get_db_connection()
    cur = conn.cursor()
    query = '''
        SELECT nombre_cliente, correo
        FROM clientes
        WHERE id_cliente IN (
            SELECT id_cliente FROM ventas WHERE total_venta > (SELECT AVG(total_venta) FROM ventas)
        );
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"Cliente": r[0], "Email": r[1]} for r in rows])

# 3. GROUP BY, HAVING y Agregación
@app.route('/api/reporte/group', methods=['GET'])
def reporte_group():
    conn = get_db_connection()
    cur = conn.cursor()
    query = '''
        SELECT e.nombre_empleado, COUNT(v.id_venta) as total_ventas, SUM(v.total_venta) as monto_total
        FROM empleados e
        JOIN ventas v ON e.id_empleado = v.id_empleado
        GROUP BY e.nombre_empleado
        HAVING SUM(v.total_venta) > 0;
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"Empleado": r[0], "Cant. Ventas": r[1], "Total Q": r[2]} for r in rows])

# 4. CTE (WITH)
@app.route('/api/reporte/cte', methods=['GET'])
def reporte_cte():
    conn = get_db_connection()
    cur = conn.cursor()
    query = '''
        WITH resumen_ventas AS (
            SELECT id_producto, SUM(cantidad_venta) as total_vendido
            FROM detalle_ventas
            GROUP BY id_producto
        )
        SELECT p.nombre_producto, rv.total_vendido
        FROM productos p
        JOIN resumen_ventas rv ON p.id_producto = rv.id_producto
        ORDER BY rv.total_vendido DESC LIMIT 5;
    '''
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"Producto": r[0], "Vendidos": r[1]} for r in rows])

# 5. VIEW
@app.route('/api/reporte/view', methods=['GET'])
def reporte_view():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE OR REPLACE VIEW vista_stock_bajo AS
        SELECT nombre_producto, stock_actual FROM productos WHERE stock_actual < 50;
    ''')
    conn.commit()
    cur.execute('SELECT * FROM vista_stock_bajo;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"Producto": r[0], "Stock Crítico": r[1]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)