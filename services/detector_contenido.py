from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """Clase base para todos los detectores """
    
    def __init__(self):
        self.palabras_clave = []
        self.peso = 0
        self.categoria = ""
    
    @abstractmethod
    def detectar(self, texto):
        """Método abstracto para detectar elementos """
        pass
    
    def _limpiar_texto(self, texto):
        """Método protegido para normalizar texto"""
        return texto.lower().strip()
    
    def _encontrar_palabras(self, texto):
        """Método protegido para encontrar palabras clave"""
        texto_limpio = self._limpiar_texto(texto)
        encontradas = []
        
        for palabra in self.palabras_clave:
            if palabra in texto_limpio:
                encontradas.append(palabra)
        
        return list(set(encontradas))  # Eliminar duplicados

class DetectorUrgencia(BaseDetector):
    """Detector de palabras de urgencia - hereda de BaseDetector"""
    
    def __init__(self):
        super().__init__()
        self.palabras_clave = [
            'urgente', 'inmediato', 'inmediatamente', 'ahora', 'rápido',
            'última oportunidad', 'expira hoy', 'limite', 'antes de que sea tarde',
            'no esperes', 'al instante', 'de inmediato', 'sin demora'
        ]
        self.peso = 2
        self.categoria = "urgencia"
    
    def detectar(self, texto):
        return self._encontrar_palabras(texto)

class DetectorAccionObligatoria(BaseDetector):
    """Detector de acciones obligatorias """
    
    def __init__(self):
        super().__init__()
        self.palabras_clave = [
            'verifica', 'actualiza', 'confirma', 'haz clic', 'haga clic',
            'click aquí', 'descargar', 'instalar', 'ingresa', 'proporciona',
            'envía', 'completa', 'registra', 'autentica'
        ]
        self.peso = 2
        self.categoria = "accion_obligatoria"
    
    def detectar(self, texto):
        return self._encontrar_palabras(texto)

class DetectorIncentivo(BaseDetector):
    """Detector de incentivos sospechosos - hereda de BaseDetector"""
    
    def __init__(self):
        super().__init__()
        self.palabras_clave = [
            'premio', 'ganaste', 'regalo', 'sorteo', 'oferta especial',
            'descuento', 'promoción', 'bono', 'recompensa', 'gratuito',
            'gratis', 'beneficio', 'ventaja', 'oportunidad única'
        ]
        self.peso = 2
        self.categoria = "incentivo"
    
    def detectar(self, texto):
        return self._encontrar_palabras(texto)

class DetectorAmenaza(BaseDetector):
    """Detector de amenazas directas-hereda de BaseDetector"""
    
    def __init__(self):
        super().__init__()
        self.palabras_clave = [
            'suspenderemos', 'bloquearemos', 'eliminaremos', 'cancelaremos',
            'cerraremos', 'perderás', 'suspendido', 'bloqueado', 'eliminado',
            'cuenta eliminada', 'servicio suspendido', 'acceso denegado'
        ]
        self.peso = 3
        self.categoria = "amenaza"
    
    def detectar(self, texto):
        return self._encontrar_palabras(texto)

class DetectorFormato:
    """Detector de características de formato"""
    
    def __init__(self):
        self.peso_mayusculas = 1
        self.peso_exclamaciones = 1
        self.umbral_mayusculas = 0.3
        self.umbral_exclamaciones = 3
    
    def detectar_exceso_mayusculas(self, texto):
        mayusculas = sum(1 for c in texto if c.isupper())
        minusculas = sum(1 for c in texto if c.islower())
        total_letras = mayusculas + minusculas
        
        if total_letras == 0:
            return False
        
        porcentaje = (mayusculas / total_letras)
        return porcentaje > self.umbral_mayusculas
    
    def detectar_exceso_exclamaciones(self, texto):
        return texto.count('!') > self.umbral_exclamaciones

class DetectorContenido:
    """Clase principal que coordina todos los detectores"""
    
    def __init__(self):
        self.detectores = [
            DetectorUrgencia(),
            DetectorAccionObligatoria(),
            DetectorIncentivo(),
            DetectorAmenaza()
        ]
        
        self.detector_formato = DetectorFormato()
    
    def analizar(self, texto):
        score_total = 0
        elementos_detectados = []
        categorias_activadas = []
        
        for detector in self.detectores:
            elementos = detector.detectar(texto)
            
            if elementos:
                score_detector = len(elementos) * detector.peso
                score_total += score_detector
                categorias_activadas.append(detector.categoria)
                
                elementos_detectados.extend([
                    {
                        'elemento': elemento,
                        'categoria': detector.categoria,
                        'peso': detector.peso
                    }
                    for elemento in elementos
                ])
        
        if self.detector_formato.detectar_exceso_mayusculas(texto):
            score_total += self.detector_formato.peso_mayusculas
            elementos_detectados.append({
                'elemento': 'exceso_mayusculas',
                'categoria': 'formato',
                'peso': self.detector_formato.peso_mayusculas
            })
            if 'formato' not in categorias_activadas:
                categorias_activadas.append('formato')
        
        if self.detector_formato.detectar_exceso_exclamaciones(texto):
            score_total += self.detector_formato.peso_exclamaciones
            elementos_detectados.append({
                'elemento': 'exceso_exclamaciones',
                'categoria': 'formato',
                'peso': self.detector_formato.peso_exclamaciones
            })
            if 'formato' not in categorias_activadas:
                categorias_activadas.append('formato')
        
        return {
            'score_total': score_total,
            'elementos_detectados': elementos_detectados,
            'categorias_activadas': categorias_activadas
        }

"""
SISTEMA DE PUNTUACION:

+2 puntos -> palabra de urgencia
+2 puntos -> acción obligatoria
+3 puntos -> amenaza directa
+2 puntos -> incentivo sospechoso
+1 punto -> exceso de mayúsculas
+1 punto -> múltiples signos de exclamación

CLASIFICACION FINAL:
0 - 2 puntos -> Seguro
3 - 5 puntos -> Sospechoso
6 o más -> Peligroso
"""