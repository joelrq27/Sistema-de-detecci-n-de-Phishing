from services.detector_contenido import DetectorContenido
from services.detector_dominio import URLAnalyzer, FinancialDomainChecker
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
    
    def analizar_mensaje(self, texto):
        """
        Funcion principal que analiza un mensaje completo
        
        Returns:
            Dict con:
            - risk_level: str - 'Seguro', 'Sospechoso', 'Peligroso'
            - detected_elements: List[Dict] - Elementos detectados con detalles
            - score: int - Puntuación total
            - links_detected: List[str] - URLs encontradas
        """
        # 1. Análisis de contenido
        resultado_contenido = self.detector_contenido.analizar(texto)
        score = resultado_contenido['score_total']
        
        # 2. Análisis de URLs
        resultado_urls = self._analizar_urls(texto)
        score_urls = resultado_urls['score_urls']
        score += score_urls
        
        # 3. Análisis de dominios
        resultado_dominios = self._analizar_dominios(resultado_urls['urls'])
        score_dominios = resultado_dominios['score_dominios']
        score += score_dominios
        
        # 4. Determinar nivel de riesgo
        risk_level = self._determinar_nivel_riesgo(score)
        
        # 5. Formatear elementos detectados
        detected_elements = self._formatear_elementos(
            resultado_contenido['elementos_detectados']
        )
        
        # 6. Agregar elementos de URLs y dominios
        detected_elements.extend(resultado_urls['elementos_urls'])
        detected_elements.extend(resultado_dominios['elementos_dominios'])
        
        # 7. URLs detectadas para el campo links_detected
        links_detected = resultado_urls['urls']
        
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
        analyzer = URLAnalyzer(texto)
        resultado = analyzer.analizar()
        
        urls = resultado['urls']
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
        for url_invalida in resultado['urls_invalidas']:
            score_urls += 2
            elementos_urls.append({
                'tipo': 'url',
                'elemento': 'url_invalida',
                'peso': 2,
                'descripcion': f'URL inválida detectada: {url_invalida}'
            })
        
        # +2 por cada URL acortada
        for url_acortada in resultado['urls_acortadas']:
            score_urls += 2
            elementos_urls.append({
                'tipo': 'url',
                'elemento': 'url_acortada',
                'peso': 2,
                'descripcion': f'URL acortada sospechosa: {url_acortada}'
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
