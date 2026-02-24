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
            "afpintegra.pe",
            "bvl.com.pe",
            "cavali.com.pe",
            "cencosudscotia.com.pe"
        ]

    def convertir_a_urls(self):
        """
        Convierte los dominios a URLs HTTPS.
        """
        return "\n".join([f"https://{dominio}" for dominio in self.dominios_financieros_peru])
    
    def es_dominio_financiero_oficial(self, dominio: str) -> bool:
        """
         Devuelve True si el dominio coincide exactamente
         o es un subdominio legítimo de un dominio financiero oficial.
        """
        dominio_normalizado = dominio.lower().strip()

        for oficial in self.dominios_financieros_peru:
            # Coincidencia exacta
            if dominio_normalizado == oficial:
                return True
        
            # Permitir subdominios legítimos (ej: login.viabcp.com)
            if dominio_normalizado.endswith("." + oficial):
                return True
        
        return False
    
    def es_dominio_sospechoso(self, dominio: str) -> bool:
        """
        Reglas:
        Si el dominio contiene el nombre de un banco oficial pero no coincide exactamente con el dominio oficial → marcar como sospechoso.
        
        Ejemplo:
        Oficial: viabcp.com
        Sospechoso: viabcp-secure-login.com
        
        AGREGADO: También detecta por similitud (>80%)
        """
        dominio_normalizado = normalizar_dominio(dominio)
        
        # Si es oficial, no es sospechoso
        if self.es_dominio_financiero_oficial(dominio_normalizado):
            return False
        
        # Verificar si contiene el nombre de algún banco oficial pero no es exacto
        for oficial in self.dominios_financieros_peru:
            # Extraer el nombre base del dominio oficial (sin .com, .pe, etc.)
            nombre_base = oficial.split('.')[0]
            
            # Si el dominio contiene el nombre base pero no es exactamente el oficial
            if nombre_base in dominio_normalizado:
                return True
        
        # AGREGADO: Detección por similitud (>80%)
        for oficial in self.dominios_financieros_peru:
            similitud = calcular_similitud(dominio_normalizado, oficial)
            if similitud > 0.8:  # Umbral del 80%
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

