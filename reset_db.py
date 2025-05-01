import os
import sys
import time

# Ruta a la base de datos
db_path = 'instance/tienda.db'

print("ADVERTENCIA: Esta acción eliminará toda la base de datos, incluyendo:")
print("- Todos los productos")
print("- Historial completo de ventas")
print("- Registros de ingresos totales")
print("- Estadísticas acumuladas")

confirmation = input("\n¿Estás seguro de que deseas continuar? (s/n): ")

if confirmation.lower() == 's':
    # Verificar si el archivo existe
    if os.path.exists(db_path):
        try:
            # Intentar eliminar el archivo
            os.remove(db_path)
            print(f"\nBase de datos '{db_path}' eliminada correctamente.")
            print("La próxima vez que ejecutes la aplicación, se creará una nueva base de datos vacía.")
        except PermissionError:
            print("\nError: No se puede eliminar la base de datos porque está siendo utilizada por otro proceso.")
            print("Por favor, asegúrate de cerrar la aplicación Flask antes de ejecutar este script.")
            print("Instrucciones:")
            print("1. Detén la aplicación Flask (presiona Ctrl+C en la terminal donde se ejecuta)")
            print("2. Cierra todas las conexiones a la base de datos")
            print("3. Intenta ejecutar este script nuevamente")
    else:
        print(f"\nNo se encontró la base de datos '{db_path}'.")
else:
    print("\nOperación cancelada. La base de datos no ha sido modificada.")