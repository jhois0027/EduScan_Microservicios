const API_URL = 'https://eduscan-database.onrender.com';

let topAlumnosChart = null;
let evolucionChart = null;
let distribucionChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    setupNavigation();
    loadAlumnos();
    loadCalificaciones();
    loadEvaluaciones();
    loadAlumnosCount();
});

function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) {
                showPage(page);
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                document.getElementById('pageTitle').textContent = item.textContent.trim().split(' ')[0];
            }
        });
    });
}

function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(`${pageName}Page`).classList.add('active');
    if (pageName === 'dashboard') loadDashboard();
    if (pageName === 'alumnos') loadAlumnos();
    if (pageName === 'calificaciones') loadCalificaciones();
    if (pageName === 'evaluaciones') loadEvaluaciones();
}

async function loadDashboard() {
    try {
        const resumen = await fetch(API_URL + '/dashboard/resumen').then(r => r.json());
        
        document.getElementById('totalAlumnos').textContent = resumen.estadisticas.total_alumnos;
        document.getElementById('totalEvaluaciones').textContent = resumen.estadisticas.total_evaluaciones;
        document.getElementById('promedioGeneral').textContent = resumen.estadisticas.promedio_general;
        document.getElementById('mejorNota').textContent = resumen.estadisticas.mejor_nota;
        document.getElementById('mejorEstudiante').textContent = resumen.top_alumnos[0]?.nombre || '-';
        
        const aprobados = resumen.top_alumnos.filter(a => a.promedio >= 3).length;
        const tasa = (aprobados / resumen.top_alumnos.length * 100).toFixed(0);
        document.getElementById('tasaAprobacion').textContent = tasa + '%';
        
        createTopAlumnosChart(resumen.top_alumnos);
        
        const evolucion = await fetch(API_URL + '/dashboard/evolucion').then(r => r.json());
        createEvolucionChart(evolucion.evolucion);
        
        const distribucion = await fetch(API_URL + '/dashboard/distribucion').then(r => r.json());
        createDistribucionChart(distribucion.distribucion);
        
        const evaluaciones = await fetch(API_URL + '/evaluaciones').then(r => r.json());
        loadRecentEvaluations(evaluaciones.evaluaciones);
        
    } catch(e) { console.error('Error:', e); }
}

function createTopAlumnosChart(data) {
    const options = {
        series: [{ name: 'Promedio', data: data.map(a => a.promedio) }],
        chart: { type: 'bar', height: 350, toolbar: { show: true } },
        colors: ['#667eea'],
        xaxis: { categories: data.map(a => a.nombre.split(' ')[0]) },
        yaxis: { max: 5, title: { text: 'Promedio' } },
        dataLabels: { enabled: true, offsetY: -20 }
    };
    if (topAlumnosChart) topAlumnosChart.destroy();
    topAlumnosChart = new ApexCharts(document.querySelector("#topAlumnosChart"), options);
    topAlumnosChart.render();
}

function createEvolucionChart(evolucion) {
    const options = {
        series: [{ name: 'Promedio', data: evolucion.map(e => e.promedio) }],
        chart: { type: 'line', height: 350, toolbar: { show: true } },
        colors: ['#764ba2'],
        stroke: { curve: 'smooth', width: 3 },
        xaxis: { categories: evolucion.map(e => e.fecha) },
        yaxis: { max: 5 }
    };
    if (evolucionChart) evolucionChart.destroy();
    evolucionChart = new ApexCharts(document.querySelector("#evolucionChart"), options);
    evolucionChart.render();
}

function createDistribucionChart(distribucion) {
    const data = [distribucion.excelente||0, distribucion.bueno||0, distribucion.aprobado||0, distribucion.insuficiente||0, distribucion.deficiente||0];
    const options = {
        series: data,
        chart: { type: 'donut', height: 350 },
        labels: ['Excelente', 'Bueno', 'Aprobado', 'Insuficiente', 'Deficiente'],
        colors: ['#38a169', '#48bb78', '#ecc94b', '#ed8936', '#f56565']
    };
    if (distribucionChart) distribucionChart.destroy();
    distribucionChart = new ApexCharts(document.querySelector("#distribucionChart"), options);
    distribucionChart.render();
}

function loadRecentEvaluations(evaluaciones) {
    const tbody = document.getElementById('recentBody');
    tbody.innerHTML = evaluaciones.slice(0,5).map(e => `
        <tr><td><strong>${e.alumno}</strong></td><td>${e.puntaje}</td><td>${e.fecha}</td><td>-</td>
        <td><span class="${e.puntaje>=3?'badge-aprobado':'badge-reprobado'}">${e.puntaje>=3?'Aprobado':'Reprobado'}</span></td>
        <td><button onclick="verDetalle(${e.id_evaluacion})">Ver</button></td></tr>
    `).join('');
}

async function loadAlumnos() {
    const data = await fetch(API_URL + '/alumnos').then(r => r.json());
    document.getElementById('alumnosBody').innerHTML = data.alumnos.map(a => `
        <tr><td>${a.id_alumno}</td><td>${a.nombre}</td><td>${a.correo}</td><td>-</td><td>-</td><td>↑</td>
        <td><button onclick="verAlumno(${a.id_alumno})">Ver</button></td></tr>
    `).join('');
    document.getElementById('alumnosCount').textContent = data.alumnos.length;
}

async function loadCalificaciones() {
    const data = await fetch(API_URL + '/evaluaciones').then(r => r.json());
    document.getElementById('calificacionesBody').innerHTML = data.evaluaciones.map(e => `
        <tr><td>${e.alumno}</td><td>Evaluación ${e.id_evaluacion}</td><td>${e.puntaje}</td><td>${e.fecha}</td><td>-</td>
        <td><button onclick="verDetalle(${e.id_evaluacion})">Ver</button></td></tr>
    `).join('');
    const alumnos = await fetch(API_URL + '/alumnos').then(r => r.json());
    document.getElementById('filtroAlumno').innerHTML = '<option value="">Todos</option>' + alumnos.alumnos.map(a => `<option>${a.nombre}</option>`).join('');
}

async function loadEvaluaciones() {
    const data = await fetch(API_URL + '/evaluaciones').then(r => r.json());
    document.getElementById('evaluacionesBody').innerHTML = data.evaluaciones.map(e => `
        <tr><td>${e.id_evaluacion}</td><td>${e.alumno}</td><td>${e.puntaje}</td><td>${e.fecha}</td><td>-</td>
        <td><button onclick="verRespuestas(${e.id_evaluacion})">Ver</button></td></tr>
    `).join('');
}

async function loadAlumnosCount() {
    const data = await fetch(API_URL + '/alumnos').then(r => r.json());
    document.getElementById('alumnosCount').textContent = data.alumnos.length;
}

async function verAlumno(id) {
    const data = await fetch(API_URL + `/alumno/${id}/detalle`).then(r => r.json());
    document.getElementById('modalBody').innerHTML = `
        <h3>${data.alumno.nombre}</h3>
        <p>Email: ${data.alumno.correo}</p>
        <p>Promedio: ${data.promedio}</p>
        <p>Total Exámenes: ${data.total_evaluaciones}</p>
        <button onclick="cerrarModal()">Cerrar</button>
    `;
    document.getElementById('modal').style.display = 'block';
}

function verDetalle(id) { alert('Detalle de evaluación ' + id); }
function verRespuestas(id) { alert('Respuestas de evaluación ' + id); }
function refreshData() { loadDashboard(); loadAlumnos(); loadCalificaciones(); loadEvaluaciones(); }
function exportarReporte() { alert('Exportando...'); }
function agregarAlumno() { alert('Agregar alumno'); }
function verTodasEvaluaciones() { showPage('evaluaciones'); }
function filterAlumnos() {
    const search = document.getElementById('searchAlumno').value.toLowerCase();
    document.querySelectorAll('#alumnosBody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(search) ? '' : 'none';
    });
}
function cerrarModal() { document.getElementById('modal').style.display = 'none'; }
document.querySelector('.close')?.addEventListener('click', cerrarModal);
window.onclick = (e) => { if (e.target === document.getElementById('modal')) cerrarModal(); };
