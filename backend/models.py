from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Categoria(Base):
    __tablename__ = "categorias"
    id_categoria = Column(Integer, primary_key=True)
    nombre_categoria = Column(String(100), nullable=False)
    descripcion_categoria = Column(Text)

    productos = relationship("Producto", back_populates="categoria")

class Proveedor(Base):
    __tablename__ = "proveedores"
    id_proveedor = Column(Integer, primary_key=True)
    nombre_empresa = Column(String(150), nullable=False)
    contacto = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False)

    productos = relationship("Producto", back_populates="proveedor")

class Cliente(Base):
    __tablename__ = "clientes"
    id_cliente = Column(Integer, primary_key=True)
    nombre_cliente = Column(String(150), nullable=False)
    nit_fiscal = Column(String(20), unique=True, nullable=False)
    correo = Column(String(100))

class Empleado(Base):
    __tablename__ = "empleados"
    id_empleado = Column(Integer, primary_key=True)
    nombre_empleado = Column(String(150), nullable=False)
    puesto = Column(String(100))
    usuario = Column(String(50), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)

class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True)
    nombre_producto = Column(String(150), nullable=False)
    descripcion_producto = Column(Text)
    precio_costo = Column(Numeric(10, 2), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, nullable=False, default=0)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)

    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")

class Compra(Base):
    __tablename__ = "compras"
    id_compra = Column(Integer, primary_key=True)
    fecha_compra = Column(DateTime, server_default=func.now())
    total_compra = Column(Numeric(10, 2), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)

class Venta(Base):
    __tablename__ = "ventas"
    id_venta = Column(Integer, primary_key=True)
    fecha_venta = Column(DateTime, server_default=func.now())
    total_venta = Column(Numeric(10, 2), nullable=False)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_empleado = Column(Integer, ForeignKey("empleados.id_empleado"), nullable=False)

class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    id_detalle_venta = Column(Integer, primary_key=True)
    cantidad_venta = Column(Integer, nullable=False)
    precio_unitario_venta = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
