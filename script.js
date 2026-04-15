const API_URL = 'http://localhost:8000';
const DB_API_URL = 'http://localhost:8003';

let imagenActual = null;
let stream = null;
let respuestasCorreccion = null;

// Elementos
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const camaraBtn = document.getElementById('modoCamaraBtn');
const galeriaBtn = document.getElementById('modoGaleriaBtn');
const previewContainer = document.getElementById('previewContainer');
const preview = document.getElementById('preview');
const corregirBtn = document.getElementById('corregirBtn');
const resultados = document.getElementById('resultados');
const loading = document.getElementById('loading');
const nuevoBtn = document.getElementById('nuevoBtn');
const cancelarBtn = document.getElementById('cancelarBtn');
const guardarBtn = document.getElementById('guardarBtn');
const cameraContainer = document.getElementById('cameraContainer');
const uploadContainer = document.getElementById('uploadContainer');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const capturarBtn = document.getElementById('capturarBtn');
const cancelarCamaraBtn = document.getElementById('cancelarCamaraBtn');
const alumnoSelect = document.getElementById('alumnoSelect');

// Cargar alumnos
async function cargarAlumnos() {
    try {
        const response = await fetch(`${DB_API_URL}/alumnos`);
        const data = await response.json();
        alumnoSelect.innerHTML = '<option value="">-- Seleccione un alumno --</option>' +
            data.alumnos.map(a => `<option value="${a.id_alumno}" data-nombre="${a.nombre}">${a.nombre}</option>`).join('');
    } catch (error) {
        console.error('Error cargando alumnos:', error);
    }
}

// Abrir cámara
async function abrirCamara() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        video.srcObject = stream;
        cameraContainer.style.display = 'block';
        uploadContainer.style.display = 'none';
        previewContainer.style.display = 'none';
    } catch (error) {
        alert('No se pudo acceder a la cámara. Verifica los permisos.');
    }
}

function cerrarCamara() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    video.srcObject = null;
    cameraContainer.style.display = 'none';
    uploadContainer.style.display = 'block';
}

function capturarFoto() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob(blob => {
        imagenActual = new File([blob], 'examen.jpg', { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        preview.src = url;
        previewContainer.style.display = 'block';
        cerrarCamara();
        uploadContainer.style.display = 'none';
    }, 'image/jpeg', 0.9);
}

// Subir imagen
uploadArea.onclick = () => fileInput.click();
fileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        imagenActual = file;
        const reader = new FileReader();
        reader.onload = (event) => {
            preview.src = event.target.result;
            previewContainer.style.display = 'block';
            uploadContainer.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
};

// Cambiar modo
camaraBtn.onclick = () => {
    camaraBtn.classList.add('active');
    galeriaBtn.classList.remove('active');
    abrirCamara();
};

galeriaBtn.onclick = () => {
    galeriaBtn.classList.add('active');
    camaraBtn.classList.remove('active');
    uploadContainer.style.display = 'block';
    cameraContainer.style.display = 'none';
};

cancelarCamaraBtn.onclick = cerrarCamara;
capturarBtn.onclick = capturarFoto;
cancelarBtn.onclick = () => {
    imagenActual = null;
    preview.src = '';
    previewContainer.style.display = 'none';
    uploadContainer.style.display = 'block';
    resultados.style.display = 'none';
};

// Corregir examen
corregirBtn.onclick = async () => {
    if (!imagenActual) {
        alert('Selecciona o toma una foto primero');
        return;
    }
    
    loading.style.display = 'block';
    previewContainer.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', imagenActual);
    
    try {
        const response = await fetch(`${API_URL}/corregir`, { method: 'POST', body: formData });
        const data = await response.json();
        
        if (response.ok) {
            respuestasCorreccion = data;
            
            document.getElementById('notaValor').textContent = data.nota_final.toFixed(1);
            document.getElementById('correctas').textContent = data.correctas;
            document.getElementById('incorrectas').textContent = data.incorrectas;
            
            const detalleHtml = data.respuestas_alumno.map((puntaje, idx) => {
                const esAprobado = puntaje >= 3.0;
                return `
                    <div class="detalle-item ${esAprobado ? 'aprobado' : 'reprobado'}">
                        <span>Pregunta ${idx + 1}</span>
                        <span>Puntaje: ${puntaje.toFixed(1)} / 5.0</span>
                        <span>${esAprobado ? '✅' : '❌'}</span>
                    </div>
                `;
            }).join('');
            
            document.getElementById('detalleLista').innerHTML = detalleHtml;
            resultados.style.display = 'block';
        } else {
            alert('Error al corregir: ' + JSON.stringify(data));
        }
    } catch (error) {
        alert('Error al conectar con el servidor');
    } finally {
        loading.style.display = 'none';
    }
};

// Guardar calificación
guardarBtn.onclick = async () => {
    const alumnoId = alumnoSelect.value;
    if (!alumnoId) {
        alert('Selecciona un alumno primero');
        return;
    }
    
    if (!respuestasCorreccion) {
        alert('Primero corrige un examen');
        return;
    }
    
    const alumnoOption = alumnoSelect.options[alumnoSelect.selectedIndex];
    const alumnoNombre = alumnoOption.getAttribute('data-nombre');
    
    const hoy = new Date().toISOString().split('T')[0];
    
    const evaluacion = {
        id_alumno: parseInt(alumnoId),
        puntaje: respuestasCorreccion.nota_final,
        fecha: hoy,
        respuestas: respuestasCorreccion.respuestas_alumno.map((p, i) => ({
            id_pregunta: i + 1,
            es_correcta: p >= 3.0
        }))
    };
    
    try {
        const response = await fetch(`${DB_API_URL}/nueva_evaluacion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(evaluacion)
        });
        
        if (response.ok) {
            alert('✅ Calificación guardada exitosamente');
            nuevoBtn.click();
        } else {
            alert('Error al guardar');
        }
    } catch (error) {
        alert('Error al conectar con el servidor');
    }
};

nuevoBtn.onclick = () => {
    imagenActual = null;
    respuestasCorreccion = null;
    fileInput.value = '';
    preview.src = '';
    previewContainer.style.display = 'none';
    resultados.style.display = 'none';
    uploadContainer.style.display = 'block';
    camaraBtn.classList.add('active');
    galeriaBtn.classList.remove('active');
    if (stream) cerrarCamara();
};

// Inicializar
cargarAlumnos();
