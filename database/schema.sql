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
    contrasena VARCHAR(255) NOT NULL
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

-- 4. DEFINICIÓN DE ÍNDICES

-- Justificación: Acelera la búsqueda de productos en la interfaz web por nombre.
CREATE INDEX idx_producto_nombre ON PRODUCTOS(nombre_producto);

-- Justificación: Optimiza la generación de reportes de ventas filtrados por fechas.
CREATE INDEX idx_ventas_fecha ON VENTAS(fecha_venta);

-- Justificación: Mejora la velocidad de login al buscar por usuario de empleado.
CREATE INDEX idx_empleado_usuario ON EMPLEADOS(usuario);