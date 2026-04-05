import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FiAlertTriangle } from 'react-icons/fi';

function ReviewTab({ data }) {
  if (data.error) {
    return (
      <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--error-color)', padding: '16px', borderRadius: '8px', color: '#fca5a5' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--error-color)' }}>
          <FiAlertTriangle /> Analysis Error
        </h3>
        <p>{data.error}</p>
        {data.details && <pre style={{ marginTop: '8px', fontSize: '0.8rem', background: '#450a0a', padding: '8px', borderRadius: '4px', overflowX: 'auto', border: '1px solid rgba(239, 68, 68, 0.3)' }}>{data.details}</pre>}
      </div>
    );
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease' }}>
      {data.rag_context_used && (
        <div style={{ marginBottom: '1.5rem', display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', padding: '4px 12px', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)', borderRadius: '12px', border: '1px solid rgba(16,185,129,0.2)' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--success-color)' }}></span>
          Enhanced with Contextual RAG
        </div>
      )}
      
      <div className="md-content">
        <ReactMarkdown>{data.review}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ReviewTab;
