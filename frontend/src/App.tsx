import { useState, useEffect } from 'react'
import { backendApi, type WorkspaceInfo, type PromptResponse } from './api/backendApi'
import PromptModal from './components/PromptModal'
import './App.css'

function App() {
  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[]>([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<PromptResponse | null>(null);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setIsLoading(true);
      const workspacesData = await backendApi.listWorkspaces();
      
      // Ensure workspacesData is an array
      const workspacesArray = Array.isArray(workspacesData) ? workspacesData : [];
      setWorkspaces(workspacesArray);
      
      // Auto-select first workspace if available
      if (workspacesArray.length > 0 && !selectedWorkspace) {
        setSelectedWorkspace(workspacesArray[0].id);
      }
    } catch (err) {
      console.error('Error loading workspaces:', err);
      setError(err instanceof Error ? err.message : 'Failed to load workspaces');
      setWorkspaces([]); // Ensure workspaces is always an array
    } finally {
      setIsLoading(false);
    }
  };

  const createWorkspace = async () => {
    const name = prompt('Enter workspace name:');
    if (!name?.trim()) return;

    try {
      const result = await backendApi.createWorkspace(name.trim());
      await loadWorkspaces();
      setSelectedWorkspace(result.workspace_id);
    } catch (err) {
      console.error('Error creating workspace:', err);
      setError(err instanceof Error ? err.message : 'Failed to create workspace');
    }
  };

  const handlePromptSuccess = (response: PromptResponse) => {
    setLastResponse(response);
    // Refresh workspaces to show new files
    setTimeout(() => loadWorkspaces(), 1000);
  };

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Filesystem MCP made by Shivam Dave</h1>
        <p>AI-powered file operations</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <div className="workspace-section">
          <div className="workspace-header">
            <h2>Workspaces</h2>
            <button onClick={createWorkspace} className="create-workspace-btn">
              + New Workspace
            </button>
          </div>

          {!Array.isArray(workspaces) || workspaces.length === 0 ? (
            <div className="empty-state">
              <p>No workspaces found. Create one to get started!</p>
              <button onClick={createWorkspace} className="primary-button">
                Create Workspace
              </button>
            </div>
          ) : (
            <div className="workspace-list">
              {workspaces.map((workspace) => (
                <div
                  key={workspace.id}
                  className={`workspace-item ${selectedWorkspace === workspace.id ? 'selected' : ''}`}
                  onClick={() => setSelectedWorkspace(workspace.id)}
                >
                  <div className="workspace-info">
                    <h3>{workspace.name}</h3>
                    <p>{workspace.file_count} files • {Math.round(workspace.size / 1024)} KB</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedWorkspace && (
          <div className="action-section">
            <h2>Ask File Operations</h2>
            <p>Use natural language to create, edit, delete, or manage files.</p>
            
            <button 
              onClick={() => setIsModalOpen(true)}
              className="prompt-button"
            >
              Prompt the model
            </button>

            {lastResponse && (
              <div className="last-response">
                <h3>Last Operation</h3>
                <div className={`response-status ${lastResponse.success ? 'success' : 'error'}`}>
                  {lastResponse.success ? '✅ Success' : '❌ Failed'}
                </div>
                {lastResponse.operations && lastResponse.operations.length > 0 && (
                  <div className="response-ops">
                    {lastResponse.operations.map((op, index) => (
                      <div key={index} className="operation">• {op}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      <PromptModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        workspaceId={selectedWorkspace}
        onSuccess={handlePromptSuccess}
      />
    </div>
  )
}

export default App
