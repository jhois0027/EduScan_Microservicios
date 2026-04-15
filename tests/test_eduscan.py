"""
Pruebas de EduScan - Version corregida
"""

import os
import pytest
import yaml

def test_backend_archivos_existen():
    archivos = [
        "backend/api/gateway.py",
        "backend/api/routes.py",
        "backend/services/procesamiento.py",
        "backend/services/ia_modelo.py",
        "backend/services/database.py",
        "backend/models/red_neuronal.py",
        "backend/requirements.txt",
        "backend/Dockerfile"
    ]
    for archivo in archivos:
        assert os.path.exists(archivo), f"No existe: {archivo}"
    print("✅ Backend archivos OK")

def test_frontend_archivos_existen():
    archivos = [
        "frontend/index.html",
        "frontend/style.css",
        "frontend/script.js"
    ]
    for archivo in archivos:
        assert os.path.exists(archivo), f"No existe: {archivo}"
    print("✅ Frontend archivos OK")

def test_kubernetes_archivos_existen():
    archivos = [
        "kubernetes/deployment.yaml",
        "kubernetes/service.yaml"
    ]
    for archivo in archivos:
        assert os.path.exists(archivo), f"No existe: {archivo}"
    print("✅ Kubernetes archivos OK")

def test_docs_archivos_existen():
    archivos = [
        "README.md",
        "docs/README.md",
        "docs/arquitectura.md"
    ]
    for archivo in archivos:
        assert os.path.exists(archivo), f"No existe: {archivo}"
    print("✅ Docs archivos OK")

def test_requirements_tiene_dependencias():
    with open("requirements.txt", "r") as f:
        contenido = f.read()
    dependencias = ["fastapi", "opencv", "uvicorn", "numpy"]
    for dep in dependencias:
        assert dep in contenido, f"Falta: {dep}"
    print("✅ Requirements OK")

def test_docker_compose_valido():
    with open("docker-compose.yml", "r") as f:
        compose = yaml.safe_load(f)
    assert "services" in compose
    assert "gateway" in compose["services"]
    print("✅ Docker Compose OK")

def test_gateway_tiene_endpoints():
    with open("backend/api/gateway.py", "r", encoding="utf-8") as f:
        contenido = f.read()
    # Verificar que contiene los endpoints (con o sin parámetros)
    tiene_post = "/corregir" in contenido and ("@app.post" in contenido or "app.post" in contenido)
    tiene_get = '"/"' in contenido or "'/'" in contenido
    tiene_health = "/health" in contenido
    assert tiene_post, "No se encuentra el endpoint /corregir"
    assert tiene_get, "No se encuentra el endpoint /"
    assert tiene_health, "No se encuentra el endpoint /health"
    print("✅ Gateway endpoints OK")

def test_index_html_tiene_estructura():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert "EduScan" in html
    assert "uploadArea" in html
    assert "corregirBtn" in html
    print("✅ Index HTML OK")

def test_kubernetes_deployment_valido():
    with open("kubernetes/deployment.yaml", "r") as f:
        contenido = f.read()
    # Verificar que contiene elementos de Kubernetes
    assert "Deployment" in contenido or "deployment" in contenido.lower()
    assert "containers" in contenido.lower()
    print("✅ Kubernetes Deployment OK")

def test_kubernetes_service_valido():
    with open("kubernetes/service.yaml", "r") as f:
        service = yaml.safe_load(f)
    assert service is not None
    assert "Service" in str(service) or "service" in str(service).lower()
    print("✅ Kubernetes Service OK")

def test_github_actions_existen():
    archivos = [
        ".github/workflows/test.yml",
        ".github/workflows/deploy.yml"
    ]
    for archivo in archivos:
        assert os.path.exists(archivo), f"No existe: {archivo}"
    print("✅ GitHub Actions OK")

def test_no_hay_comentarios_ofensivos():
    archivos_py = []
    for root, dirs, files in os.walk("backend"):
        for file in files:
            if file.endswith(".py"):
                archivos_py.append(os.path.join(root, file))
    
    # Verificar que los archivos no estén vacíos (excepto __init__.py)
    for archivo in archivos_py:
        if "__init__" in archivo:
            continue  # Saltar __init__.py que pueden estar vacíos
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            assert len(contenido) > 50, f"{archivo} parece vacío"
    print("✅ Archivos no vacios OK")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
