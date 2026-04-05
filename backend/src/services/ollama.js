import { Ollama } from 'ollama';

const ollama = new Ollama({ host: process.env.OLLAMA_HOST || 'http://127.0.0.1:11434' });
const MODEL_NAME = process.env.OLLAMA_MODEL || 'custom-code-reviewer';

/**
 * Generate a code review using the fine-tuned model
 */
export async function generateCodeReview(code, contextDocs = []) {
    let contextPrompt = '';
    if (contextDocs.length > 0) {
        contextPrompt = '\n\nRelated documentation/context (RAG):\n' + contextDocs.join('\n');
    }

    const systemPrompt = "You are an expert AI code reviewer. Locate vulnerabilities, suggest best practices, and output structured code documentation.";

    const userPrompt = `Review this code for vulnerabilities and quality issues. If vulnerable, identify the issue and suggest a fix. Also output basic documentation for this code.${contextPrompt}\n\n### Input Context:\n${code}`;

    const response = await ollama.chat({
        model: MODEL_NAME,
        messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ],
        stream: false
    });

    return response.message.content;
}
