import re
from urllib.parse import urlparse
from utils.similitud import calcular_similitud, normalizar_dominio, extraer_nombre_base


class URLValidator:
    ACORTADORES_SOSPECHOSOS = [
        "bit.ly", "tinyurl.com", "t.co",
        "goo.gl", "is.gd", "buff.ly"
    ]

    def __init__(self, url: str):
        self.url = url
        self.parsed = urlparse(url)

    def es_valida(self) -> bool:
        """
        Verifica si la URL tiene estructura válida.
        """
        return all([self.parsed.scheme, self.parsed.netloc])

    def es_acortada(self) -> bool:
        """
        Detecta si la URL usa un servicio de acortamiento.
        """
        dominio = self.parsed.netloc.lower()
        return any(acortador in dominio for acortador in self.ACORTADORES_SOSPECHOSOS)


class URLExtractor:
    def __init__(self, texto: str):
        self.texto = texto

    def extraer(self):
        """
        Extrae todas las URLs del texto.
        """
        patron = r'https?://[^\s]+'
        return re.findall(patron, self.texto)


class URLAnalyzer:
    def __init__(self, texto: str):
        self.texto = texto
        self.extractor = URLExtractor(texto)

    def analizar(self):
        urls = self.extractor.extraer()

        resultado = {
            "total_urls": len(urls),
            "urls": urls,
            "urls_invalidas": [],
            "urls_acortadas": []
        }

        for url in urls:
            validator = URLValidator(url)

            if not validator.es_valida():
                resultado["urls_invalidas"].append(url)

            if validator.es_acortada():
                resultado["urls_acortadas"].append(url)

        return resultado


class FinancialDomainChecker:
    def __init__(self):
        self.dominios_financieros_peru = [
            "viabcp.com",
            "interbank.pe",
            "bbva.pe",
            "scotiabank.com.pe",
            "bancom.pe",
            "banbif.com.pe",
            "mibanco.com.pe",
            "pichincha.pe",
            "yape.com.pe",
            "prima.com.pe",
        ]
        
        # Lista de marcas populares comúnmente usadas en phishing
        self.marcas_populares = [
            "netflix.com", "amazon.com", "facebook.com", "instagram.com", 
            "twitter.com", "x.com", "whatsapp.com", "gmail.com", "outlook.com",
            "hotmail.com", "yahoo.com", "microsoft.com", "apple.com", 
            "google.com", "youtube.com", "tiktok.com", "linkedin.com",
            "paypal.com", "ebay.com", "mercadolibre.com", "mercado libre"
        ]
    
    def es_dominio_financiero_oficial(self, dominio: str) -> bool:
        """
        Verifica si el dominio es un dominio financiero oficial.
        """
        dominio_normalizado = normalizar_dominio(dominio)
        
        for oficial in self.dominios_financieros_peru:
            if dominio_normalizado == normalizar_dominio(oficial):
                return True
        return False
    
    def es_marca_oficial(self, dominio: str) -> bool:
        """
        Verifica si el dominio es un dominio oficial de una marca popular.
        """
        dominio_normalizado = normalizar_dominio(dominio)
        
        for marca in self.marcas_populares:
            if dominio_normalizado == normalizar_dominio(marca):
                return True
        return False
    
    def es_dominio_sospechoso(self, dominio: str) -> bool:
        """
        Reglas:
        1. Si el dominio contiene el nombre de un banco oficial pero no coincide exactamente → marcar como sospechoso.
        2. Si el dominio contiene el nombre de una marca popular pero no es el dominio oficial → marcar como sospechoso.
        
        Ejemplos:
        - Oficial: viabcp.com → Sospechoso: viabcp-secure-login.com
        - Oficial: netflix.com → Sospechoso: netflix-verificacion.com
        
        También detecta por similitud (>80%)
        """
        dominio_normalizado = normalizar_dominio(dominio)
        
        # Si es oficial (financiero o marca), no es sospechoso
        if self.es_dominio_financiero_oficial(dominio_normalizado):
            return False
        
        if self.es_marca_oficial(dominio_normalizado):
            return False
        
        # Verificar dominios financieros sospechosos
        for oficial in self.dominios_financieros_peru:
            nombre_base = oficial.split('.')[0]
            if nombre_base in dominio_normalizado:
                return True
        
        # Verificar marcas populares sospechosas
        for marca in self.marcas_populares:
            nombre_base = marca.split('.')[0]
            if nombre_base in dominio_normalizado:
                return True
        
        # Detección por similitud (>80%) para financieros
        for oficial in self.dominios_financieros_peru:
            similitud = calcular_similitud(dominio_normalizado, normalizar_dominio(oficial))
            if similitud > 0.8:
                return True
        
        # Detección por similitud (>80%) para marcas populares
        for marca in self.marcas_populares:
            similitud = calcular_similitud(dominio_normalizado, normalizar_dominio(marca))
            if similitud > 0.8:
                return True
        
        return False


if __name__ == "__main__":

    checker = FinancialDomainChecker()
    texto_prueba = checker.convertir_a_urls()

    analyzer = URLAnalyzer(texto_prueba)
    resultado = analyzer.analizar()

    print("===================================")
    print("RESULTADO DEL ANÁLISIS")
    print("===================================")
    print(f"Total URLs analizadas: {resultado['total_urls']}")
    print(f"URLs inválidas: {resultado['urls_invalidas']}")
    print(f"URLs acortadas: {resultado['urls_acortadas']}")

