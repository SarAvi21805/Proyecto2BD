-- 0. ROLES Y PERMISOS EN BASE DE DATOS
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_ventas') THEN
        CREATE ROLE rol_ventas NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_inventario') THEN
        CREATE ROLE rol_inventario NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_clientes') THEN
        CREATE ROLE rol_clientes NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_reportes') THEN
        CREATE ROLE rol_reportes NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_gerente') THEN
        CREATE ROLE rol_gerente NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'proy3') THEN
        CREATE ROLE proy3 LOGIN PASSWORD 'secret';
    ELSE
        ALTER ROLE proy3 WITH LOGIN PASSWORD 'secret';
    END IF;
END $$;

-- El usuario de aplicación hereda los roles de negocio.
GRANT rol_ventas, rol_inventario, rol_clientes, rol_reportes, rol_gerente TO proy3;

-- 1. TABLAS BASE (SIN FK)

CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL,
    descripcion_categoria TEXT
);

CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre_empresa VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(150) NOT NULL,
    nit_fiscal VARCHAR(20) UNIQUE NOT NULL,
    correo VARCHAR(100)
);

CREATE TABLE empleados (
    id_empleado SERIAL PRIMARY KEY,
    nombre_empleado VARCHAR(150) NOT NULL,
    puesto VARCHAR(100),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol_app VARCHAR(50) NOT NULL
);

-- 2. TABLAS DEPENDIENTES

CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    descripcion_producto TEXT,
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    id_categoria INT NOT NULL,
    id_proveedor INT NOT NULL,
    CONSTRAINT fk_producto_categoria 
        FOREIGN KEY(id_categoria) REFERENCES categorias(id_categoria),
    CONSTRAINT fk_producto_proveedor 
        FOREIGN KEY(id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE compras (
    id_compra SERIAL PRIMARY KEY,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_compra DECIMAL(10,2) NOT NULL,
    id_proveedor INT NOT NULL,
    CONSTRAINT fk_compra_proveedor 
        FOREIGN KEY(id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE ventas (
    id_venta SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(10,2) NOT NULL,
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    CONSTRAINT fk_venta_cliente 
        FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_venta_empleado 
        FOREIGN KEY(id_empleado) REFERENCES empleados(id_empleado)
);

-- 3. TABLAS DETALLE

CREATE TABLE detalle_compras (
    id_detalle_compra SERIAL PRIMARY KEY,
    cantidad_compra INT NOT NULL,
    precio_unitario_compra DECIMAL(10,2) NOT NULL,
    subtotal_compra DECIMAL(10,2) NOT NULL,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    CONSTRAINT fk_det_compra_compra 
        FOREIGN KEY(id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_det_compra_producto 
        FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE detalle_ventas (
    id_detalle_venta SERIAL PRIMARY KEY,
    cantidad_venta INT NOT NULL,
    precio_unitario_venta DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    CONSTRAINT fk_det_venta_venta 
        FOREIGN KEY(id_venta) REFERENCES ventas(id_venta),
    CONSTRAINT fk_det_venta_producto 
        FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
);

-- 4. PROCEDIMIENTOS ALMACENADOS

CREATE OR REPLACE FUNCTION fn_crear_cliente(
    p_nombre TEXT,
    p_nit TEXT,
    p_correo TEXT
) RETURNS INT AS $$
DECLARE
    v_id INT;
BEGIN
    INSERT INTO clientes (nombre_cliente, nit_fiscal, correo)
    VALUES (p_nombre, p_nit, p_correo)
    RETURNING id_cliente INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION fn_crear_producto(
    p_nombre TEXT,
    p_precio_costo NUMERIC,
    p_precio_venta NUMERIC,
    p_stock INT,
    p_id_categoria INT,
    p_id_proveedor INT
) RETURNS INT AS $$
DECLARE
    v_id INT;
BEGIN
    INSERT INTO productos (
        nombre_producto, precio_costo, precio_venta, stock_actual, id_categoria, id_proveedor
    ) VALUES (
        p_nombre, p_precio_costo, p_precio_venta, p_stock, p_id_categoria, p_id_proveedor
    ) RETURNING id_producto INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION fn_registrar_venta(
    p_id_cliente INT,
    p_id_empleado INT,
    p_id_producto INT,
    p_cantidad INT
) RETURNS INT AS $$
DECLARE
    v_stock INT;
    v_precio NUMERIC(10,2);
    v_total NUMERIC(10,2);
    v_id_venta INT;
BEGIN
    SELECT stock_actual, precio_venta INTO v_stock, v_precio
    FROM productos
    WHERE id_producto = p_id_producto;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no existe';
    END IF;

    IF v_stock < p_cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente (Solo hay %)', v_stock;
    END IF;

    v_total := v_precio * p_cantidad;

    INSERT INTO ventas (total_venta, id_cliente, id_empleado)
    VALUES (v_total, p_id_cliente, p_id_empleado)
    RETURNING id_venta INTO v_id_venta;

    INSERT INTO detalle_ventas (
        cantidad_venta, precio_unitario_venta, subtotal, id_venta, id_producto
    ) VALUES (
        p_cantidad, v_precio, v_total, v_id_venta, p_id_producto
    );

    UPDATE productos
    SET stock_actual = stock_actual - p_cantidad
    WHERE id_producto = p_id_producto;

    RETURN v_id_venta;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION fn_eliminar_cliente(
    p_id_cliente INT
) RETURNS INT AS $$
DECLARE
    v_deleted INT;
BEGIN
    DELETE FROM clientes WHERE id_cliente = p_id_cliente
    RETURNING id_cliente INTO v_deleted;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cliente no encontrado';
    END IF;

    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION fn_reporte_stock_bajo()
RETURNS TABLE(nombre_producto TEXT, stock_actual INT) AS $$
BEGIN
    RETURN QUERY
    SELECT nombre_producto, stock_actual
    FROM productos
    WHERE stock_actual < 50;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE PROCEDURE sp_registrar_venta_proc(
    p_id_cliente INT,
    p_id_empleado INT,
    p_id_producto INT,
    p_cantidad INT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_stock INT;
    v_precio NUMERIC(10,2);
    v_total NUMERIC(10,2);
    v_id_venta INT;
BEGIN
    SELECT stock_actual, precio_venta INTO v_stock, v_precio
    FROM productos
    WHERE id_producto = p_id_producto;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no existe';
    END IF;

    IF v_stock < p_cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente (Solo hay %)', v_stock;
    END IF;

    v_total := v_precio * p_cantidad;

    INSERT INTO ventas (total_venta, id_cliente, id_empleado)
    VALUES (v_total, p_id_cliente, p_id_empleado)
    RETURNING id_venta INTO v_id_venta;

    INSERT INTO detalle_ventas (
        cantidad_venta, precio_unitario_venta, subtotal, id_venta, id_producto
    ) VALUES (
        p_cantidad, v_precio, v_total, v_id_venta, p_id_producto
    );

    UPDATE productos
    SET stock_actual = stock_actual - p_cantidad
    WHERE id_producto = p_id_producto;
END;
$$;

CREATE OR REPLACE FUNCTION fn_obtener_cliente_info(
    p_id_cliente INT
) RETURNS TABLE(nombre TEXT, nit TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT nombre_cliente, nit_fiscal
    FROM clientes
    WHERE id_cliente = p_id_cliente;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cliente no encontrado';
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. VISTAS Y REPORTES

CREATE OR REPLACE VIEW vista_stock_bajo AS
SELECT nombre_producto, stock_actual
FROM productos
WHERE stock_actual < 50;

-- 6. DEFINICIÓN DE ÍNDICES

-- Justificación: Acelera la búsqueda de productos en la interfaz web por nombre.
CREATE INDEX idx_producto_nombre ON productos(nombre_producto);

-- Justificación: Optimiza la generación de reportes de ventas filtrados por fechas.
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);

-- Justificación: Mejora la velocidad de login al buscar por usuario de empleado.
CREATE INDEX idx_empleado_usuario ON empleados(usuario);

-- 7. PERMISOS GRANULARES POR ROL

GRANT CONNECT ON DATABASE tienda_db TO rol_ventas, rol_inventario, rol_clientes, rol_reportes, rol_gerente, proy3;
GRANT USAGE ON SCHEMA public TO rol_ventas, rol_inventario, rol_clientes, rol_reportes, rol_gerente, proy3;

-- Permisos sobre secuencias
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rol_ventas, rol_inventario, rol_clientes, rol_reportes, rol_gerente, proy3;

GRANT SELECT, INSERT, UPDATE, DELETE ON productos TO rol_inventario, rol_ventas, rol_reportes, rol_gerente, proy3;
GRANT SELECT ON categorias, proveedores TO rol_inventario, rol_ventas, rol_reportes, rol_gerente, proy3;
GRANT SELECT ON empleados TO rol_ventas, rol_reportes, rol_gerente, proy3;
GRANT SELECT ON clientes TO rol_clientes, rol_ventas, rol_reportes, rol_gerente, proy3;
GRANT SELECT, INSERT, DELETE ON clientes TO rol_clientes, rol_gerente, proy3;
GRANT SELECT, INSERT ON ventas, detalle_ventas TO rol_ventas, rol_gerente, proy3;
GRANT SELECT, INSERT ON compras, detalle_compras TO rol_inventario, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_crear_cliente(TEXT, TEXT, TEXT) TO rol_clientes, rol_ventas, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_crear_producto(TEXT, NUMERIC, NUMERIC, INT, INT, INT) TO rol_inventario, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_registrar_venta(INT, INT, INT, INT) TO rol_ventas, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_eliminar_cliente(INT) TO rol_clientes, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_reporte_stock_bajo() TO rol_reportes, rol_gerente, proy3;
GRANT EXECUTE ON PROCEDURE sp_registrar_venta_proc(INT, INT, INT, INT) TO rol_ventas, rol_gerente, proy3;
GRANT EXECUTE ON FUNCTION fn_obtener_cliente_info(INT) TO rol_clientes, rol_ventas, rol_reportes, rol_gerente, proy3;
GRANT SELECT ON vista_stock_bajo TO rol_reportes, rol_gerente, proy3;
