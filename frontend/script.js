const API_URL = 'http://192.168.1.36:8000';
const DB_API_URL = 'http://192.168.1.36:8003';

let imagenActual = null;
let stream = null;
let respuestasCorreccion = null;

const alumnoSelect = document.getElementById('alumnoSelect');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const camaraBtn = document.getElementById('camaraBtn');
const galeriaBtn = document.getElementById('galeriaBtn');
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

async function cargarAlumnos() {
    try {
        const response = await fetch(`${DB_API_URL}/alumnos`);
        const data = await response.json();
        if (alumnoSelect && data.alumnos) {
            alumnoSelect.innerHTML = '<option value="">-- Seleccione un alumno --</option>';
            data.alumnos.forEach(a => {
                const option = document.createElement('option');
                option.value = a.id_alumno;
                option.textContent = a.nombre;
                alumnoSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error:', error);
        alumnoSelect.innerHTML = '<option value="">Error cargando alumnos</option>';
    }
}

async function abrirCamara() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        video.srcObject = stream;
        cameraContainer.style.display = 'block';
        uploadContainer.style.display = 'none';
    } catch (error) {
        alert('No se pudo acceder a la cámara');
    }
}

function cerrarCamara() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    cameraContainer.style.display = 'none';
    uploadContainer.style.display = 'block';
}

function capturarFoto() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob(blob => {
        imagenActual = new File([blob], 'examen.jpg', { type: 'image/jpeg' });
        preview.src = URL.createObjectURL(blob);
        previewContainer.style.display = 'block';
        cerrarCamara();
        uploadContainer.style.display = 'none';
    }, 'image/jpeg');
}

uploadArea.onclick = () => fileInput.click();
fileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        imagenActual = file;
        preview.src = URL.createObjectURL(file);
        previewContainer.style.display = 'block';
        uploadContainer.style.display = 'none';
    }
};

camaraBtn.onclick = () => { abrirCamara(); };
galeriaBtn.onclick = () => {
    uploadContainer.style.display = 'block';
    cameraContainer.style.display = 'none';
};
cancelarCamaraBtn.onclick = cerrarCamara;
capturarBtn.onclick = capturarFoto;
cancelarBtn.onclick = () => {
    imagenActual = null;
    previewContainer.style.display = 'none';
    uploadContainer.style.display = 'block';
    resultados.style.display = 'none';
};

corregirBtn.onclick = async () => {
    if (!imagenActual) {
        alert('Selecciona una imagen primero');
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
            document.getElementById('notaValor').textContent = data.nota_final;
            document.getElementById('correctas').textContent = data.correctas;
            document.getElementById('incorrectas').textContent = data.incorrectas;
            
            const detalleHtml = data.respuestas_alumno.map((p, i) => `
                <div>Pregunta ${i+1}: ${p} / 5.0 ${p >= 4.0 ? '✅' : (p >= 3.1 ? '⚠️' : '❌')}</div>
            `).join('');
            document.getElementById('detalleLista').innerHTML = detalleHtml;
            
            resultados.style.display = 'block';
        } else {
            alert('Error: ' + JSON.stringify(data));
        }
    } catch (error) {
        alert('Error al conectar con el servidor');
    } finally {
        loading.style.display = 'none';
    }
};

guardarBtn.onclick = async () => {
    const alumnoId = alumnoSelect.value;
    if (!alumnoId) {
        alert('Selecciona un alumno');
        return;
    }
    if (!respuestasCorreccion) {
        alert('Primero corrige un examen');
        return;
    }
    
    const evaluacion = {
        id_alumno: parseInt(alumnoId),
        puntaje: respuestasCorreccion.nota_final,
        fecha: new Date().toISOString().split('T')[0],
        respuestas: respuestasCorreccion.respuestas_alumno.map((p, i) => ({
            id_pregunta: i + 1,
            es_correcta: p >= 4.0
        }))
    };
    
    try {
        const response = await fetch(`${DB_API_URL}/nueva_evaluacion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(evaluacion)
        });
        if (response.ok) {
            alert('✅ Guardado');
            nuevoBtn.click();
        } else {
            alert('Error al guardar');
        }
    } catch (error) {
        alert('Error de conexión');
    }
};

nuevoBtn.onclick = () => {
    imagenActual = null;
    previewContainer.style.display = 'none';
    resultados.style.display = 'none';
    uploadContainer.style.display = 'block';
};

cargarAlumnos();
