const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'N4n4p4ss!',
    database: 'seat_booking'
});

module.exports = pool;
