import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import reviewRoutes from './src/routes/review.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/review', reviewRoutes);

app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'AI Code Reviewer API is running' });
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
