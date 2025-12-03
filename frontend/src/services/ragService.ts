import api from './api';

export interface UploadedFile {
  id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  file_type: string;
  status: string;
  chunks_count: number;
  uploaded_at: string;
  processed_at?: string;
}

export interface SearchResult {
  text: string;
  score: number;
  metadata: Record<string, any>;
  file_id?: string;
  filename?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
}

export const ragService = {
  uploadFile: async (file: File): Promise<UploadedFile> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/v1/rag/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  searchDocuments: async (query: string, topK = 5): Promise<SearchResponse> => {
    const response = await api.post('/api/v1/rag/search', {
      query,
      top_k: topK,
    });
    return response.data;
  },

  listFiles: async (skip = 0, limit = 50): Promise<UploadedFile[]> => {
    const response = await api.get('/api/v1/rag/files', {
      params: { skip, limit },
    });
    return response.data;
  },

  getFile: async (fileId: string): Promise<UploadedFile> => {
    const response = await api.get(`/api/v1/rag/files/${fileId}`);
    return response.data;
  },

  deleteFile: async (fileId: string): Promise<void> => {
    await api.delete(`/api/v1/rag/files/${fileId}`);
  },

  getStats: async (): Promise<any> => {
    const response = await api.get('/api/v1/rag/stats');
    return response.data;
  },
};
