const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const db = require('./db');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

app.get('/test', async (req, res) => {
    try {
        const [rows] = await db.query('SELECT 1 + 1 AS result');
        res.json(rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/seats', async (req, res) => {
    try {
        const [rows] = await db.query(`
            SELECT 
                seats.id,
                seats.label,
                seats.position_x,
                seats.position_y,
                seats.status,
                bookings.status AS booking_status,
                campaigns.color_hex
            FROM seats
            LEFT JOIN bookings 
                ON seats.id = bookings.seat_id 
                AND bookings.status = 'pending'
            LEFT JOIN campaigns 
                ON bookings.campaign_id = campaigns.id
        `);

        res.json(rows);

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(3000, () => {
    console.log("Server running on http://localhost:3000");
});

app.get('/campaigns', async (req, res) => {
    try {
        const [rows] = await db.query('SELECT * FROM campaigns');
        res.json(rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/book', async (req, res) => {
    const { user_id, campaign_id, seat_ids } = req.body;

    try {
        for (let seatId of seat_ids) {
            await db.query(
                'INSERT INTO bookings (user_id, seat_id, campaign_id, status) VALUES (?, ?, ?, "pending")',
                [user_id, seatId, campaign_id]
            );

            await db.query(
                'UPDATE seats SET status = "pending" WHERE id = ?',
                [seatId]
            );
        }

        res.json({ message: "Booking submitted successfully" });

    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

