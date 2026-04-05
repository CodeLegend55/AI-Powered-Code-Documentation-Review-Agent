import express from 'express';
import multer from 'multer';
import { generateCodeReview } from '../services/ollama.js';
import { queryRAGContext } from '../services/rag.js';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post('/analyze', upload.single('codeFile'), async (req, res) => {
    try {
        let codeContent = '';
        
        // Handle file upload or raw text
        if (req.file) {
            codeContent = req.file.buffer.toString('utf-8');
        } else if (req.body.code) {
            codeContent = req.body.code;
        } else {
            return res.status(400).json({ error: 'No code provided for review.' });
        }

        // 1. Retrieve RAG Context (e.g. project rules, past patches)
        const relevantContext = await queryRAGContext(codeContent);

        // 2. Generate LLM Review
        const reviewOutput = await generateCodeReview(codeContent, relevantContext);
        
        res.json({
            success: true,
            review: reviewOutput,
            rag_context_used: relevantContext.length > 0
        });

    } catch (error) {
        console.error("Review Error:", error);
        res.status(500).json({ error: 'Failed to generate code review.', details: error.message });
    }
});

export default router;
