from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# Configuración de la base de datos
if os.environ.get('DATABASE_URL'):
    # Configuración para producción (Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Configuración para desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'

# Añadir esta línea para evitar advertencias
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Modelos de la base de datos
class Usuario(db.Model):
    __tablename__ = 'usuario'  # Nombre explícito de la tabla
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Producto(db.Model):
    __tablename__ = 'producto'  # Nombre explícito de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(200))

class Venta(db.Model):
    __tablename__ = 'venta'  # Nombre explícito de la tabla
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    productos = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'  # Nombre explícito de la tabla
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto')

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Verificar si el usuario existe
            user = Usuario.query.filter_by(username=username).first()
            
            if user is None:
                print(f"Intento de login fallido: Usuario '{username}' no encontrado")
                flash('Usuario no encontrado')
                return render_template('login.html')
            
            # Verificar la contraseña
            if check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                print(f"Login exitoso para usuario: {username}")
                flash('Inicio de sesión exitoso')
                return redirect(url_for('index'))
            else:
                print(f"Intento de login fallido: Contraseña incorrecta para usuario '{username}'")
                flash('Contraseña incorrecta')
                return render_template('login.html')
                
        return render_template('login.html')
    except Exception as e:
        print(f"Error en login: {str(e)}")
        flash('Ocurrió un error durante el inicio de sesión. Por favor, intente nuevamente.')
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
@login_required
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        descripcion = request.form['descripcion']
        
        nuevo_producto = Producto(nombre=nombre, precio=precio, 
                                cantidad=cantidad, descripcion=descripcion)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente')
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.precio = float(request.form['precio'])
        producto.cantidad = int(request.form['cantidad'])
        producto.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Producto actualizado exitosamente')
        return redirect(url_for('index'))
    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar_producto/<int:id>')
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    # Eliminar primero los detalles de venta relacionados
    DetalleVenta.query.filter_by(producto_id=id).delete()
    
    # Eliminar el producto
    db.session.delete(producto)
    db.session.commit()
    
    flash('Producto y su historial de ventas eliminados exitosamente')
    return redirect(url_for('index'))

@app.route('/realizar_venta', methods=['GET', 'POST'])
@login_required
def realizar_venta():
    if request.method == 'POST':
        productos_seleccionados = request.form.getlist('productos')
        cantidades_restantes = request.form.getlist('cantidades_restantes')
        
        total = 0
        nueva_venta = Venta(total=0)
        db.session.add(nueva_venta)
        db.session.flush()
        
        for i, producto_id in enumerate(productos_seleccionados):
            cantidad_restante = int(cantidades_restantes[i])
            producto = Producto.query.get(producto_id)
            
            # Solo procesar si la cantidad restante es diferente al stock actual
            if cantidad_restante != producto.cantidad:
                # Calcular la cantidad vendida como la diferencia entre el stock actual y la cantidad que quedará
                cantidad_vendida = producto.cantidad - cantidad_restante
                
                if cantidad_vendida > 0:  # Asegurarse de que la cantidad vendida sea positiva
                    detalle = DetalleVenta(
                        venta_id=nueva_venta.id,
                        producto_id=producto_id,
                        cantidad=cantidad_vendida,
                        precio_unitario=producto.precio
                    )
                    total += producto.precio * cantidad_vendida
                    producto.cantidad = cantidad_restante  # Actualizar el stock con la cantidad restante
                    db.session.add(detalle)
                else:
                    flash(f'La cantidad restante de {producto.nombre} no puede ser mayor que el stock actual')
                    db.session.rollback()
                    return redirect(url_for('realizar_venta'))
        
        # Solo guardar la venta si se vendió al menos un producto
        if total > 0:
            nueva_venta.total = total
            db.session.commit()
            flash('Venta realizada exitosamente')
        else:
            db.session.rollback()
            flash('No se realizaron ventas. Debe modificar al menos un producto para realizar una venta.')
        
        return redirect(url_for('index'))
    
    productos = Producto.query.filter(Producto.cantidad > 0).all()
    return render_template('realizar_venta.html', productos=productos)

@app.route('/historial_ventas')
@login_required
def historial_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('historial_ventas.html', ventas=ventas)

@app.route('/reportes')
@login_required
def reportes():
    # Estadísticas básicas
    total_ventas = Venta.query.count()
    total_ingresos = db.session.query(db.func.sum(Venta.total)).scalar() or 0
    
    # Productos más vendidos (calculando la diferencia entre stock inicial y final)
    productos_mas_vendidos = db.session.query(
        Producto.nombre,
        db.func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Producto.id).order_by(db.desc('total_vendido')).limit(5).all()
    
    # Ingresos por producto
    ingresos_por_producto = db.session.query(
        Producto.nombre,
        db.func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario).label('ingresos_totales')
    ).join(DetalleVenta).group_by(Producto.id).order_by(db.desc('ingresos_totales')).all()
    
    return render_template('reportes.html',
                         total_ventas=total_ventas,
                         total_ingresos=total_ingresos,
                         productos_mas_vendidos=productos_mas_vendidos,
                         ingresos_por_producto=ingresos_por_producto)

@app.route('/limpiar_historial_ventas')
@login_required
def limpiar_historial_ventas():
    try:
        # Eliminar todos los detalles de ventas
        DetalleVenta.query.delete()
        # Eliminar todas las ventas
        Venta.query.delete()
        # Confirmar los cambios
        db.session.commit()
        flash('El historial de ventas ha sido eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el historial: {str(e)}', 'danger')
    
    return redirect(url_for('historial_ventas'))

if __name__ == '__main__':
    app.run(debug=True)