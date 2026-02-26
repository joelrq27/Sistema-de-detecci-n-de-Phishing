from services.detector_contenido import DetectorContenido
from services.detector_dominio import FinancialDomainChecker
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
        
        # 5. Formatear y agregar todos los factores detectados
        elementos_contenido_formateados = self._formatear_elementos(resultado_contenido['elementos_detectados'])
        elementos_urls_formateados = self._formatear_elementos(resultado_urls['elementos_urls'])
        elementos_dominios_formateados = self._formatear_elementos(resultado_dominios['elementos_dominios'])
        
        analisis.factores_detectados.extend(elementos_contenido_formateados)
        analisis.factores_detectados.extend(elementos_urls_formateados)
        analisis.factores_detectados.extend(elementos_dominios_formateados)
        
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
            # Verificar si ya tiene la estructura correcta (URLs y dominios)
            if 'tipo' in elemento and 'elemento' in elemento and 'peso' in elemento and 'descripcion' in elemento:
                # Ya está formateado, agregar explicación detallada
                elemento_formateado = {
                    'tipo': elemento['tipo'],
                    'elemento': elemento['elemento'],
                    'peso': elemento['peso'],
                    'descripcion': elemento['descripcion'],
                    'explicacion': self._generar_explicacion(elemento)
                }
                elementos_formateados.append(elemento_formateado)
            else:
                # Viene del detector_contenido, necesita formateo
                elemento_formateado = {
                    'tipo': elemento['categoria'],
                    'elemento': elemento['elemento'],
                    'peso': elemento['peso'],
                    'descripcion': self._generar_descripcion(elemento),
                    'explicacion': self._generar_explicacion(elemento)
                }
                elementos_formateados.append(elemento_formateado)
        
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
    
    def _generar_explicacion(self, elemento):
        """
        Genera una explicación detallada para cada elemento detectado
        """
        categoria = elemento.get('categoria', elemento.get('tipo', ''))
        elemento_texto = elemento.get('elemento', '')
        
        explicaciones = {
            'urgencia': f"Se detectó la palabra '{elemento_texto.upper()}' que los phishers usan para presionarte a actuar sin pensar.",
            'accion_obligatoria': f"El mensaje usa '{elemento_texto}' para forzarte a realizar una acción inmediata, una táctica común de phishing.",
            'incentivo': f"Se ofrece '{elemento_texto}' como incentivo para que bajes la guardia y compartas información.",
            'amenaza': f"El mensaje menciona '{elemento_texto}', una táctica de intimidación para generar miedo y urgencia.",
            'formato': f"Se detectó un problema de formato: '{elemento_texto}', común en correos fraudulentos.",
            'url': f"El mensaje contiene enlaces que podrían llevar a sitios maliciosos.",
            'dominio': f"Se detectó un dominio sospechoso que intenta imitar una entidad legítima."
        }
        
        return explicaciones.get(
            categoria,
            f"Se detectó un elemento sospechoso: '{elemento_texto}' que requiere atención."
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
        
        """
        # Usar funciones del módulo detector_url
        urls = extraer_urls(texto)
        score_urls = 0
        elementos_urls = []
        detalles_urls = []
        
        # +1 si hay al menos 1 URL
        if len(urls) > 0:
            score_urls += 1
            elementos_urls.append({
                'tipo': 'url',
                'elemento': 'presencia_urls',
                'peso': 1,
                'descripcion': f'Se detectaron {len(urls)} URLs en el mensaje',
                'detalles': {
                    'tipo_detalle': 'presencia',
                    'valor': f'{len(urls)} URLs',
                    'texto': f'Presencia de {len(urls)} URL(s) en el mensaje'
                }
            })
        
        # +2 por cada URL inválida
        for url in urls:
            if not es_url_valida(url):
                score_urls += 2
                elementos_urls.append({
                    'tipo': 'url',
                    'elemento': 'url_invalida',
                    'peso': 2,
                    'descripcion': f'URL inválida detectada: {url}',
                    'detalles': {
                        'tipo_detalle': 'invalida',
                        'valor': url,
                        'texto': f'URL inválida: {url}'
                    }
                })
                detalles_urls.append({
                    'tipo': 'invalida',
                    'url': url,
                    'peso': 2
                })
        
        # +2 por cada URL acortada
        for url in urls:
            if es_url_acortada(url):
                score_urls += 2
                elementos_urls.append({
                    'tipo': 'url',
                    'elemento': 'url_acortada',
                    'peso': 2,
                    'descripcion': f'URL acortada sospechosa: {url}',
                    'detalles': {
                        'tipo_detalle': 'acortada',
                        'valor': url,
                        'texto': f'URL acortada: {url}'
                    }
                })
                detalles_urls.append({
                    'tipo': 'acortada',
                    'url': url,
                    'peso': 2
                })
        
        return {
            'urls': urls,
            'score_urls': score_urls,
            'elementos_urls': elementos_urls,
            'detalles_urls': detalles_urls
        }
    
    def _analizar_dominios(self, urls):
        """
        Analiza los dominios de las URLs y calcula su score
        
        SCORE DOMINIO:
        +3 si imita dominio financiero oficial
        
        """
        score_dominios = 0
        elementos_dominios = []
        detalles_dominios = []
        
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
                        'descripcion': f'Dominio sospechoso que imita entidad financiera: {dominio}',
                        'detalles': {
                            'tipo_detalle': 'sospechoso',
                            'valor': dominio,
                            'texto': f'Dominio sospechoso: {dominio}'
                        }
                    })
                    detalles_dominios.append({
                        'tipo': 'sospechoso',
                        'dominio': dominio,
                        'peso': 3
                    })
                
                # Nota: dominios financieros oficiales no suman puntos (0 puntos)
                
            except Exception as e:
                # Si hay error al parsear la URL, lo ignoramos
                continue
        
        return {
            'score_dominios': score_dominios,
            'elementos_dominios': elementos_dominios,
            'detalles_dominios': detalles_dominios
        }
