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

        // 2. Setup SSE Headers
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        // 3. Send initial metadata
        res.write(`data: ${JSON.stringify({ type: 'metadata', rag_context_used: relevantContext.length > 0 })}\n\n`);

        // 4. Generate LLM Review and stream chunks
        const responseStream = await generateCodeReview(codeContent, relevantContext);
        
        try {
            for await (const chunk of responseStream) {
                if (chunk && chunk.message && chunk.message.content) {
                    res.write(`data: ${JSON.stringify({ type: 'chunk', text: chunk.message.content })}\n\n`);
                }
            }
        } catch (streamError) {
            // Ollama often cuts the connection gracefully or crashes if CPU takes too long.
            // We catch "Did not receive done" so the user still sees the partial review!
            console.warn("Stream ended early:", streamError.message);
        }

        // 5. End Stream
        res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);
        res.end();

    } catch (error) {
        console.error("Review Error:", error);
        if (!res.headersSent) {
            res.status(500).json({ error: 'Failed to generate code review.', details: error.message });
        } else {
            res.write(`data: ${JSON.stringify({ type: 'error', error: 'Failed to generate code review.', details: error.message })}\n\n`);
            res.end();
        }
    }
});

export default router;
