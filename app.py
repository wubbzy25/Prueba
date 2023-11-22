import json
import requests
from flask import Flask, request, jsonify

# Definición de una clase para el servicio de agenda
class ServicioAgenda:
    def __init__(self, url_datos):
        self.url_datos = url_datos
        self.actualizar_datos_agenda()

    def actualizar_datos_agenda(self):
        try:
            # Obtención de datos desde la URL especificada
            respuesta = requests.get(self.url_datos)
            
            # Verificación de si la solicitud fue exitosa
            respuesta.raise_for_status()  

            # Parseo de la respuesta JSON y almacenamiento de los datos como agenda
            self.datos_agenda = respuesta.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la agenda: {e}")
            self.datos_agenda = []

    def obtener_espacios_disponibles(self, dia):
        try:
            # Filtrado de citas para el día especificado
            citas_dia = [
                cita for cita in self.datos_agenda
                if cita['Day'].lower() == dia.lower()
            ]

            # Cálculo del tiempo total ocupado para el día
            tiempo_ocupado = sum(int(cita['Duration']) for cita in citas_dia)

            # Cálculo del tiempo total de trabajo disponible en minutos
            tiempo_total_trabajo = (
                17 - 9
            ) * 60  # Horas de trabajo de 9:00 a 17:00 en minutos

            # Cálculo del tiempo disponible para citas
            tiempo_disponible = tiempo_total_trabajo - tiempo_ocupado

            # Establecimiento de la duración mínima para una cita
            duracion_minima_cita = 30

            # Cálculo del número de espacios disponibles para citas
            espacios_disponibles = tiempo_disponible // duracion_minima_cita

            return espacios_disponibles
        except KeyError as e:
            print(f"Error al procesar datos de la agenda: {e}")
            return 0 

# Inicialización de la aplicación Flask
app = Flask(__name__)

# URL de la agenda como variable de configuración
URL_AGENDA = "https://luegopago.blob.core.windows.net/luegopago-uploads/Pruebas%20LuegoPago/data.json"

# Creación de una instancia de la clase ServicioAgenda con la URL de la agenda como parámetro
servicio_agenda = ServicioAgenda(URL_AGENDA)
# Definición de una ruta para obtener espacios disponibles para citas
@app.route('/espacios_disponibles', methods=['GET'])
def obtener_espacios_disponibles():
    # Extracción del parámetro 'dia' de la solicitud
    dia = request.args.get('dia')

    # Manejo del caso en que falta el parámetro 'dia'
    if not dia:
        return jsonify({'error': 'Debes proporcionar el día de la semana'}), 400

    try:
        # Llamada al método obtener_espacios_disponibles y devolución del resultado como JSON
        espacios_disponibles = servicio_agenda.obtener_espacios_disponibles(dia)
        return jsonify({'dia': dia, 'espacios_disponibles': espacios_disponibles})
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error interno'}), 500

# Ejecución de la aplicación Flask si el script se ejecuta directamente
if __name__ == '__main__':
    app.run(debug=True)
