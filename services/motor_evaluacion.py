from services.detector_contenido import DetectorContenido
from services.detector_dominio import URLAnalyzer, FinancialDomainChecker
from services.detector_url import extraer_urls, es_url_valida, es_url_acortada
from models.mensaje import Mensaje
from models.analisis import Analisis
from urllib.parse import urlparse

class MotorEvaluacion:
    """
    Clase principal que coordina el análisis completo de mensajes
    Implementa el patrón de diseño Facade para simplificar la interfaz
    """
    
    def __init__(self):
        self.detector_contenido = DetectorContenido()
        self.domain_checker = FinancialDomainChecker()
        
        self.umbrales = {
            'seguro_max': 2,
            'sospechoso_max': 5
        }
    
    def analizar_mensaje(self, mensaje: Mensaje) -> Analisis:
        """
        Función principal que analiza un mensaje completo usando objetos modelo
        
        Args:
            mensaje (Mensaje): Objeto Mensaje a analizar
            
        Returns:
            Analisis: Objeto con el resultado completo del análisis
        """
        # Crear objeto de análisis
        analisis = Analisis()
        
        # Verificar si el mensaje está vacío
        if mensaje.esta_vacio():
            return analisis
        
        texto = mensaje.get_contenido()
        
        # 1. Análisis de contenido
        resultado_contenido = self.detector_contenido.analizar(texto)
        analisis.detalle_contenido = resultado_contenido
        analisis.score_total += resultado_contenido['score_total']
        
        # 2. Análisis de URLs
        resultado_urls = self._analizar_urls(texto)
        analisis.detalle_url = resultado_urls
        analisis.score_total += resultado_urls['score_urls']
        
        # 3. Análisis de dominios
        resultado_dominios = self._analizar_dominios(resultado_urls['urls'])
        analisis.detalle_dominio = resultado_dominios
        analisis.score_total += resultado_dominios['score_dominios']
        
        # 4. Determinar nivel de riesgo
        analisis.nivel_riesgo = self._determinar_nivel_riesgo(analisis.score_total)
        
        # 5. Agregar todos los factores detectados
        analisis.factores_detectados.extend(resultado_contenido['elementos_detectados'])
        analisis.factores_detectados.extend(resultado_urls['elementos_urls'])
        analisis.factores_detectados.extend(resultado_dominios['elementos_dominios'])
        
        return analisis
    
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
            'formato': f"Problema de formato detectado: '{elemento_texto}'",
            'url': f"URL sospechosa detectada: '{elemento_texto}'",
            'dominio': f"Dominio sospechoso detectado: '{elemento_texto}'"
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
    
    def _analizar_urls(self, texto):
        """
        Analiza las URLs del texto y calcula su score
        
        SCORE URL:
        +1 si hay URLs
        +2 por URL inválida
        +2 por URL acortada
        
        Returns:
            Dict con urls, score_urls y elementos_urls
        """
        # Usar funciones del módulo detector_url
        urls = extraer_urls(texto)
        score_urls = 0
        elementos_urls = []
        
        # +1 si hay al menos 1 URL
        if len(urls) > 0:
            score_urls += 1
            elementos_urls.append({
                'tipo': 'url',
                'elemento': 'presencia_urls',
                'peso': 1,
                'descripcion': f'Se detectaron {len(urls)} URLs en el mensaje'
            })
        
        # +2 por cada URL inválida
        for url in urls:
            if not es_url_valida(url):
                score_urls += 2
                elementos_urls.append({
                    'tipo': 'url',
                    'elemento': 'url_invalida',
                    'peso': 2,
                    'descripcion': f'URL inválida detectada: {url}'
                })
        
        # +2 por cada URL acortada
        for url in urls:
            if es_url_acortada(url):
                score_urls += 2
                elementos_urls.append({
                    'tipo': 'url',
                    'elemento': 'url_acortada',
                    'peso': 2,
                    'descripcion': f'URL acortada sospechosa: {url}'
                })
        
        return {
            'urls': urls,
            'score_urls': score_urls,
            'elementos_urls': elementos_urls
        }
    
    def _analizar_dominios(self, urls):
        """
        Analiza los dominios de las URLs y calcula su score
        
        SCORE DOMINIO:
        +3 si imita dominio financiero oficial
        
        Returns:
            Dict con score_dominios y elementos_dominios
        """
        score_dominios = 0
        elementos_dominios = []
        
        for url in urls:
            try:
                dominio = urlparse(url).netloc.lower()
                
                # Eliminar www. si existe
                if dominio.startswith('www.'):
                    dominio = dominio[4:]
                
                # Verificar si es dominio sospechoso que imita banco
                if self.domain_checker.es_dominio_sospechoso(dominio):
                    score_dominios += 3
                    elementos_dominios.append({
                        'tipo': 'dominio',
                        'elemento': 'dominio_sospechoso',
                        'peso': 3,
                        'descripcion': f'Dominio sospechoso que imita entidad financiera: {dominio}'
                    })
                
                # Nota: dominios financieros oficiales no suman puntos (0 puntos)
                
            except Exception as e:
                # Si hay error al parsear la URL, lo ignoramos
                continue
        
        return {
            'score_dominios': score_dominios,
            'elementos_dominios': elementos_dominios
        }
