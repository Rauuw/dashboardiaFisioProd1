
from flask import Flask, render_template, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Configura la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:JMdIVQBtXWQlHweRScAftFmuFuqXBqVo@monorail.proxy.rlwy.net:18490/fisio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define el modelo
class Ejercicio(db.Model):
    __tablename__ = 'rutina_ejercicio'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    tiempo_ejercicio = db.Column(db.Integer, nullable=False)
    cantidad_repeticiones = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    paciente_id = db.Column(db.Integer, nullable=False)


# Ruta para KPI 1: Tiempo por Ejercicio
@app.route('/kpi1/<int:id>')
def kpi1(id):
    ejercicios = db.session.query(Ejercicio).filter_by(paciente_id=id).all()

    # Obtener datos para el gráfico
    repeticiones = [ejercicio.cantidad_repeticiones for ejercicio in ejercicios]
    tiempos = [ejercicio.tiempo_ejercicio for ejercicio in ejercicios]

    # Generar gráfico de barras
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(repeticiones)), tiempos, align='center', alpha=0.7, label='Tiempo de Ejecución')
    plt.xticks(range(len(repeticiones)), repeticiones)
    plt.xlabel('Cantidad de Repeticiones')
    plt.ylabel('Tiempo de Ejecución (segundos)')
    plt.title('Tiempo de Ejecución por Cantidad de Repeticiones por Ejercicio')
    plt.legend()

    # Guardar gráfico en un objeto BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')


# Ruta para KPI 2: Porcentaje de Ejercicios Completados Correctamente
@app.route('/kpi2/<int:id>')
def kpi2(id):
    total_ejercicios = db.session.query(Ejercicio).filter_by(paciente_id=id).count()
    ejercicios_correctos = db.session.query(Ejercicio).filter_by(paciente_id=id, motivo='Ejercicio correcto').count()
    ejercicios_incorrectos = db.session.query(Ejercicio).filter(Ejercicio.paciente_id == id, Ejercicio.motivo != 'Ejercicio correcto').count()

    # Calcular porcentajes
    porcentaje_correctos = (ejercicios_correctos / total_ejercicios) * 100 if total_ejercicios > 0 else 0
    porcentaje_incorrectos = (ejercicios_incorrectos / total_ejercicios) * 100 if total_ejercicios > 0 else 0

    # Generar gráfico de torta
    labels = ['Correcto', 'Incorrecto']
    sizes = [porcentaje_correctos, porcentaje_incorrectos]
    colors = ['green', 'red']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Porcentaje de Ejercicios Completados Correctamente e Incorrectamente')

    # Guardar gráfico en un objeto BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
