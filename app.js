const conexion = require('./db');

// Consulta a la base de datos
conexion.query('SELECT * FROM alumnos', (err, results) => {
  if (err) {
    console.log('❌ Error:', err);
  } else {
    console.log('📊 Datos de alumnos:');
    console.table(results);
  }
});