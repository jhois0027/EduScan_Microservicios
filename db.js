const mysql = require('mysql2');

const conexion = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'root', // ← pon tu contraseña real
  database: 'evaluacion_ia'
});

conexion.connect((err) => {
  if (err) {
    console.log('❌ Error de conexión:', err);
  } else {
    console.log('✅ Conectado a MySQL');
  }
});

module.exports = conexion;