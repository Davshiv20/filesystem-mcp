import { useState } from 'react';
import { backendApi } from '../api/backendApi';
import type { PromptRequest, PromptResponse } from '../api/backendApi';
import './PromptModal.css';

interface PromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceId: string;
  onSuccess?: (response: PromptResponse) => void;
}

export default function PromptModal({ 
  isOpen, 
  onClose, 
  workspaceId, 
  onSuccess 
}: PromptModalProps) {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<PromptResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const request: PromptRequest = {
        workspace_id: workspaceId,
        prompt: prompt.trim()
      };

      const result = await backendApi.processPrompt(request);
      setResponse(result);
      onSuccess?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setPrompt('');
    setResponse(null);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>AI File Operations</h2>
          <button className="close-button" onClick={handleClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="prompt-form">
          <div className="form-group">
            <label htmlFor="prompt">Describe what you want to do:</label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Create a Python file called hello.py with a function that prints hello world"
              rows={4}
              disabled={isLoading}
              required
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              onClick={handleClose}
              disabled={isLoading}
              className="cancel-button"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={isLoading || !prompt.trim()}
              className="submit-button"
            >
              {isLoading ? 'Processing...' : 'Execute'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <h3>Result</h3>
            <div className="response-details">
              <div className="status">
                Status: <span className={response.success ? 'success' : 'error'}>
                  {response.success ? 'Success' : 'Failed'}
                </span>
              </div>
              <div className="confidence">
                Confidence: <span>{Math.round(response.confidence * 100)}%</span>
              </div>
              <div className="method">
                Method: <span>{response.method}</span>
              </div>
            </div>

            {response.operations.length > 0 && (
              <div className="operations">
                <h4>Operations Performed:</h4>
                <ul>
                  {response.operations.map((op, index) => (
                    <li key={index} className="operation-item">
                      ✅ {op}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.errors.length > 0 && (
              <div className="errors">
                <h4>Errors:</h4>
                <ul>
                  {response.errors.map((err, index) => (
                    <li key={index} className="error-item">
                      ❌ {err}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.reasoning && (
              <div className="reasoning">
                <h4>AI Reasoning:</h4>
                <p>{response.reasoning}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 