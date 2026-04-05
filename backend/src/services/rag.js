import { ChromaClient } from 'chromadb';
import { Ollama } from 'ollama';

// Embeddings model - nomic-embed-text is highly recommended locally
const ollama = new Ollama({ host: process.env.OLLAMA_HOST || 'http://127.0.0.1:11434' });
const EMBED_MODEL = process.env.EMBED_MODEL || 'nomic-embed-text'; 

const chromaClient = new ChromaClient({
    path: process.env.CHROMA_URL || "http://localhost:8000"
});

export async function getOrCreateCollection() {
    return await chromaClient.getOrCreateCollection({
        name: "code-context-collection",
    });
}

/**
 * Generate embeddings using local Ollama model
 */
export async function generateEmbedding(text) {
    const response = await ollama.embeddings({
        model: EMBED_MODEL,
        prompt: text
    });
    return response.embedding;
}

/**
 * Add a document (e.g., project guidelines, prior verified secure code) to RAG
 */
export async function addDocumentToRAG(docId, text, metadata = {}) {
    const collection = await getOrCreateCollection();
    const embedding = await generateEmbedding(text);
    
    await collection.upsert({
        ids: [docId],
        embeddings: [embedding],
        metadatas: [metadata],
        documents: [text]
    });
}

/**
 * Query the RAG database for context relevant to the incoming code
 */
export async function queryRAGContext(queryText, nResults = 2) {
    try {
        const collection = await getOrCreateCollection();
        const queryEmbedding = await generateEmbedding(queryText);
        
        const results = await collection.query({
            queryEmbeddings: [queryEmbedding],
            nResults: nResults
        });
        
        return results.documents[0] || [];
    } catch (error) {
        console.error("RAG Query Failed:", error.message);
        return []; // Fail gracefully returning no extra context
    }
}
