-- 1. CATEGORíAS

INSERT INTO categorias (nombre_categoria, descripcion_categoria)
SELECT 
    'Categoria ' || i,
    'Descripcion de categoria ' || i
FROM generate_series(1,25) i;
	
-- 2. PROVEEDORES

INSERT INTO proveedores (nombre_empresa, contacto, telefono)
SELECT 
    'Proveedor ' || i,
    'contacto' || i || '@empresa.com',
    '555-' || LPAD(i::text,4,'0')
FROM generate_series(1,25) i;

-- 3. CLIENTES

INSERT INTO clientes (nombre_cliente, nit_fiscal, correo)
SELECT 
    'Cliente ' || i,
    'NIT' || LPAD(i::text,6,'0'),
    'cliente' || i || '@mail.com'
FROM generate_series(1,25) i;

-- 4. EMPLEADOS

INSERT INTO empleados (nombre_empleado, puesto, usuario, contrasena)
SELECT 
    'Empleado ' || i,
    CASE 
        WHEN i % 3 = 0 THEN 'Gerente'
        WHEN i % 3 = 1 THEN 'Ventas'
        ELSE 'Caja'
    END,
    'user' || i,
    '1234'
FROM generate_series(1,25) i;

-- 5. PRODUCTOS

INSERT INTO productos (
    nombre_producto, descripcion_producto, precio_costo, precio_venta, stock_actual, id_categoria, id_proveedor
)
SELECT
    'Producto ' || i,
    'Descripcion producto ' || i,
    (random()*50 + 10)::numeric(10,2),
    (random()*100 + 60)::numeric(10,2),
    (random()*200)::int,
    (i % 25) + 1,
    (i % 25) + 1
FROM generate_series(1,25) i;

-- 6. COMPRAS

INSERT INTO compras (fecha_compra, total_compra, id_proveedor)
SELECT 
    NOW() - (i || ' days')::interval,
    0,
    (i % 25) + 1
FROM generate_series(1,25) i;

-- 7. DETALLE_COMPRAS

INSERT INTO detalle_compras (
    cantidad_compra, precio_unitario_compra, subtotal_compra, id_compra, id_producto
)
SELECT
    (random()*10 + 1)::int,
    p.precio_costo,
    ((random()*10 + 1)::int * p.precio_costo),
    c.id_compra,
    p.id_producto
FROM compras c
JOIN productos p ON p.id_producto = ((c.id_compra % 25) + 1)
LIMIT 50;

-- 7.5. ACTUALIZAR TOTAL_COMPRAS

UPDATE compras c
SET total_compra = sub.total
FROM (
    SELECT id_compra, SUM(subtotal_compra) as total
    FROM detalle_compras
    GROUP BY id_compra
) sub
WHERE c.id_compra = sub.id_compra;

-- 8. VENTAS

INSERT INTO ventas (fecha_venta, total_venta, id_cliente, id_empleado)
SELECT 
    NOW() - (i || ' days')::interval,
    0,
    (i % 25) + 1,
    (i % 25) + 1
FROM generate_series(1,25) i;

-- 9. DETALLE_VENTAS

INSERT INTO detalle_ventas (
    cantidad_venta, precio_unitario_venta, subtotal, id_venta, id_producto
)
SELECT
    (random()*5 + 1)::int,
    p.precio_venta,
    ((random()*5 + 1)::int * p.precio_venta),
    v.id_venta,
    p.id_producto
FROM ventas v
JOIN productos p ON p.id_producto = ((v.id_venta % 25) + 1)
LIMIT 50;

-- 9.5. ACTUALIZAR TOTAL_VENTAS

UPDATE ventas v
SET total_venta = sub.total
FROM (
    SELECT id_venta, SUM(subtotal) as total
    FROM detalle_ventas
    GROUP BY id_venta
) sub
WHERE v.id_venta = sub.id_venta;