import pandas as pd
from .models import Registro, db

def importar_datos_csv(csv_path):
    # Leer el archivo CSV
    df = pd.read_csv(csv_path)

    # Limpiar y formatear los datos
    df['KILOS'] = df['KILOS'].str.replace(',', '.').astype(float)  # Reemplazar comas por puntos y convertir a float
    df['METROS'] = df['METROS'].str.replace(',', '.').astype(float)  # Reemplazar comas por puntos y convertir a float

    # Insertar cada fila en la base de datos
    for _, row in df.iterrows():
        registro = Registro(
            fecha=row['FECHA'],
            tejidos=row['TEJIDOS'],
            color=row['COLOR'],
            kilos=row['KILOS'],
            metros=row['METROS'],
            partida=row['PARTIDA'],
            tarifa_venta=row['TARIFA VENTA'],
            coste=None,  # Vacío por defecto
            facturado=None,  # Vacío por defecto
            beneficio=None  # Vacío por defecto
        )
        db.session.add(registro)
    db.session.commit()