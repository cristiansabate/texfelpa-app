from app import create_app, db  # Asegúrate de importar correctamente tu aplicación Flask
from app.models import Registro  # Ajusta la ruta de importación de tu modelo

def consultar_registros_2025():
    app = create_app()  # Crear la aplicación Flask
    with app.app_context():  # Iniciar el contexto de la aplicación
        registros = db.session.query(Registro).filter(Registro.fecha >= '2025-01-01', Registro.fecha <= '2025-12-31').all()
        for registro in registros:
            print(f"ID: {registro.id}, Fecha: {registro.fecha}, Tejidos: {registro.tejidos}, Color: {registro.color}, "
                  f"Kilos: {registro.kilos}, Metros: {registro.metros}, Partida: {registro.partida}, "
                  f"Tintura: {registro.tintura}, Coste: {registro.coste}, Facturado: {registro.facturado}, "
                  f"Beneficio: {registro.beneficio}, Rend: {registro.rend}, Precio Tintura: {registro.precio_tintura}")

if __name__ == "__main__":
    consultar_registros_2025()

