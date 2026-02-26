from flask import Flask, request, jsonify, render_template, redirect, url_for
from models.mensaje import Mensaje
from services.motor_evaluacion import MotorEvaluacion

app = Flask(__name__)

@app.route('/')
def index():
    """
    Página principal con formulario de análisis.
    """
    return render_template('index.html')

@app.route('/resultado')
def resultado():
    """
    Página de resultados del análisis.
    """
    resultado_str = request.args.get('resultado')
    if not resultado_str:
        return redirect(url_for('index'))
    
    try:
        import json
        resultado = json.loads(resultado_str)
        return render_template('resultado.html', resultado=resultado)
    except json.JSONDecodeError:
        return redirect(url_for('index'))

@app.route('/api/analizar', methods=['POST'])
def api_analizar():
    """
    Endpoint para analizar mensajes de phishing.
    """
    try:
        # Verificar si se recibió JSON
        if not request.is_json:
            return jsonify({
                'error': 'Se requiere JSON en la petición',
                'codigo': 400
            }), 400
        
        # Obtener datos del JSON
        data = request.get_json()
        
        # Verificar que exista el campo 'mensaje'
        if not data or 'mensaje' not in data:
            return jsonify({
                'error': 'El campo "mensaje" es requerido',
                'codigo': 400
            }), 400
        
        # Verificar que el mensaje no esté vacío
        if not data['mensaje'] or not data['mensaje'].strip():
            return jsonify({
                'error': 'El campo "mensaje" no puede estar vacío',
                'codigo': 400
            }), 400
        
        # Crear objeto Mensaje
        mensaje = Mensaje(data['mensaje'])
        
        # Crear instancia de MotorEvaluacion y analizar
        motor = MotorEvaluacion()
        resultado_analisis = motor.analizar_mensaje(mensaje)
        
        # Retornar resultado usando to_dict()
        return jsonify({
            'exito': True,
            'resultado': resultado_analisis.to_dict()
        })
        
    except Exception as e:
        # Manejo de errores generales
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}',
            'codigo': 500
        }), 500

@app.route('/analizar', methods=['POST'])
def analizar():
    """
    Endpoint para análisis desde formulario web.
    """
    try:
        # Obtener mensaje del formulario
        mensaje_texto = request.form.get('mensaje', '')
        
        if not mensaje_texto or not mensaje_texto.strip():
            return render_template('index.html', error='El mensaje no puede estar vacío')
        
        # Crear objeto Mensaje
        mensaje = Mensaje(mensaje_texto)
        
        # Crear instancia de MotorEvaluacion y analizar
        motor = MotorEvaluacion()
        resultado_analisis = motor.analizar_mensaje(mensaje)
        
        # Redirigir a página de resultados
        import json
        resultado_str = json.dumps(resultado_analisis.to_dict())
        return redirect(url_for('resultado', resultado=resultado_str))
        
    except Exception as e:
        return render_template('index.html', error=f'Error al analizar: {str(e)}')

@app.errorhandler(404)
def not_found(error):
    """
    Manejador de errores 404.
    """
    return jsonify({
        'error': 'Endpoint no encontrado',
        'codigo': 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """
    Manejador de errores 405 (método no permitido).
    """
    return jsonify({
        'error': 'Método no permitido',
        'codigo': 405
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """
    Manejador de errores 500.
    """
    return jsonify({
        'error': 'Error interno del servidor',
        'codigo': 500
    }), 500

if __name__ == "__main__":
    """
    Ejecutar la aplicación Flask en modo debug.
    """
    app.run(debug=True, host='0.0.0.0', port=5000)
