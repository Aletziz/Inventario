#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Inicializar la base de datos solo si no existe
python -c "
from app import app, db
with app.app_context():
    # Verificar si las tablas existen
    inspector = db.inspect(db.engine)
    if not inspector.has_table('producto'):
        print('Creando tablas de la base de datos...')
        db.create_all()
    else:
        print('Las tablas ya existen, no se realizará ninguna modificación.')
"