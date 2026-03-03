class Analisis:
    """
    Clase que representa el resultado final del análisis de phishing.
    Modelo puro: solo almacena datos, sin lógica de análisis.
    """
    
    def __init__(self):
        """
        Inicializa el análisis con valores por defecto seguros.
        """
        self.score_total = 0
        self.nivel_riesgo = "Seguro"
        self.factores_detectados = []
        self.detalle_contenido = {}
        self.detalle_url = {}
        self.detalle_dominio = {}
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto a diccionario para fácil serialización.
        
        """
        return {
            'score_total': self.score_total,
            'nivel_riesgo': self.nivel_riesgo,
            'factores_detectados': self.factores_detectados,
            'detalle_contenido': self.detalle_contenido,
            'detalle_url': self.detalle_url,
            'detalle_dominio': self.detalle_dominio
        }
    
    def __str__(self) -> str:
        """
        Representación en cadena para debugging.
        
        """
        total_factores = len(self.factores_detectados)
        contenido_activado = "Sí" if self.detalle_contenido else "No"
        url_activada = "Sí" if self.detalle_url else "No"
        dominio_activada = "Sí" if self.detalle_dominio else "No"
        
        return (f"Análisis(score={self.score_total}, riesgo={self.nivel_riesgo}, "
                f"factores={total_factores}, contenido={contenido_activado}, "
                f"url={url_activada}, dominio={dominio_activada})")
    
    def get_score_total(self) -> int:
        """Retorna el score total del análisis."""
        return self.score_total
    
    def get_nivel_riesgo(self) -> str:
        """Retorna el nivel de riesgo."""
        return self.nivel_riesgo
    
    def get_factores_detectados(self) -> list:
        """Retorna la lista de factores detectados."""
        return self.factores_detectados
    
    def get_detalle_contenido(self) -> dict:
        """Retorna el detalle del análisis de contenido."""
        return self.detalle_contenido
    
    def get_detalle_url(self) -> dict:
        """Retorna el detalle del análisis de URLs."""
        return self.detalle_url
    
    def get_detalle_dominio(self) -> dict:
        """Retorna el detalle del análisis de dominios."""
        return self.detalle_dominio
