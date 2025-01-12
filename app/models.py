from . import db

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID automático
    fecha = db.Column(db.Date, nullable=False)  # Cambiar a tipo Date
    tejidos = db.Column(db.Integer, nullable=True)
    color = db.Column(db.Integer, nullable=True)
    kilos = db.Column(db.Float, nullable=True)
    metros = db.Column(db.Float, nullable=True)
    partida = db.Column(db.String(100), nullable=True)
    tintura = db.Column(db.Integer, nullable=True)
    coste = db.Column(db.Float, nullable=True)
    facturado = db.Column(db.Float, nullable=True)
    beneficio = db.Column(db.Float, nullable=True)
    rend = db.Column(db.Float, nullable=True)
    precio_tintura = db.Column(db.Float, nullable=True)  # Nueva columna

    

class PrecioColor(db.Model):
    __tablename__ = 'precios_color'
    
    id = db.Column(db.Integer, primary_key=True)  # ID automático
    color_numero = db.Column(db.Integer, nullable=False, unique=True)
    color_nombre = db.Column(db.String(100), nullable=False)
    tintes_alzira = db.Column(db.Float, nullable=True)
    area_tintura = db.Column(db.Float, nullable=True)
    precio_hilo = db.Column(db.Float, nullable=True)
    tejer_felpa = db.Column(db.Float, nullable=True)
    precio_acabado = db.Column(db.Float, nullable=True)
    precio_venta = db.Column(db.Float, nullable=True)