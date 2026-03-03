# 🛡️ Sistema de Detección de Phishing

Herramienta de análisis especializada en la detección de mensajes de phishing mediante evaluación de contenido, URLs y dominios sospechosos. Diseñada para identificar tácticas comunes de ingeniería social y proporcionar una puntuación de riesgo clara.

##  Características Principales

- **Análisis de Contenido**: Detección de palabras de urgencia, acciones obligatorias e incentivos sospechosos
- **Análisis de URLs**: Identificación de protocolos inseguros, URLs acortadas y estructuras inválidas
- **Análisis de Dominios**: Detección de dominios que imitan marcas conocidas (bancos, Netflix, Amazon, etc.)
- **Sistema de Puntuación**: Score con clasificación por niveles de riesgo (0-2 Seguro, 3-5 Sospechoso, 6+ Peligroso)
- **Interfaz Web**: Panel de control intuitivo con visualización detallada de amenazas

##  Tecnologías Utilizadas

- **Backend**: Python 3.x con Flask
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Análisis**: Expresiones regulares y algoritmos de similitud
- **UI/UX**: Font Awesome para iconos, diseño oscuro profesional

##  Instalación

### Prerrequisitos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/joelrq27/Sistema-de-detecci-n-de-Phishing
   cd Sistema-de-detecci-n-de-Phishing
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

4. **Acceder a la aplicación**
   
   Abre tu navegador y navega a `http://127.0.0.1:5000`

## Guía de Uso

### Análisis Básico
1. Ingresa el mensaje sospechoso en el campo de texto
2. Haz clic en "Analizar Mensaje"
3. Revisa los resultados en el panel de detección

### Interpretación de Resultados

- **Score 0-2**: ✅ Seguro - Baja probabilidad de phishing
- **Score 3-5**: ⚠️ Sospechoso - Requiere revisión cuidadosa
- **Score 6+**: 🚨 Peligroso - Alta probabilidad de phishing

### Elementos Detectados
- **Contenido**: Palabras de urgencia, acciones obligatorias, incentivos
- **URLs**: Protocolos inseguros (HTTP), URLs acortadas, estructuras inválidas
- **Dominios**: Imitación de marcas conocidas, similitud con dominios oficiales

## 📁 Estructura del Proyecto

```
phishing-detector/
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias del proyecto
├── models/                         # Modelos de datos
│   ├── mensaje.py                  # Modelo para mensajes
│   └── analisis.py                 # Modelo para resultados
├── services/                       # Lógica de análisis
│   ├── detector_url.py             # Detección de URLs
│   ├── detector_dominio.py         # Detección de dominios
│   └── motor_evaluacion.py         # Motor principal de evaluación
├── utils/                          # Utilidades
│   └── similitud.py                # Algoritmos de similitud
└── templates/                      # Plantillas web
    ├── index.html                  # Página principal
    └── resultado.html              # Página de resultados
```

##  Configuración

La aplicación se ejecuta por defecto en:
- **Puerto**: 5000
- **Host**: 127.0.0.1 (localhost)
- **Modo Debug**: Activado para desarrollo

## 📊 Métricas de Detección

El sistema evalúa múltiples factores:

| Categoría | Elementos Detectados | Peso |
|-----------|---------------------|------|
| Contenido | Urgencia, acciones, incentivos | Variable |
| URLs | Protocolo inseguro, acortadas, inválidas | +2 cada una |
| Dominios | Imitación de marcas, similitud >80% | +3 cada uno |

##  Autores

- 
-
-

---

**Nota**: Esta herramienta es una ayuda en la detección de phishing, no reemplaza el juicio humano.