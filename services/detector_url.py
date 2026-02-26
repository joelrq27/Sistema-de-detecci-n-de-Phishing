import re
from urllib.parse import urlparse

# Lista de acortadores de URL comunes en phishing
ACORTADORES_SOSPECHOSOS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly"
]

def extraer_urls(texto: str):
    """
    Extrae todas las URLs del texto usando expresiones regulares.
    Retorna una lista de URLs encontradas.
    """
    # Patrón unificado para detectar todos los tipos de URLs sin duplicados
    # Detecta: http://dominio.com, https://dominio.com, bit.ly/xyz, www.ejemplo.com, ejemplo.com/ruta
    patron_unificado = r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?(?<!://)'
    
    # Detectar protocolos incompletos (http:// sin dominio)
    patron_incompleto = r'https?://(?=\s|$)'
    
    urls_completas = re.findall(patron_unificado, texto)
    urls_incompletas = re.findall(patron_incompleto, texto)
    
    # Combinar resultados eliminando duplicados manteniendo el orden
    todas_urls = []
    seen = set()
    
    # Agregar URLs incompletas primero
    for url in urls_incompletas:
        if url not in seen:
            seen.add(url)
            todas_urls.append(url)
    
    # Agregar URLs completas
    for url in urls_completas:
        if url not in seen:
            seen.add(url)
            todas_urls.append(url)
    
    # Normalizar URLs sin protocolo agregando http://
    urls_normalizadas = []
    for url in todas_urls:
        if not url.startswith(('http://', 'https://')):
            url_normalizada = 'http://' + url
        else:
            url_normalizada = url
        urls_normalizadas.append(url_normalizada)
    
    return urls_normalizadas


def es_url_valida(url: str) -> bool:
    """
    Verifica si una URL tiene estructura válida.
    """
    try:
        resultado = urlparse(url)
        
        # Verificar que tenga esquema y netloc
        if not all([resultado.scheme, resultado.netloc]):
            return False
        
        # Verificar que el netloc tenga al menos un punto y no esté vacío
        netloc = resultado.netloc
        if not netloc or '.' not in netloc:
            return False
            
        # Verificar que no sea solo http:// o https:// sin dominio
        if netloc in ['', 'http', 'https']:
            return False
            
        return True
    except:
        return False


def es_url_acortada(url: str) -> bool:
    """
    Detecta si la URL usa un servicio de acortamiento.
    """
    dominio = urlparse(url).netloc.lower()
    for acortador in ACORTADORES_SOSPECHOSOS:
        if acortador in dominio:
            return True
    return False


def analizar_urls(texto: str):
    """
    Analiza las URLs del mensaje y devuelve un diccionario con resultados.
    """
    urls = extraer_urls(texto)

    resultado = {
        "total_urls": len(urls),
        "urls": urls,
        "urls_invalidas": [],
        "urls_acortadas": []
    }

    for url in urls:
        if not es_url_valida(url):
            resultado["urls_invalidas"].append(url)

        if es_url_acortada(url):
            resultado["urls_acortadas"].append(url)

    return resultado

