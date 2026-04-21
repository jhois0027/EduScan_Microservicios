const { Pool } = require('pg');

// Render inyecta DATABASE_URL automáticamente
// NO pongas la contraseña aquí directamente
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' 
    ? { rejectUnauthorized: false } 
    : false
});

module.exports = pool;