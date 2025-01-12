from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import Registro, db, PrecioColor
from datetime import datetime
from . import db
from sqlalchemy import func


felpa_routes = Blueprint('felpa', __name__, template_folder='../templates')


@felpa_routes.route('/registros-felpa', methods=['GET'])
def registros_felpa():
    # Consultar registros entre 2020 y 2025
    registros = Registro.query.filter(Registro.fecha >= datetime(2020, 1, 1),
                                      Registro.fecha <= datetime(2025, 12, 31)).all()

    # Calcular rendimiento medio anual
    rendimientos = {}
    for year in range(2020, 2026):
        registros_anuales = [r for r in registros if r.fecha.year == year and r.rend is not None]
        if registros_anuales:
            rendimiento_medio = sum(r.rend for r in registros_anuales) / len(registros_anuales)
            rendimientos[year] = round(rendimiento_medio, 2)
        else:
            rendimientos[year] = None  # Si no hay registros, se asigna None

    # Datos específicos para la sección de gráficos de felpa-2025
    year = 2025
    registros_2025 = [r for r in registros if r.fecha.year == year]
    partidas_tintadas = len(registros_2025)
    kilos_tintados = sum(r.kilos for r in registros_2025 if r.kilos)
    metros_tintados = sum(r.metros for r in registros_2025 if r.metros)
    total_facturado = sum(r.facturado for r in registros_2025 if r.facturado)
    coste_total = sum(r.coste for r in registros_2025 if r.coste)

    fechas = [r.fecha.strftime('%d-%m-%Y') for r in registros_2025]
    metros_diarios = [r.metros for r in registros_2025 if r.metros]
    facturacion_diaria = [r.facturado for r in registros_2025 if r.facturado]

    # Renderizar plantilla y pasar todos los datos necesarios
    return render_template(
        'registros-felpa.html',
        registros=registros,
        rendimientos=rendimientos,
        partidas_tintadas=partidas_tintadas,
        kilos_tintados=kilos_tintados,
        metros_tintados=metros_tintados,
        total_facturado=total_facturado,
        coste_total=coste_total,
        fechas=fechas,
        metros_diarios=metros_diarios,
        facturacion_diaria=facturacion_diaria,
        year=year
    )




@felpa_routes.route('/colores-disponibles')
def colores_disponibles():
    # Obtener los colores únicos desde la base de datos
    colores = db.session.query(Registro.color).distinct().all()
    # Extraer solo los valores de color en una lista
    colores_lista = [c[0] for c in colores]
    return jsonify({'colores': colores_lista})



@felpa_routes.route('/cargar-registros')
def cargar_registros():
    columna = request.args.get('columna', 'id')
    direccion = request.args.get('direccion', 'asc')

    # Filtros opcionales
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    colores = request.args.getlist('colores')  # Obtener lista de colores seleccionados

    query = Registro.query

    # Aplicar filtros de fecha si existen
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Registro.fecha >= fecha_inicio_dt)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Fecha de inicio inválida'}), 400

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Registro.fecha <= fecha_fin_dt)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Fecha de fin inválida'}), 400

    # Aplicar filtro de colores si existe
    if colores:
        try:
            colores_lista = [int(c) for c in colores]
            query = query.filter(Registro.color.in_(colores_lista))
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Filtro de color inválido'}), 400

    # Ordenar resultados
    if direccion == 'asc':
        query = query.order_by(getattr(Registro, columna).asc())
    else:
        query = query.order_by(getattr(Registro, columna).desc())

    registros = query.all()  # Obtener todos los registros filtrados
    return render_template('registros_parciales.html', registros=registros)



@felpa_routes.route('/editar-registro/<int:id>', methods=['POST'])
def editar_registro(id):
    try:
        registro = Registro.query.get_or_404(id)

        # Convertir la fecha a objeto datetime.date
        fecha_str = request.form['fecha']
        registro.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

        # Actualizar los demás campos del registro
        registro.tejidos = int(request.form['tejidos'])
        registro.color = int(request.form['color'])
        registro.kilos = float(request.form['kilos'])
        registro.metros = float(request.form['metros'])
        registro.partida = request.form['partida']

        # Obtener la tintura seleccionada del formulario
        tintura_seleccionada = request.form['tintura']

        # Recalcular rendimiento
        registro.rend = round(registro.metros / registro.kilos, 2) if registro.kilos != 0 else None

        # Relacionar con la tabla PrecioColor para obtener los precios necesarios
        precio_color = PrecioColor.query.filter_by(color_numero=registro.color).first()

        if precio_color:
            # Actualizar el precio de tintura según la opción seleccionada
            if tintura_seleccionada == "Tintes Alzira":
                registro.precio_tintura = precio_color.tintes_alzira or 0
            elif tintura_seleccionada == "Área Tintura":
                registro.precio_tintura = precio_color.area_tintura or 0
            else:
                registro.precio_tintura = 0

            # Calcular el nuevo coste y facturado si el rendimiento es válido
            if registro.rend and registro.rend > 0:
                precio_acabado = precio_color.precio_acabado or 0
                tejer_felpa = precio_color.tejer_felpa or 0
                precio_hilo = precio_color.precio_hilo or 0
                print(f"Metros recibidos: {registro.metros}, Kilos recibidos: {registro.kilos}, Rendimiento: {registro.rend}, Precio tintura: {registro.precio_tintura}, Acabado: {precio_acabado}, Felpa: {tejer_felpa}, Hilo: {precio_hilo}")
                registro.coste = round(((registro.precio_tintura + precio_acabado + tejer_felpa + precio_hilo) / registro.rend) * registro.metros, 2)
                registro.facturado = round(precio_color.precio_venta * registro.metros, 2)
            else:
                registro.coste = None
                registro.facturado = None
            # Calcular el nuevo beneficio
            if registro.coste is not None and registro.facturado is not None:
                registro.beneficio = round(registro.facturado - registro.coste, 2)
            else:
                registro.beneficio = None
        else:
            # Si no se encuentra el precio del color, asignar None a todos los campos dependientes
            registro.precio_tintura = 0
            registro.coste = None
            registro.facturado = None
            registro.beneficio = None

        # Guardar los cambios en la base de datos
        print(f"Coste calculado: {registro.coste}, Facturado: {registro.facturado}, Beneficio: {registro.beneficio}")
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Registro actualizado correctamente.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500




@felpa_routes.route('/formulario-felpa', methods=['GET', 'POST'])
def nuevo_registro():
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            fecha_str = request.form['fecha']
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()  # Convertir a objeto date
            
            tejidos = int(request.form['tejidos'])
            color = int(request.form['color'])
            kilos = float(request.form['kilos'])
            metros = float(request.form['metros'])
            partida = request.form['partida']
            tintura_seleccionada = request.form['tintura']

            # Calcular rendimiento
            rend = round(metros / kilos, 2) if kilos != 0 else None

            # Buscar el precio correspondiente en la tabla PrecioColor
            precio_color = PrecioColor.query.filter_by(color_numero=color).first()

            if precio_color:
                # Obtener el precio de tintura según la tarifa seleccionada
                if tintura_seleccionada == "Tintes Alzira":
                    precio_tintura = precio_color.tintes_alzira or 0
                elif tintura_seleccionada == "Área Tintura":
                    precio_tintura = precio_color.area_tintura or 0
                else:
                    precio_tintura = 0

                # Calcular el coste solo si el rendimiento es válido
                if rend and rend > 0:
                    precio_acabado = precio_color.precio_acabado or 0
                    tejer_felpa = precio_color.tejer_felpa or 0
                    precio_hilo = precio_color.precio_hilo or 0
                    coste = round(((precio_tintura + precio_acabado + tejer_felpa + precio_hilo) / rend) * metros, 2)
                else:
                    coste = None

                # Calcular el facturado
                facturado = round(precio_color.precio_venta * metros, 2)

                # Calcular el beneficio
                beneficio = round(facturado - coste, 2) if coste is not None else None
            else:
                # Si no se encuentra el precio del color, asignar valores predeterminados
                precio_tintura = 0
                coste = None
                facturado = None
                beneficio = None

            # Crear un nuevo registro con los valores calculados
            nuevo_registro = Registro(
                fecha=fecha,  # Ahora es un objeto date
                tejidos=tejidos,
                color=color,
                kilos=kilos,
                metros=metros,
                partida=partida,
                tintura=precio_tintura,
                rend=rend,
                precio_tintura=precio_tintura,
                coste=coste,
                facturado=facturado,
                beneficio=beneficio
            )

            # Guardar el registro en la base de datos
            db.session.add(nuevo_registro)
            db.session.commit()

            # Agregar un mensaje flash de éxito
            flash('El registro se ha añadido correctamente.', 'success')
            return redirect(url_for('felpa.nuevo_registro'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al añadir el registro: {str(e)}', 'danger')
            return redirect(url_for('felpa.nuevo_registro'))

    return render_template('formulario-felpa.html')





@felpa_routes.route('/grafico-felpa')
def grafico_registros():
    # Consultar todos los registros de la base de datos
    registros = Registro.query.all()

    # Preparar los datos como una lista de diccionarios
    data = [{'fecha': r.fecha, 'kilos': r.kilos, 'metros': r.metros} for r in registros]

    # Renderizar la plantilla y pasar los datos en formato JSON
    return render_template('grafico.html', registros=data)


@felpa_routes.route('/beneficios-felpa', methods=['GET'])
def grafico_beneficio():
    from calendar import month_name

    # Obtener el año seleccionado del formulario (por defecto, el año actual)
    year = request.args.get('year', default=datetime.now().year, type=int)

    # Consultar el beneficio mensual agrupado por mes del año seleccionado
    resultados = (
        db.session.query(
            func.extract('month', Registro.fecha).label('mes'),
            func.sum(Registro.beneficio).label('beneficio_mensual')
        )
        .filter(func.extract('year', Registro.fecha) == year)
        .group_by(func.extract('month', Registro.fecha))
        .order_by(func.extract('month', Registro.fecha))
        .all()
    )

    # Crear un diccionario con los beneficios mensuales, completando con 0 los meses sin datos
    beneficios_por_mes = {int(r.mes): float(r.beneficio_mensual) if r.beneficio_mensual is not None else 0 for r in resultados}
    meses = list(range(1, 13))  # Meses del 1 al 12
    beneficios = [round(beneficios_por_mes.get(mes, 0), 2) for mes in meses]  # Beneficios con 2 decimales

    # Manejar el caso en el que no haya beneficios en el año seleccionado
    if all(b == 0 for b in beneficios):  # Si todos los valores de beneficios son 0
        beneficio_total = 0
        mes_mayor_beneficio = None
        mes_menor_beneficio = None
        max_beneficio = "0,00"
        min_beneficio = "0,00"
    else:
        # Calcular el beneficio anual total, mes con mayor beneficio y mes con menor beneficio
        beneficio_total = round(sum(beneficios), 2)
        mes_mayor_beneficio = meses[beneficios.index(max(beneficios))]
        mes_menor_beneficio = meses[beneficios.index(min(beneficios))]
        max_beneficio = f"{max(beneficios):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        min_beneficio = f"{min(beneficios):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Pasar los nombres de los meses al gráfico
    nombres_meses = [month_name[mes] for mes in meses]

    # Formatear números con punto para miles y coma para decimales
    def formato_numero(numero):
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return render_template(
        'beneficios-felpa.html',
        meses=nombres_meses,
        beneficios=beneficios,
        year=year,
        beneficio_total=formato_numero(beneficio_total),
        mes_mayor_beneficio=mes_mayor_beneficio,
        mes_menor_beneficio=mes_menor_beneficio,
        max_beneficio=max_beneficio,
        min_beneficio=min_beneficio
    )



@felpa_routes.route('/felpa-2025')
def dashboard_tintados():
    # Filtrar registros del año 2025
    year = 2025
    registros = db.session.query(Registro).filter(func.extract('year', Registro.fecha) == year).all()

    # Cálculos para las tarjetas
    partidas_tintadas = len(registros)
    kilos_tintados = sum(r.kilos for r in registros if r.kilos)
    metros_tintados = sum(r.metros for r in registros if r.metros)
    total_facturado = sum(r.facturado for r in registros if r.facturado)
    coste_total = sum(r.coste for r in registros if r.coste)

    # Datos para el gráfico de líneas y barras
    fechas = [r.fecha.strftime('%d-%m-%Y') for r in registros]
    metros_diarios = [r.metros for r in registros if r.metros]
    facturacion_diaria = [r.facturado for r in registros if r.facturado]

    return render_template(
        'felpa-2025.html',
        partidas_tintadas=partidas_tintadas,
        kilos_tintados=kilos_tintados,
        metros_tintados=metros_tintados,
        total_facturado=total_facturado,
        coste_total=coste_total,
        fechas=fechas,
        metros_diarios=metros_diarios,
        facturacion_diaria=facturacion_diaria,
        year=year
    )
