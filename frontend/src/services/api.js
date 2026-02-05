import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Code Review API
export const reviewCode = async (code, language, docStyle, options = {}) => {
  const response = await api.post('/api/review', {
    code,
    language,
    doc_style: docStyle,
    check_security: options.checkSecurity ?? true,
    generate_docs: options.generateDocs ?? true,
    context: options.context || '',
  });
  return response.data;
};

export const quickReview = async (code, language) => {
  const response = await api.post('/api/review/quick', {
    code,
    language,
  });
  return response.data;
};

export const analyzeDefects = async (code, language) => {
  const response = await api.post('/api/analyze/defects', {
    code,
    language,
  });
  return response.data;
};

export const analyzeMetrics = async (code, language) => {
  const response = await api.post('/api/analyze/metrics', {
    code,
    language,
  });
  return response.data;
};

// Documentation API
export const generateDocumentation = async (code, language, docStyle, includeExamples = true) => {
  const response = await api.post('/api/document', {
    code,
    language,
    doc_style: docStyle,
    include_examples: includeExamples,
  });
  return response.data;
};

export const getDocStyles = async () => {
  const response = await api.get('/api/document/styles');
  return response.data;
};

// GitHub API
export const reviewPullRequest = async (repoUrl, prNumber) => {
  const response = await api.post('/api/github/review-pr', {
    repo_url: repoUrl,
    pr_number: prNumber,
  });
  return response.data;
};

export const reviewCommit = async (repoUrl, commitSha) => {
  const response = await api.post('/api/github/review-commit', {
    repo_url: repoUrl,
    commit_sha: commitSha,
  });
  return response.data;
};

// Knowledge Base API
export const searchKnowledge = async (query, language = null) => {
  const response = await api.post('/api/knowledge/search', null, {
    params: { query, language },
  });
  return response.data;
};

export const getKnowledgeStats = async () => {
  const response = await api.get('/api/knowledge/stats');
  return response.data;
};

export const uploadKnowledge = async (content, title, docType, language = null) => {
  const response = await api.post('/api/knowledge/upload', {
    content,
    title,
    doc_type: docType,
    language,
  });
  return response.data;
};

// Health & Config API
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

export default api;
