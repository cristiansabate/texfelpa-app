from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import Registro, db, PrecioColor
from .utils import importar_datos_csv

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/')
def index():
    
    return render_template('index.html')



@main.route('/mas-datos')
def mas_datos():
    return render_template('mas-datos.html')


@main.route('/load-more', methods=['GET'])
def load_more():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = Registro.query.order_by(Registro.fecha.desc()).paginate(page=page, per_page=per_page)
    
    registros = []
    for registro in pagination.items:
        precio_color = PrecioColor.query.filter_by(color_numero=registro.color).first()
        if precio_color:
            precio_hilo = precio_color.precio_hilo or 0
            tejer_felpa = precio_color.tejer_felpa or 0
            precio_acabado = precio_color.precio_acabado or 0
            coste = ((registro.precio_tintura + precio_hilo + tejer_felpa + precio_acabado) / (registro.rend or 1)) * (registro.metros or 0)
            facturado = (precio_color.precio_venta or 0) * (registro.metros or 0)
            beneficio = facturado - coste
        else:
            coste = facturado = beneficio = 0

        registros.append({
            'id': registro.id,
            'fecha': registro.fecha,
            'tejidos': registro.tejidos,
            'partida': registro.partida,
            'color': registro.color,
            'kilos': registro.kilos,
            'metros': registro.metros,
            'rend': registro.rend,
            'tarifa_venta': registro.tarifa_venta,
            'precio_tintura': registro.precio_tintura,
            'coste': round(coste, 2),
            'facturado': round(facturado, 2),
            'beneficio': round(beneficio, 2)
        })
    
    return jsonify({'registros': registros, 'has_more': pagination.has_next})
