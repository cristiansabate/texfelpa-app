from flask import Blueprint, render_template, jsonify
from .models import Registro, PrecioColor

graficos_routes = Blueprint('graficos', __name__, template_folder='../templates')

# Ruta para renderizar la página del gráfico
@graficos_routes.route('/beneficios-felpa')
def beneficios_felpa():
    return render_template('graficos/beneficios-felpa.html')

# Ruta para devolver los datos en formato JSON
@graficos_routes.route('/beneficios-felpa-datos')
def grafico_beneficio_anual():
    try:
        # Consultar todos los registros de la tabla Registro
        registros = Registro.query.all()

        # Diccionario para almacenar el beneficio anual
        beneficio_anual = {}

        for registro in registros:
            # Relacionar el color del registro con color_numero en PrecioColor
            precio_color = PrecioColor.query.filter_by(color_numero=registro.color).first()

            if precio_color:
                # Calcular facturado: precio_venta * metros
                facturado = precio_color.precio_venta * registro.metros
                # Calcular beneficio: facturado - coste
                beneficio = facturado - (registro.coste or 0)

                # Extraer el año de la fecha del registro
                year = registro.fecha.year

                # Sumar el beneficio al año correspondiente
                if year in beneficio_anual:
                    beneficio_anual[year] += beneficio
                else:
                    beneficio_anual[year] = beneficio

        # Ordenar los beneficios por año
        beneficio_anual = dict(sorted(beneficio_anual.items()))

        return jsonify({'status': 'success', 'data': beneficio_anual})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


