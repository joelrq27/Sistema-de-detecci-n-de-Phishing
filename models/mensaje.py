class Mensaje:
    """
    Clase que representa un mensaje para análisis de phishing.
    Sigue el principio de responsabilidad única: solo almacena el contenido.
    """
    
    def __init__(self, contenido: str):
        """
        Inicializa el mensaje con su contenido.
        
        Args:
            contenido (str): El texto del mensaje a analizar
        """
        self.contenido = contenido if contenido else ""
    
    def get_contenido(self) -> str:
        """
        Retorna el contenido del mensaje.
        
        Returns:
            str: El texto del mensaje
        """
        return self.contenido
    
    def esta_vacio(self) -> bool:
        """
        Indica si el mensaje está vacío o solo contiene espacios en blanco.
        
        Returns:
            bool: True si está vacío, False si tiene contenido
        """
        return not self.contenido.strip()
    
    def __str__(self) -> str:
        """
        Representación en cadena del objeto.
        
        Returns:
            str: Representación del mensaje
        """
        if self.esta_vacio():
            return "Mensaje(vacío)"
        
        # Mostrar primeros 50 caracteres para vista previa
        preview = self.contenido[:50] + ("..." if len(self.contenido) > 50 else "")
        return f"Mensaje('{preview}')"
