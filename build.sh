#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Inicializar la base de datos y usuarios solo si no existen
python -c "
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # Verificar si las tablas existen
    inspector = db.inspect(db.engine)
    if not inspector.has_table('producto'):
        print('Creando tablas de la base de datos...')
        db.create_all()
        
        # Crear usuarios iniciales solo si la tabla usuario está vacía
        if not Usuario.query.first():
            print('Creando usuarios iniciales...')
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
            
            try:
                db.session.commit()
                print('Usuarios iniciales creados exitosamente!')
            except Exception as e:
                db.session.rollback()
                print(f'Error al crear usuarios iniciales: {str(e)}')
    else:
        print('Las tablas ya existen, no se realizará ninguna modificación.')
"