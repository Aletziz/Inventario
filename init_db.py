from app import app, db, Usuario
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        print("Iniciando inicialización de la base de datos...")
        
        # Eliminar todas las tablas existentes
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas
        print("Creando nuevas tablas...")
        db.create_all()
        
        # Crear usuarios
        print("Creando usuarios...")
        
        # Usuario admin
        admin = Usuario(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        # Usuario josue
        josue = Usuario(
            username='josue',
            password_hash=generate_password_hash('josueconyedo321')
        )
        db.session.add(josue)
        
        # Guardar cambios
        try:
            db.session.commit()
            print("Base de datos inicializada exitosamente!")
            print("Usuarios creados:")
            print("- admin/admin123")
            print("- josue/josueconyedo321")
        except Exception as e:
            db.session.rollback()
            print(f"Error al inicializar la base de datos: {str(e)}")
            raise e

if __name__ == '__main__':
    init_db() 