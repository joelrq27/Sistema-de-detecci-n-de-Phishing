import difflib
from typing import List, Tuple

def calcular_similitud(texto1: str, texto2: str) -> float:
    """
    Calcula la similitud entre dos textos usando difflib.
    
    float: Valor entre 0.0 y 1.0 (0 = nada similar, 1 = idéntico)
    """
    return difflib.SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

def encontrar_similares(texto: str, lista_textos: List[str], umbral: float = 0.8) -> List[Tuple[str, float]]:
    """
    Encuentra textos similares en una lista.
    
    """
    similares = []
    
    for texto_lista in lista_textos:
        similitud = calcular_similitud(texto, texto_lista)
        if similitud >= umbral:
            similares.append((texto_lista, similitud))
    
    # Ordenar por similitud descendente
    similares.sort(key=lambda x: x[1], reverse=True)
    return similares

def es_similitud_alta(texto1: str, texto2: str, umbral: float = 0.8) -> bool:
    """
    Determina si dos textos tienen alta similitud.
    
    umbral (float): Umbral de similitud (default 0.8)
   
    """
    return calcular_similitud(texto1, texto2) >= umbral

def normalizar_dominio(dominio: str) -> str:
    """
    Normaliza un dominio para comparación.
    
    """
    # Eliminar protocolo
    if '://' in dominio:
        dominio = dominio.split('://')[1]
    
    # Eliminar www
    if dominio.startswith('www.'):
        dominio = dominio[4:]
    
    # Eliminar puertos
    if ':' in dominio:
        dominio = dominio.split(':')[0]
    
    return dominio.lower().strip()

def extraer_nombre_base(dominio: str) -> str:
    """
    Extrae el nombre base de un dominio (sin TLD).
    
    """
    dominio_normalizado = normalizar_dominio(dominio)
    partes = dominio_normalizado.split('.')
    
    # Retornar la primera parte (ej: viabcp.com -> viabcp)
    return partes[0] if partes else dominio_normalizado
