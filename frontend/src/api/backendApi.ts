const API_BASE_URL = 'http://localhost:8000';

export interface PromptRequest {
  workspace_id: string;
  prompt: string;
}

export interface PromptResponse {
  success: boolean;
  operations: string[];
  errors: string[];
  confidence: number;
  reasoning: string;
  method: string;
  file_path: string;
  success_message: string;
}

export interface WorkspaceInfo {
  id: string;
  name: string;
  created_at: string;
  file_count: number;
  size: number;
}

class BackendApi {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    return response.json();
  }


  async checkHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  async createWorkspace(name: string): Promise<{ workspace_id: string }> {
    return this.request<{ workspace_id: string }>('/workspace/create', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }


  async getWorkspace(workspaceId: string): Promise<WorkspaceInfo> {
    return this.request<WorkspaceInfo>(`/workspace/${workspaceId}`);
  }

  // List workspaces
  async listWorkspaces(): Promise<WorkspaceInfo[]> {
    return this.request<WorkspaceInfo[]>('/workspace/');
  }

  // Process prompt
  async processPrompt(request: PromptRequest): Promise<PromptResponse> {
    return this.request<PromptResponse>('/prompt/process', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Check prompt service health
  async checkPromptHealth(): Promise<{
    status: string;
    llm_available: boolean;
    method: string;
  }> {
    return this.request<{
      status: string;
      llm_available: boolean;
      method: string;
    }>('/prompt/health');
  }

  // List files in workspace
  async listFiles(workspaceId: string): Promise<{
    files: Array<{
      name: string;
      path: string;
      size: number;
      is_directory: boolean;
    }>;
  }> {
    return this.request<{
      files: Array<{
        name: string;
        path: string;
        size: number;
        is_directory: boolean;
      }>;
    }>(`/operations/list/${workspaceId}`);
  }
}

export const backendApi = new BackendApi();
export default BackendApi; 