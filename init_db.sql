-- Crear base de datos
CREATE DATABASE IF NOT EXISTS evaluacion_ia;
USE evaluacion_ia;

-- Tabla alumnos
CREATE TABLE IF NOT EXISTS alumnos (
    id_alumno INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE
);

-- Tabla evaluacion
CREATE TABLE IF NOT EXISTS evaluacion (
    id_evaluacion INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno INT,
    puntaje DECIMAL(5,2),
    fecha DATE,
    FOREIGN KEY (id_alumno) REFERENCES alumnos(id_alumno)
);

-- Tabla pregunta
CREATE TABLE IF NOT EXISTS pregunta (
    id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
    descripcion TEXT,
    respuesta_correcta VARCHAR(50)
);

-- Tabla respuesta
CREATE TABLE IF NOT EXISTS respuesta (
    id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
    id_evaluacion INT,
    id_pregunta INT,
    es_correcta BOOLEAN,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluacion(id_evaluacion),
    FOREIGN KEY (id_pregunta) REFERENCES pregunta(id_pregunta)
);

-- Insertar datos de ejemplo
INSERT INTO alumnos (nombre, correo) VALUES
('Carlos Ramirez', 'carlos@gmail.com'),
('Laura Torres', 'laura@gmail.com'),
('Andres Lopez', 'andres@gmail.com'),
('Sofia Martinez', 'sofia@gmail.com'),
('Daniela Rojas', 'daniela@gmail.com'),
('Luis Fernandez', 'luis@gmail.com'),
('Camila Vargas', 'camila@gmail.com'),
('Miguel Castro', 'miguel@gmail.com'),
('Valentina Ruiz', 'valentina@gmail.com'),
('Sebastian Herrera', 'sebastian@gmail.com');

INSERT INTO evaluacion (id_alumno, puntaje, fecha) VALUES
(1, 4.5, '2026-04-12'),
(2, 3.8, '2026-04-12'),
(3, 5.0, '2026-04-13'),
(4, 2.5, '2026-04-13'),
(5, 4.2, '2026-04-14'),
(6, 3.0, '2026-04-14'),
(7, 4.8, '2026-04-14'),
(8, 3.7, '2026-04-14'),
(9, 2.9, '2026-04-14'),
(10, 4.1, '2026-04-14');

INSERT INTO pregunta (descripcion, respuesta_correcta) VALUES
('2 + 2 = ?', '4'),
('5 x 3 = ?', '15'),
('10 - 6 = ?', '4'),
('Capital de Colombia', 'Bogota'),
('Color del cielo en un dia despejado', 'Azul'),
('3 + 7 = ?', '10'),
('9 x 2 = ?', '18'),
('15 / 3 = ?', '5'),
('Raiz cuadrada de 16', '4'),
('Cuantos dias tiene una semana', '7');

INSERT INTO respuesta (id_evaluacion, id_pregunta, es_correcta) VALUES
(1,1,TRUE),(1,2,TRUE),(1,3,FALSE),(1,4,TRUE),(1,5,TRUE),
(1,6,TRUE),(1,7,FALSE),(1,8,TRUE),(1,9,TRUE),(1,10,TRUE),
(2,1,TRUE),(2,2,FALSE),(2,3,TRUE),(2,4,TRUE),(2,5,FALSE),
(2,6,TRUE),(2,7,TRUE),(2,8,FALSE),(2,9,TRUE),(2,10,TRUE),
(3,1,TRUE),(3,2,TRUE),(3,3,TRUE),(3,4,TRUE),(3,5,TRUE),
(3,6,TRUE),(3,7,TRUE),(3,8,TRUE),(3,9,TRUE),(3,10,TRUE);

-- Verificar datos
SELECT 'Alumnos:' as Tabla, COUNT(*) as Total FROM alumnos
UNION SELECT 'Evaluaciones:', COUNT(*) FROM evaluacion
UNION SELECT 'Preguntas:', COUNT(*) FROM pregunta
UNION SELECT 'Respuestas:', COUNT(*) FROM respuesta;
