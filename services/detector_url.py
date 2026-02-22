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
    patron = r'https?://[^\s]+'   # http o https hasta espacio
    urls = re.findall(patron, texto)
    return urls


def es_url_valida(url: str) -> bool:
    """
    Verifica si una URL tiene estructura válida.
    """
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
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

