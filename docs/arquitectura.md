# 🏗️ Arquitectura de EduScan

## Modelo de Microservicios

EduScan utiliza una arquitectura de **microservicios** independientes y desacoplados:

### 1. API Gateway (Puerto 8000)
- **Responsabilidad**: Recibir peticiones del frontend y orquestar los demás servicios
- **Tecnología**: FastAPI
- **Endpoints**:
  - `POST /corregir` - Procesa un examen
  - `GET /health` - Verifica estado

### 2. Servicio de Procesamiento (Puerto 8001)
- **Responsabilidad**: Procesar imágenes, enderezar hojas, detectar preguntas
- **Tecnología**: OpenCV + FastAPI
- **Algoritmos**:
  - Detección de bordes (Canny)
  - Transformación de perspectiva
  - Segmentación de preguntas

### 3. Servicio de IA (Puerto 8002)
- **Responsabilidad**: Corregir exámenes usando IA generativa
- **Tecnología**: Google Gemini API (modelo 2.5-flash)
- **Cómo funciona**:
  1. Recibe la imagen del examen
  2. Gemini analiza las respuestas del alumno
  3. Calcula nota en escala 0-5
  4. Genera feedback automático

### ¿Por qué Gemini y no un modelo propio?
- ✅ No requiere entrenamiento previo
- ✅ Precisión excelente desde el día 1
- ✅ Soporta imágenes y texto
- ✅ Escalable sin infraestructura adicional

### 4. Servicio de Base de Datos (Puerto 8003)
- **Responsabilidad**: Almacenar resultados y configuraciones
- **Tecnología**: PostgreSQL

## Comunicación entre Servicios
Frontend → Gateway → Procesamiento → IA → Resultado
↓
Recorte de preguntas

text

## Ventajas de esta Arquitectura
- ✅ **Escalabilidad**: Cada servicio puede replicarse independientemente
- ✅ **Mantenibilidad**: Cambios en un servicio no afectan a los demás
- ✅ **Despliegue independiente**: Cada servicio tiene su propio ciclo de vida
- ✅ **Tolerancia a fallos**: Si un servicio falla, los demás siguen funcionando