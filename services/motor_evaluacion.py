from services.detector_contenido import DetectorContenido

class MotorEvaluacion:
    """
    Clase principal que coordina el análisis completo de mensajes
    Implementa el patrón de diseño Facade para simplificar la interfaz
    """
    
    def __init__(self):
        self.detector_contenido = DetectorContenido()
        
        self.umbrales = {
            'seguro_max': 2,
            'sospechoso_max': 5
        }
    
    def analizar_mensaje(self, texto):
        """
        Funcion principal que analiza un mensaje completo
        
        Returns:
            Dict con:
            - risk_level: str - 'Seguro', 'Sospechoso', 'Peligroso'
            - detected_elements: List[Dict] - Elementos detectados con detalles
            - score: int - Puntuación total
            - links_detected: List[str] - URLs encontradas (vacío por ahora)
        """
        resultado_contenido = self.detector_contenido.analizar(texto)
        
        score = resultado_contenido['score_total']
        
        risk_level = self._determinar_nivel_riesgo(score)
        
        detected_elements = self._formatear_elementos(
            resultado_contenido['elementos_detectados']
        )
        
        links_detected = []
        
        return {
            'risk_level': risk_level,
            'detected_elements': detected_elements,
            'score': score,
            'links_detected': links_detected
        }
    
    def _determinar_nivel_riesgo(self, score):
        """
        Determina el nivel de riesgo basado en el score
        """
        if score <= self.umbrales['seguro_max']:
            return 'Seguro'
        elif score <= self.umbrales['sospechoso_max']:
            return 'Sospechoso'
        else:
            return 'Peligroso'
    
    def _formatear_elementos(self, elementos):
        """
        Formatea los elementos detectados para salida estandarizada
        """
        elementos_formateados = []
        
        for elemento in elementos:
            elementos_formateados.append({
                'tipo': elemento['categoria'],
                'elemento': elemento['elemento'],
                'peso': elemento['peso'],
                'descripcion': self._generar_descripcion(elemento)
            })
        
        return elementos_formateados
    
    def _generar_descripcion(self, elemento):
        """
        Genera una descripción legible para cada elemento detectado
        """
        categoria = elemento['categoria']
        elemento_texto = elemento['elemento']
        
        descripciones = {
            'urgencia': f"Palabra de urgencia detectada: '{elemento_texto}'",
            'accion_obligatoria': f"Acción obligatoria detectada: '{elemento_texto}'",
            'incentivo': f"Incentivo sospechoso detectado: '{elemento_texto}'",
            'amenaza': f"Amenaza directa detectada: '{elemento_texto}'",
            'formato': f"Problema de formato detectado: '{elemento_texto}'"
        }
        
        return descripciones.get(
            categoria,
            f"Elemento sospechoso: '{elemento_texto}'"
        )
    
    def obtener_resumen_categorias(self, elementos):
        """
        Obtiene un resumen de cuántos elementos hay por categoría
        """
        resumen = {}
        
        for elemento in elementos:
            categoria = elemento['tipo']
            resumen[categoria] = resumen.get(categoria, 0) + 1
        
        return resumen
