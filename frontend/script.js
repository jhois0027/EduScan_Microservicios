const API_URL = 'http://localhost:8000';

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

let imagenActual = null;

uploadArea.onclick = () => fileInput.click();
camaraBtn.onclick = () => { fileInput.setAttribute('capture', 'environment'); fileInput.click(); };
galeriaBtn.onclick = () => { fileInput.removeAttribute('capture'); fileInput.click(); };

fileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        imagenActual = file;
        const reader = new FileReader();
        reader.onload = (event) => {
            preview.src = event.target.result;
            previewContainer.style.display = 'block';
            uploadArea.style.display = 'none';
            document.querySelector('.camera-options').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
};

corregirBtn.onclick = async () => {
    if (!imagenActual) return;
    
    loading.style.display = 'block';
    previewContainer.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', imagenActual);
    
    try {
        const response = await fetch(`${API_URL}/corregir`, { method: 'POST', body: formData });
        const data = await response.json();
        
        if (response.ok) {
            // Mostrar nota final (numérica de 0.0 a 5.0)
            document.getElementById('notaValor').textContent = data.nota_final.toFixed(1);
            document.getElementById('correctas').textContent = data.correctas;
            document.getElementById('incorrectas').textContent = data.incorrectas;
            
            // Mostrar detalles de preguntas
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
            
            const detalleLista = document.getElementById('detalleLista');
            if (detalleLista) {
                detalleLista.innerHTML = detalleHtml;
            }
            
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

nuevoBtn.onclick = () => {
    imagenActual = null;
    fileInput.value = '';
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'block';
    document.querySelector('.camera-options').style.display = 'flex';
    resultados.style.display = 'none';
};
