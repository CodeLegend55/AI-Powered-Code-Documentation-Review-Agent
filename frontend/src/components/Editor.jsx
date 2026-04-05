import React from 'react';
import Editor from '@monaco-editor/react';

function EditorComponent({ code, onChange }) {
  const handleEditorChange = (value) => {
    onChange(value);
  };

  return (
    <div style={{ flex: 1, position: 'relative' }}>
      <Editor
        height="100%"
        defaultLanguage="javascript"
        theme="vs-dark"
        value={code}
        onChange={handleEditorChange}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "'JetBrains Mono', monospace",
          padding: { top: 16 },
          scrollBeyondLastLine: false,
          smoothScrolling: true,
          cursorBlinking: "smooth"
        }}
        loading={
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#94a3b8' }}>
            Loading Editor...
          </div>
        }
      />
    </div>
  );
}

export default EditorComponent;
