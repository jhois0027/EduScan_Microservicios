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
- **Responsabilidad**: Clasificar respuestas usando Deep Learning
- **Tecnología**: TensorFlow / Red Neuronal Convolucional
- **Arquitectura del modelo**:
  - Capa Conv2D (32 filtros, 3x3)
  - Capa MaxPooling2D
  - Capa Conv2D (64 filtros, 3x3)
  - Capa MaxPooling2D
  - Capa Flatten
  - Capa Dense (128 neuronas)
  - Capa Dense (4 neuronas, salida A/B/C/D)

### 4. Servicio de Base de Datos (Puerto 8003)
- **Responsabilidad**: Almacenar resultados y configuraciones
- **Tecnología**: PostgreSQL (futuro)

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